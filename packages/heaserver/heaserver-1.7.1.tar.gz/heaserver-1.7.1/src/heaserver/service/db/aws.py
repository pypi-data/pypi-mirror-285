from abc import ABC, abstractmethod
from functools import partial
from aiohttp.web import Request
from aiohttp import ClientResponseError
import boto3
import botocore
from aiohttp import hdrs, web
from botocore.exceptions import ClientError, ParamValidationError
from mypy_boto3_iam import IAMClient
from mypy_boto3_s3 import S3Client, S3ServiceResource
from mypy_boto3_sts import STSClient
from mypy_boto3_account import AccountClient
from mypy_boto3_organizations import OrganizationsClient

from ..appproperty import HEA_DB
from .database import DatabaseContextManager, Database, MicroserviceDatabaseManager, get_credentials_from_volume
from .mongo import Mongo
from ..oidcclaimhdrs import SUB
from ..sources import AWS as AWS_SOURCE
from heaobject.root import DesktopObject, PermissionContext, Permission
from heaobject.aws import S3Object
from heaobject.bucket import AWSBucket
from heaobject.account import AWSAccount
from heaobject.keychain import AWSCredentials, Credentials
from heaobject.registry import Property
from heaobject.volume import AWSFileSystem
from heaobject.user import AWS_USER, CREDENTIALS_MANAGER_USER, NONE_USER
from heaobject.person import Person, AccessToken
from ..heaobjectsupport import type_to_resource_url
from .. import client
from yarl import URL
from typing import Optional, TypeVar, cast, overload, Literal, Generic
from configparser import ConfigParser
import asyncio
from threading import Lock
from contextlib import closing
from collections import defaultdict
from collections.abc import Callable, Sequence, AsyncGenerator
from copy import copy
from .awsaction import *
from cachetools import TTLCache
import logging

_boto3_client_lock = Lock()
_boto3_resource_lock = Lock()
_boto3_client_config = botocore.config.Config(max_pool_connections=25)

_permission_for = {
    S3_GET_OBJECT: Permission.VIEWER,
    S3_PUT_OBJECT: Permission.EDITOR,
    S3_DELETE_OBJECT: Permission.DELETER,
    S3_GET_OBJECT_TAGGING: Permission.VIEWER,
    S3_PUT_OBJECT_TAGGING: Permission.EDITOR,
    S3_LIST_BUCKET: Permission.VIEWER,
    S3_CREATE_BUCKET: Permission.EDITOR,
    S3_DELETE_BUCKET: Permission.DELETER,
    S3_GET_BUCKET_TAGGING: Permission.VIEWER,
    S3_PUT_BUCKET_TAGGING: Permission.EDITOR
}

class AWS(Database, ABC):
    """
    Connectivity to Amazon Web Services (AWS) for HEA microservices. Subclasses must call this constructor.
    """
    pass
    # async def compute_shares(self, obj: DesktopObject, context: AWSPermissionContext):
    #     return await obj.get_permissions_as_share(obj)


