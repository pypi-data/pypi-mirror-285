# HEA Server Framework
[Research Informatics Shared Resource](https://risr.hci.utah.edu), [Huntsman Cancer Institute](https://healthcare.utah.edu/huntsmancancerinstitute/), Salt Lake City, UT

The HEA Server Framework contains shared code for creating HEA microservices.

## Version 1.7.0
* requirements_dev.txt now sets a minimum version of setuptools to address a security vulnerability. Also updated to a newer version of build.
* Implemented attribute-level permissions.
* Addressed potential performance issue with unarchiving large numbers of AWS S3 objects.
* Addressed potential crash when the server loses its connection to a client while downloading an object's contents, and increased logging during downloads.
* Mapped AWS access policies to HEA permissions so that HEA may present accurate permissions for AWS accounts, S3 buckets, and S3 objects.

## Version 1.6.3
* Upgrading heaobject dependency to get bug fixes.

## Version 1.6.2
* Added ability to toggle aws key duration depending on if system credential manager or any other user.
* Background tasks now pass the aiohttp app object as a parameter of the coroutine added to the queue.
* Added the scheduled_cleanup_ctx manager for scheduling reoccurring tasks with a delay optionally.
* Prevent the id field from appearing in mongodb when a new desktop object is inserted.


## Version 1.6.0
* Improved docstrings.
* New heaobject dependency.
* Removed account_type_names parameters from heaserver.service.db.database.get_volumes and heaserver.service.db.database.Database.get_volumes.
* New heaserver.service.util.now() function.
* Removed file system-related parameters from heaserver.service.heaobjectsupport functions (type_to_resource_url, get_dict, get, get_all, get_component, get_resource_url).
* heaserver.service.client: Made a type passed into type_or_obj not used to create the object instance; new get_all_list() function.
* Use heaobject.util.now() instead of datetime.now() to get the current datetime with a timezone.
* Don't allow creating a new desktop object in MongoDB if the current user and the owner of the object are not the same.
* Set the created and modified attributes of desktop objects in heaserver.service.db.mongo.
* Populate new AWSAccount attributes.

## Version 1.5.3
* When updating AWS temporary credentials, generate new headers rather than pass the headers from the HTTP request,
possibly resulting in a Content-Length header that is shorter than the request body.
* Make heaserver.service.db.aws.get_credentials raise the right exception.

## Version 1.5.2
* Fixed TypeError regression in the heaserver.service.client module.

## Version 1.5.1
* Ensure the Content-Type header is set to application/json in heaserver.service.client put and post calls.

## Version 1.5.0
* Added attribute-level permissions.
* Temporarily restored the role check that was removed in version 1.4.1 in case an AWS credentials object with overly
permissive permissions is altered.

## Version 1.4.2
* Synchronize around getting temporary credentials.

## Version 1.4.1
* Increased the boto3 max connection pool size from the default value (10) to 25.
* Fixed a connection leak in DatabaseContextManager, and fixed the documentation for the connection() method.
* Updated heaobject dependency.
* Removed an unnecessary role check.

## Version 1.4.0
* Added type_display_name attribute to all HEA objects.

## Version 1.3.0
* Performance improvement getting accounts.
* heaserver.service.db.database.DatabaseContextManagers now allow initializing with either a volume id or a Credentials
object.

## Version 1.2.0
* get_volumes() in the database module and Database class can now filter by account ids.
* New heaobject dependency: new heaobject.root.AbstractAssociation base class and heaobject.account.AccountAssociation
implementation, and heaobject.organization.Organization class now has an accounts attribute using AccountAssociation.

## Version 1.1.3
* Fixed permissions setting in mongoservicelib.aggregate().

## Version 1.1.2
* Added resolved permissions for desktop objects in WeSTL and Collection+JSON docs.

## Version 1.1.1
* No longer errors out when accessing account information that the user is unauthorized to see.

## Version 1.1.0
* AWS account objects are now populated with more information.
* New heaobject with new APIs.

## Version 1.0.8
* Performance improvements converting to/from a HEAObject and a dictionary.

## Version 1.0.7
* Prevent a condition where zip file generation resulted in a truncated zip file.

## Version 1.0.6
* Prevent hang while getting HEA object content when the client connection goes away.

## Version 1.0.5
* Backed out boto connections issue.

## Version 1.0.4
* Don't crash when getting the user's AWS account list includes an account that doesn't exist.
* Fixed exceptions while unarchiving objects.
* Better error messaging when trying to move archived files.
* Allow copying and moving unarchived files.

## Version 1.0.3
* Added heaserver.service.response.status_generic_error() function.
* Made heaserver.service.db.awsservicelib.handle_client_error always return an HTTP response object that can be raised
  as an exception.

## Version 1.0.2
* Improved performance of heaserver.service.activity.DesktopObjectActionLifecycle context manager.
* Removed unused properties from heaserver.service.activity.DesktopObjectActionLifecycle.
* Implemented input validation for heaserver.service.db.awsservicelib.archive_object().

## Version 1.0.1
* Fixed caching bug affecting mongodb paginated queries.
* Fixed passing one desktop object dict to heaserver.service.wstl.RuntimeWeSTLDocumentBuilder().

## Version 1
Initial release.

## Runtime requirements
* Python 3.10 or 3.11.

## Development environment

### Build requirements
* Any development environment is fine.
* On Windows, you also will need:
    * Build Tools for Visual Studio 2019, found at https://visualstudio.microsoft.com/downloads/. Select the C++ tools.
    * git, found at https://git-scm.com/download/win.
* On Mac, Xcode or the command line developer tools is required, found in the Apple Store app.
* Python 3.10 or 3.11: Download and install Python 3.10 from https://www.python.org, and select the options to install
for all users and add Python to your environment variables. The install for all users option will help keep you from
accidentally installing packages into your Python installation's site-packages directory instead of to your virtualenv
environment, described below.
* Create a virtualenv environment using the `python -m venv <venv_directory>` command, substituting `<venv_directory>`
with the directory name of your virtual environment. Run `source <venv_directory>/bin/activate` (or `<venv_directory>/Scripts/activate` on Windows) to activate the virtual
environment. You will need to activate the virtualenv every time before starting work, or your IDE may be able to do
this for you automatically. **Note that PyCharm will do this for you, but you have to create a new Terminal panel
after you newly configure a project with your virtualenv.**
* From the project's root directory, and using the activated virtualenv, run `pip install wheel` followed by
  `pip install -r requirements_dev.txt`. **Do NOT run `python setup.py develop`. It will break your environment.**

### Running tests
Run tests with the `pytest` command from the project root directory. To improve performance, run tests in multiple
processes with `pytest -n auto`.

### Running integration tests
* Install Docker
* On Windows, install pywin32 version >= 223 from https://github.com/mhammond/pywin32/releases. In your venv, make sure that
`include-system-site-packages` is set to `true`.

### Packaging and releasing this project
See the [RELEASING.md](RELEASING.md) file for details.
