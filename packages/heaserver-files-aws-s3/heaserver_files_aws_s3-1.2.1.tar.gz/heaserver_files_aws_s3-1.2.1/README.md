# HEA Server AWS S3 Bucket Files Microservice
[Research Informatics Shared Resource](https://risr.hci.utah.edu), [Huntsman Cancer Institute](https://healthcare.utah.edu/huntsmancancerinstitute/),
Salt Lake City, UT

The HEA Server AWS S3 Bucket Files Microservice manages files in AWS S3 buckets.

## Version 1.2.1
* Correct issue where some users lost access to files because the user lacked permissions in AWS to simulate permissions. Instead, such users will appear to receive full permission for everything, which was the behavior prior to version 1.2.0. As before, AWS will still reject requests that users lack permission for.

## Version 1.2.0
* Present accurate bucket permissions.
* Install setuptools first during installation.

## Version 1.1.4
* Minor bug fixes.

## Version 1.1.3
* Made a file's unarchive restore duration required in the unarchive card.

## Version 1.1.2
* Fixed potential issue preventing the service from updating temporary credentials.

## Version 1.1.1
* Display type display name in properties card, and return the type display name from GET calls.

## Version 1.1.0
* Pass desktop object permissions back to clients.

## Version 1.0.8
* Changed presented bucket owner to system|aws.
* Omitted shares from the properties template.

## Version 1.0.7
* Added support for uploading files to storage tiers other than STANDARD.

## Version 1.0.6
* Prevent potential corruption when getting a file's content.

## Version 1.0.5
* Addressed issue where downloads start failing for all users if one user interrupts their download.

## Version 1.0.4
* Addressed potential failures to connect to other CORE Browser microservices.

## Version 1.0.3
* Addressed potential exception while unarchiving objects.
* Addressed issue preventing copying and moving unarchived files.

## Version 1.0.2
* Allow unarchived S3 objects to be downloaded.

## Version 1.0.1
* Define a default value for archive storage class.
* Improved performance.
* Respond with the correct status code when an object's storage class is incompatible with downloading.

## Version 1
Initial release.

## Runtime requirements
* Python 3.10 or 3.11

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
* A compatible heaserver-registry Docker image must be available.
* Run tests with the `pytest integrationtests` command from the project root directory.

### Trying out the APIs
This microservice has Swagger3/OpenAPI support so that you can quickly test the APIs in a web browser. Do the following:
* Install Docker, if it is not installed already.
* Have a heaserver-registry docker image in your Docker cache. You can generate one using the Dockerfile in the
  heaserver-registry project.
* Run the `run-swaggerui.py` file in your terminal. This file contains some test objects that are loaded into a MongoDB
  Docker container.
* Go to http://127.0.0.1:8080/docs in your web browser.

Once `run-swaggerui.py` is running, you can also access the APIs via `curl` or other tool. For example, in Windows
PowerShell, execute:
```
Invoke-RestMethod -Uri http://localhost:8080/awss3files/root/items -Method GET -Headers @{'accept' = 'application/json'}`
```
In MacOS or Linux, the equivalent command is:
```
curl -X GET http://localhost:8080/awss3files/root/items -H 'accept: application/json'
```

### Packaging and releasing this project
See the [RELEASING.md](RELEASING.md) file for details.