class S3(AWS):
    """
    Connectivity to AWS Simple Storage Service (S3) for HEA microservices.
    """
    # this is the buffer we give to refresh credentials in minutes on our end before they expire on aws
    MAX_EXPIRATION_LIMIT = 540
    MIN_EXPIRATION_LIMIT = 11
    MAX_DURATION_SECONDS = 43200
    MIN_DURATION_SECONDS = 900

    _S3Service = TypeVar('_S3Service')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__locks = defaultdict(asyncio.Lock)

    @property
    def file_system_type(self) -> type[AWSFileSystem]:
        return AWSFileSystem

    async def update_credentials(self, request: Request, credentials: AWSCredentials) -> None:
        """
        Obtains the keychain microservice's url from the registry and executes a PUT call to update the credentials
        object. It executes the PUT call as the system|awscredentialsmanager user.

        :param request: the HTTP request (required).
        :param credentials: the AWS credentials to update (required).
        :raises ValueError: if there was a problem accessing the registry service or the credentials service was not
        found.
        :raises ClientResponseError: if there was a problem making the PUT request.
        """
        if credentials.id is None:
            raise ValueError(f'credentials must have a non-None id attribute')
        resource_url = await type_to_resource_url(request, Credentials)
        headers = {SUB: CREDENTIALS_MANAGER_USER}
        try:
            await client.put(app=request.app, url=URL(resource_url) / credentials.id, data=credentials,
                            headers=headers)
        except ClientResponseError as e:
            raise ValueError(f'Updating credentials failed: {str(e)}') from e

    async def get_property(self, app: web.Application, name: str) -> Optional[Property]:
        """
        This is a wrapper function to be extended by tests
        Gets the Property with the given name from the HEA registry service.

        :param app: the aiohttp app.
        :param name: the property's name.
        :return: a Property instance or None (if not found).
        """
        return await client.get_property(app=app, name=name)

    @overload
    async def get_client(self, request: Request, service_name: Literal['s3'], volume_id: str | None = None,
                         credentials: AWSCredentials | None = None) -> S3Client:
        ...

    @overload
    async def get_client(self, request: Request, service_name: Literal['iam'],
                         volume_id: str | None = None,
                         credentials: AWSCredentials | None = None) -> IAMClient:
        ...

    @overload
    async def get_client(self, request: Request, service_name: Literal['sts'], volume_id: str | None = None,
                         credentials: AWSCredentials | None = None) -> STSClient:
        ...

    @overload
    async def get_client(self, request: Request, service_name: Literal['account'], volume_id: str | None = None,
                         credentials: AWSCredentials | None = None) -> AccountClient:
        ...

    @overload
    async def get_client(self, request: Request, service_name: Literal['organizations'], volume_id: str | None = None,
                         credentials: AWSCredentials | None = None) -> OrganizationsClient:
        ...

    async def get_client(self, request: Request, service_name: str, volume_id: str | None = None,
                         credentials: AWSCredentials | None = None) -> S3Client | IAMClient | STSClient | AccountClient | OrganizationsClient:
        """
        Gets an AWS service client.  If the volume has no credentials, it uses the boto3 library to try and find them.
        This method is not designed to be overridden.

        :param request: the HTTP request (required).
        :param service_name: AWS service name (required).
        :param volume_id: the id string of a volume (required).
        :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
        was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
        application-level property.
        :raise ValueError: if there is no volume with the provided volume id, the volume's file system does not exist,
        the volume's credentials were not found, or a necessary service is not registered.

        TODO: need a separate exception thrown for when a service is not registered (so that the server can respond with a 500 error).
        TODO: need to lock around client creation because it's not threadsafe, manifested by sporadic KeyError: 'endpoint_resolver'.
        """
        if credentials is None:
            credentials = await self.get_credentials_from_volume(request, volume_id)
        return await self.__get_resource_or_client(request, service_name, create_client, credentials)

    async def get_resource(self, request: Request, service_name: str, volume_id: str | None = None,
                           credentials: AWSCredentials | None = None) -> S3ServiceResource:
        """
        Gets an AWS resource. If the volume has no credentials, it uses the boto3 library to try and find them. This
        method is not designed to be overridden.

        :param request: the HTTP request (required).
        :param service_name: AWS service name (required).
        :param volume_id: the id string of a volume (required).
        :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
        was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
        application-level property.
        :raise ValueError: if there is no volume with the provided volume id, the volume's file system does not exist,
        the volume's credentials were not found, or a necessary service is not registered.

        TODO: need to lock around resource creation because it's not threadsafe, manifested by sporadic KeyError: 'endpoint_resolver'.
        """
        if credentials is None:
            credentials = await self.get_credentials_from_volume(request, volume_id)
        return await self.__get_resource_or_client(request, service_name, create_resource, credentials)

    async def has_account(self, request: Request, volume_id: str) -> bool:
        """
        Return whether the current user can access the AWS accounts associated with the provided volume_id.

        :param request: the HTTP request object (required).
        :param volume_id: the volume id (required).
        :return: True or False.
        """
        return await self.get_account(request, volume_id) is not None

    async def get_account(self, request: Request, volume_id: str) -> AWSAccount | None:
        """
        Gets the current user's AWS account associated with the provided volume_id.

        :param request: the HTTP request object (required).
        :param volume_id: the volume id (required).
        :return: the AWS account, or None if not found.
        """
        return await self._get_account(request, volume_id)

    async def get_accounts(self, request: Request, volume_ids: Sequence[str]) -> AsyncGenerator[
        tuple[AWSAccount, str], None]:
        """
        Gets the AWS accounts associated with the provided volume ids.

        :param request: the HTTP request object (required).
        :param volume_ids: the volume ids (required).
        :return: an async generator of tuples containing the AWS accounts and corresponding volume ids.
        """
        logger = logging.getLogger(__name__)

        async def execute(volume_id: str) -> tuple[AWSAccount, str]:
            return await self.get_account(request, volume_id), volume_id

        for i, account in enumerate(await asyncio.gather(*(execute(volume_id) for volume_id in volume_ids),
                                                                return_exceptions=True)):
            if not isinstance(account, tuple):
                if isinstance(account, ValueError):
                    logger.error('Error getting account for volume %s', volume_ids[i], exc_info=account)
                    continue
                else:
                    raise account
            yield account

    async def generate_cloud_credentials(self, request: Request, arn: str, session_name: str) -> AWSCredentials | None:
        """
        Create temporary credentials and return a newly created AWSCredentials object.

        :param session_name:
        :param request: the HTTP request (required).
        :param arn: The aws role arn that to be assumed
        :returns an AWSCredentials object with the generated credentials, or None if the user doesn't have the provided
        role.
        :raises ValueError: if an error occurs generating cloud credentials other than the user lacking permission.
        """
        return await _generate_cloud_credentials(request=request, arn=arn, session_name=session_name)

    async def get_credentials_from_volume(self, request: web.Request, volume_id: str) -> AWSCredentials | None:
        """
        Gets the volume's credentials.

        :param request: the HTTP request (required).
        :param volume_id: the volume id (required).
        :return a Credentials object, or None if no credentials were found.
        :raises ValueError: if no volume with that id exists
        """
        return await get_credentials_from_volume(request, volume_id, credential_type=AWSCredentials)

    @staticmethod
    async def _get_basic_account_info(sts_client: STSClient) -> AWSAccount:
        loop = asyncio.get_running_loop()
        identity = await loop.run_in_executor(None, sts_client.get_caller_identity)
        logger = logging.getLogger(__name__)
        logger.debug('Caller identity: %s', identity)
        # user_future = loop.run_in_executor(None, iam_client.get_user)
        # await asyncio.wait([identity_future])  # , user_future])
        aid = identity.get('Account')
        # aws_object_dict['alias'] = next(iam_client.list_account_aliases()['AccountAliases'], None)  # Only exists for IAM accounts.
        # user = user_future.result()['User']
        # aws_object_dict['account_name'] = user.get('UserName')  # Only exists for IAM accounts.
        account = AWSAccount()
        account.id = aid
        account.name = aid
        account.display_name = aid
        account.owner = AWS_USER
        account.source = AWS_SOURCE
        account.source_detail = AWS_SOURCE
        account.type_display_name
        account.file_system_type = AWSFileSystem.get_type_name()
        account.credential_type_name = AWSCredentials.get_type_name()
        return account

    async def _get_account(self, request: Request, volume_id: str) -> AWSAccount:
        logger = logging.getLogger(__name__)
        loop = asyncio.get_running_loop()
        credentials = await self.get_credentials_from_volume(request, volume_id)
        logger.debug('Got credentials %s for volume %s', credentials, volume_id)

        async with STSClientContext(request, credentials=credentials) as sts_client:
            account = await S3._get_basic_account_info(sts_client)
            aid = account.id

        async def populate_contact_info():
            try:
                async with AccountClientContext(request, credentials=credentials) as account_client:
                    contact_info = await loop.run_in_executor(None, partial(account_client.get_contact_information, AccountId=aid))
                    account.full_name = contact_info.get('FullName')
                    account.phone_number = contact_info.get('PhoneNumber')
            except ClientError as e:
                code = e.response['Error']['Code']
                if code != 'AccessDeniedException':
                    logger.exception('Client error %s', code)
                    raise e
                logger.debug('Account %s is not authorized to access contact information', aid, exc_info=True)

        async def populate_organization_info():
            try:
                async with OrganizationsClientContext(request, credentials=credentials) as org_client:
                    account_info = await loop.run_in_executor(None, partial(org_client.describe_account, AccountId=aid))
                    account_info_ = account_info['Account']
                    account.name = account_info_.get('Name')
                    account.email_address = account_info_.get('Email')
            except ParamValidationError:
                logger.debug('Account %s is not part of an organization', aid, exc_info=True)
            except ClientError as e:
                code = e.response['Error']['Code']
                if code != 'AccessDeniedException':
                    logger.exception('Client error %s', code)
                    raise e
                logger.debug('Account %s is not authorized to access organization-level account information',
                            aid, exc_info=True)

        await asyncio.gather(populate_contact_info(), populate_organization_info())

        # account.created = user['CreateDate']
        # FIXME this info coming from Alternate Contact(below) gets 'permission denied' with IAMUser even with admin level access
        # not sure if only root account user can access. This is useful info need to investigate different strategy
        # alt_contact_resp = account_client.get_alternate_contact(AccountId=account.id, AlternateContactType='BILLING' )
        # alt_contact =  alt_contact_resp.get("AlternateContact ", None)
        # if alt_contact:
        # account.full_name = alt_contact.get("Name", None)

        return account

    async def __get_resource_or_client(self, request: Request, service_name: str,
                                       creator: Callable[[str, str | None, str | None, str | None,
                                                          str | None], _S3Service],
                                       credentials: AWSCredentials | None) -> _S3Service:
        """
        Gets an S3 resource or client.

        :param request: the HTTP request (required).
        :param service_name: the name of the S3 service (required).
        :param creator: the function for creating the resource or client (create_resource or create_client).
        :param credentials: the AWSCredentials object, or None to let boto3 find the credentials.

        :raises ValueError: if updating temporary credentials failed.
        """
        logger = logging.getLogger(__name__)
        logger.debug("credentials retrieved from database checking if expired: %r", credentials)
        loop = asyncio.get_running_loop()
        if not credentials:  # delegate to boto3 to find the credentials
            return await loop.run_in_executor(None, creator, service_name)
        elif credentials.temporary:
            return await self.__get_temporary_credentials(request=request,
                                                            credentials=credentials,
                                                            creator=creator,
                                                            service_name=service_name)
        else:  # for permanent credentials
            return await loop.run_in_executor(None, partial(creator, service_name,
                                                            region_name=credentials.where,
                                                            aws_access_key_id=credentials.account,
                                                            aws_secret_access_key=credentials.password))


    async def __get_temporary_credentials(self, request: web.Request, credentials: AWSCredentials,
                                          creator: Callable[
                                              [str, str | None, str | None, str | None, str | None], _S3Service],
                                          service_name: str) -> _S3Service:
        """
            Gets temporary credentials and returns the authorized client. In order to do that it
            gets the previous credential's role and then assumes it.

            :param request: the aiohttp request
            :param credentials: the aws credentials last saved
            :param aws_source: must be either boto3.client or boto3.resource.
            :param service_name: The type of client to return
            :return: the boto3 client provided with credentials
            :raise ValueError if no previously saved credentials it raises ValueError
        """
        logger = logging.getLogger(__name__)
        assert credentials.role is not None, 'credentials must have a non-None role attribute'
        loop = asyncio.get_running_loop()
        sub = request.headers.get(SUB, None)

        async with self.__locks[credentials.id]:
            logger.debug("checking if credentials need to be refreshed, right before")
            if credentials.has_expired(S3.MAX_EXPIRATION_LIMIT if sub != CREDENTIALS_MANAGER_USER else S3.MIN_EXPIRATION_LIMIT):
                logger.debug("credentials need to be refreshed")
                cloud_creds = await self.generate_cloud_credentials(request, credentials.role, credentials.id)
                if not cloud_creds:
                    raise ValueError(f'Could not generate cloud credentials with role {credentials.role}')
                logger.debug("Credentials successfully obtained from cloud: %r", cloud_creds)
                credentials.account = cloud_creds.account
                credentials.password = cloud_creds.password
                credentials.session_token = cloud_creds.session_token
                credentials.expiration = cloud_creds.expiration
                await self.update_credentials(request=request, credentials=credentials)
                logger.debug("Credentials updated in the database")
            return await loop.run_in_executor(None, partial(creator,
                                                            service_name,
                                                            region_name=credentials.where,
                                                            aws_access_key_id=credentials.account,
                                                            aws_secret_access_key=credentials.password,
                                                            aws_session_token=credentials.session_token))


class S3WithMongo(S3, Mongo):
    def __init__(self, config: Optional[ConfigParser], **kwargs):
        super().__init__(config, **kwargs)


class S3Manager(MicroserviceDatabaseManager):
    """
    Database manager for mock Amazon Web Services S3 buckets. It will not make any calls to actual S3 buckets. This
    class is not designed to be subclassed.
    """

    def get_database(self) -> S3:
        return S3(self.config)

    @classmethod
    def database_types(self) -> list[str]:
        return ['system|awss3']


class S3WithMongoManager(S3Manager):

    def get_database(self) -> S3:
        return S3WithMongo(self.config)


class S3ClientContext(DatabaseContextManager[S3Client]):  # Go into db package?
    """
    Provides an S3 client.
    """

    def __init__(self, request: web.Request, volume_id: str | None = None, credentials: AWSCredentials | None = None):
        super().__init__(request, volume_id, credentials)

    async def connection(self) -> S3Client:
        return await cast(S3, self.request.app[HEA_DB]).get_client(self.request, 's3', self.volume_id, self.credentials)


class IAMClientContext(DatabaseContextManager[IAMClient]):  # Go into db package?
    """
    Provides an STS client.
    """

    def __init__(self, request: web.Request, volume_id: str | None = None, credentials: AWSCredentials | None = None):
        super().__init__(request, volume_id, credentials)

    async def connection(self) -> IAMClient:
        return await cast(S3, self.request.app[HEA_DB]).get_client(self.request, 'iam', self.volume_id, self.credentials)


class STSClientContext(DatabaseContextManager[STSClient]):  # Go into db package?
    """
    Provides an STS client.
    """

    def __init__(self, request: web.Request, volume_id: str | None = None, credentials: AWSCredentials | None = None):
        super().__init__(request, volume_id, credentials)

    async def connection(self) -> STSClient:
        return await cast(S3, self.request.app[HEA_DB]).get_client(self.request, 'sts', self.volume_id, self.credentials)


class AccountClientContext(DatabaseContextManager[AccountClient]):
    """
    Provides an Account client.
    """

    def __init__(self, request: web.Request, volume_id: str | None = None, credentials: AWSCredentials | None = None):
        super().__init__(request, volume_id, credentials)

    async def connection(self) -> AccountClient:
        return await cast(S3, self.request.app[HEA_DB]).get_client(self.request, 'account', self.volume_id, self.credentials)


class OrganizationsClientContext(DatabaseContextManager[OrganizationsClient]):
    """
    Provides an Organizations client.
    """

    def __init__(self, request: web.Request, volume_id: str | None = None, credentials: AWSCredentials | None = None):
        super().__init__(request, volume_id, credentials)

    async def connection(self) -> OrganizationsClient:
        return await cast(S3, self.request.app[HEA_DB]).get_client(self.request, 'organizations', self.volume_id, self.credentials)


@overload
def create_client(service_name: Literal['s3'],
                  region_name: str | None = None,
                  aws_access_key_id: str | None = None,
                  aws_secret_access_key: str | None = None,
                  aws_session_token: str | None = None) -> S3Client:
    ...


@overload
def create_client(service_name: Literal['sts'],
                  region_name: str | None = None,
                  aws_access_key_id: str | None = None,
                  aws_secret_access_key: str | None = None,
                  aws_session_token: str | None = None) -> STSClient:
    ...


@overload
def create_client(service_name: Literal['account'],
                  region_name: str | None = None,
                  aws_access_key_id: str | None = None,
                  aws_secret_access_key: str | None = None,
                  aws_session_token: str | None = None) -> AccountClient:
    ...


@overload
def create_client(service_name: Literal['organizations'],
                  region_name: str | None = None,
                  aws_access_key_id: str | None = None,
                  aws_secret_access_key: str | None = None,
                  aws_session_token: str | None = None) -> OrganizationsClient:
    ...


def create_client(service_name: Literal['s3', 'iam', 'sts', 'account', 'organizations'],
                  region_name: str | None = None,
                  aws_access_key_id: str | None = None,
                  aws_secret_access_key: str | None = None,
                  aws_session_token: str | None = None) -> S3Client | IAMClient | STSClient | AccountClient | OrganizationsClient:
    """
    Thread-safe boto client creation. Once created, clients are generally
    thread-safe.

    :raises ValueError: if an error occurred getting the S3 client.
    """
    with _boto3_client_lock:
        return boto3.client(service_name,
                            region_name=region_name,
                            aws_access_key_id=aws_access_key_id,
                            aws_secret_access_key=aws_secret_access_key,
                            aws_session_token=aws_session_token,
                            config=_boto3_client_config)


def create_resource(service_name: Literal['s3'],
                    region_name: str | None = None,
                    aws_access_key_id: str | None = None,
                    aws_secret_access_key: str | None = None,
                    aws_session_token: str | None = None) -> S3ServiceResource:
    """
    Thread-safe boto resource creation. Resources are generally NOT
    thread-safe!

    :raises ValueError: if an error occurred getting the S3 resource.
    """
    with _boto3_resource_lock:
        return boto3.resource(service_name,
                              region_name=region_name,
                              aws_access_key_id=aws_access_key_id,
                              aws_secret_access_key=aws_secret_access_key,
                              aws_session_token=aws_session_token,
                              config=_boto3_client_config)


PC_DesktopObject = TypeVar('PC_DesktopObject', S3Object, AWSBucket, AWSAccount)

class AWSPermissionContext(PermissionContext, ABC, Generic[PC_DesktopObject]):
    """
    Helper class for desktop objects' permissions-related methods that require external information, such as the
    current user.
    """
    def __init__(self, request: Request, volume_id: str, actions: Sequence[str], **kwargs):
        """
        Accepts an aiohttp Application object, a desktop object type, and any query parameters. Any additional keyword
        arguments will be passed onto the next class in the method resolution order.
        """
        if request is None:
            raise ValueError('request is required')
        sub = request.headers.get(SUB, NONE_USER)
        super().__init__(sub=sub, **kwargs)
        self.__request = request
        self.__volume_id = str(volume_id)
        self.__actions = copy(actions)
        self.__cache = TTLCache(maxsize=128, ttl=30)
        self.__credentials: Credentials | None = None

    @property
    def request(self) -> Request:
        return self.__request

    @property
    def volume_id(self) -> str:
        return self.__volume_id

    async def get_permissions(self, obj: PC_DesktopObject) -> list[Permission]:
        """
        Gets the user's permissions for a desktop object. This default implementation delegates to the object's
        _default_get_permissions() method.

        :param obj: the desktop object (required).
        :return: a list of Permissions, or the empty list if there is none.
        """
        cached_value = self.__cache.get(obj.instance_id)
        if cached_value is not None:
            return copy(cached_value)
        else:
            if not await is_account_owner(request=self.__request, volume_id=self.__volume_id):
                perms = await self._simulate_perms(obj, self.__actions)
            else:
                perms = [Permission.COOWNER]
            self.__cache[obj.instance_id] = perms
            return copy(perms)

    async def _simulate_perms(self, obj: DesktopObject, actions: Sequence[str]) -> list[Permission]:
        logger = logging.getLogger(__name__)
        if self.__credentials is None:
            self.__credentials = cast(Credentials,
                        await cast(S3, self.__request.app[HEA_DB]).get_credentials_from_volume(self.__request, self.__volume_id))
        perms: list[Permission] = []
        async with IAMClientContext(request=self.__request, volume_id=self.__volume_id) as iam_client:
            loop = asyncio.get_running_loop()
            response_ = await loop.run_in_executor(None, partial(iam_client.simulate_principal_policy, PolicySourceArn=self.__credentials.role,
                                                                    ActionNames=actions,
                                                                    CallerArn=self._caller_arn(obj)))
            logger.debug('Response for checking %s: %s', actions, response_)
            for results in response_['EvaluationResults']:
                if results['EvalDecision'] == 'allowed':
                    if perm := _permission_for.get(results.get('EvalActionName')):
                        perms.append(perm)
        return perms

    @abstractmethod
    def _caller_arn(self, obj: PC_DesktopObject):
        pass

class S3ObjectPermissionContext(AWSPermissionContext[S3Object]):
    def __init__(self, request: Request, volume_id: str, **kwargs):
        actions = [S3_GET_OBJECT, S3_PUT_OBJECT, S3_DELETE_OBJECT]
        super().__init__(request=request, volume_id=volume_id, actions=actions, **kwargs)

    async def get_attribute_permissions(self, obj: DesktopObject, attr: str) -> list[Permission]:
        if attr == 'tags' and not await is_account_owner(request=self.request, volume_id=self.volume_id):
            return await self._simulate_perms(obj, [S3_GET_OBJECT_TAGGING, S3_PUT_OBJECT_TAGGING])
        else:
            return await super().get_attribute_permissions(obj, attr)

    def _caller_arn(self, obj: S3Object):
        return f'arn:aws:s3:::{obj.bucket_id}/{obj.key}'


async def is_account_owner(request: Request, volume_id: str) -> bool:
    return not await _user_has_assumed_role(request, volume_id)


async def _generate_cloud_credentials(request: Request, arn: str, session_name:str) -> AWSCredentials | None:
    """
    Create temporary credentials and return a newly created AWSCredentials object.

    :param request: the HTTP request (required).
    :param arn: The aws role arn that to be assumed (required).
    :param session_name: The session name that can be associated uniquely with the user (required).
    :returns an AWSCredentials object with the generated credentials, or None if the user doesn't have the provided
    role.
    :raises ValueError: if an error occurs generating cloud credentials other than the user lacking permission.
    """
    logger = logging.getLogger(__name__)
    sub = request.headers.get(SUB, None)
    logger.debug("In generate_credentials sub is %s" % sub)
    if sub is None:
        raise ValueError('OIDC SUB header is required')
    if not arn:
        raise ValueError('Cannot get credentials arn which is required')
    auth = request.headers.get(hdrs.AUTHORIZATION, '')
    auth_token = auth.split(' ')

    logger.debug('Getting credentials for user %s with role %s...', sub, arn)
    try:
        if sub == CREDENTIALS_MANAGER_USER:
            resource_url = await type_to_resource_url(request, Person)
            logger.debug("url for token for people: %s" % (URL(resource_url) / 'internal' / 'token'))
            token_obj = await client.get(app=request.app, type_or_obj=AccessToken,
                                         url=URL(resource_url) / 'internal' / 'token',
                                         headers=request.headers)

            auth_token = [token_obj.auth_scheme, token_obj.id]

        if len(auth_token) != 2:
            raise ValueError("Bearer Token is required in header")

        logger.debug('User %s has role %s', sub, arn)
        loop = asyncio.get_running_loop()
        sts_client_call = partial(boto3.client, 'sts', config=_boto3_client_config)
        with closing(await loop.run_in_executor(None, sts_client_call)) as sts_client:
            assumed_role_object = await loop.run_in_executor(None, partial(sts_client.assume_role_with_web_identity,
                                                                            WebIdentityToken=auth_token[1],
                                                                            RoleArn=arn,
                                                                            RoleSessionName=session_name,
                                                                            DurationSeconds=S3.MIN_DURATION_SECONDS if sub == CREDENTIALS_MANAGER_USER else S3.MAX_DURATION_SECONDS))
    except ClientError:
        logger.exception('User %s does not have role %s', sub, arn)
        return None
    except ClientResponseError as cre:
        logger.debug("Token can not be obtained: %s" % cre)
        return None
    except Exception as e:
        return None
    creds_dict = assumed_role_object.get('Credentials')
    if not creds_dict:
        return None
    creds = AWSCredentials()
    creds.account = creds_dict['AccessKeyId']
    creds.password = creds_dict['SecretAccessKey']
    creds.session_token = creds_dict['SessionToken']
    creds.role = arn
    creds.temporary = True
    creds.expiration = assumed_role_object.get('Credentials')['Expiration']


    return creds

async def _user_has_assumed_role(request: Request, volume_id: str) -> bool:
    logger = logging.getLogger(__name__)
    async with STSClientContext(request=request, volume_id=volume_id) as sts_client:
        caller_identity_resp = sts_client.get_caller_identity()
        logger.debug('caller identity: %s', caller_identity_resp)
        caller_identity_arn = caller_identity_resp['Arn']
        caller_identity_arn_split = caller_identity_arn.split(':')
        return caller_identity_arn_split[5].startswith('assumed-role')
