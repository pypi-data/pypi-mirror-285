# Overview

This is a generic utility library full of helper functions relating to cherrypy webservice routines.
Included are handlers for:

-   authentication (authentication.py)
-   sqlalchemy with cherrypy (cherrypy_sqlalchemy_utils.py & database.py)
-   json parsing and constructing orm entities from json (json_utils.py)
-   timestamp (ISO and posix epoch) parsing (timestamp.py)
-   url construction and parsing from parts (similar to os.path.join) (url_utils.py)
-   ldap login utilities (login/ldap_auth.py & login/models.py)

## Usage

To use this package in your project as a dependency (using pipenv), you can add it as a package with the following definition:

    [packages]
    cherrypy_utils = { git = "${USERNAME}:${PASSWORD}@git.mindmodeling.org:ian.davis/CherrypyUtils.git" }

You will need to export appropriate environment variables for USERNAME and PASSWORD.
See this page for more info: https://pipenv.pypa.io/en/latest/advanced/#injecting-credentials-into-pipfiles-via-environment-variables
Alternatively, if you save your username/password in git config, pipenv will intelligently use that if you provide the http link instead:

    [packages]
    cherrypy_utils = { git = "https://git.mindmodeling.org/ian.davis/CherrypyUtils.git" }

## Development

This package is developed using Pipenv for package management, which makes dealing with pip packages easier.
Check out more here: https://pipenv.pypa.io/en/latest/install/#using-installed-packages

It also uses pyenv to manage multiple different installed versions of python.
Currently, this package targets python 3.6.8.

The package uses the black formatter and enforces a strict formatting policy, automatic formatting on save is required.

## GCP Deployment

https://packaging.python.org/en/latest/tutorials/packaging-projects/
https://cloud.google.com/artifact-registry/docs/python/authentication#keyring
https://cloud.google.com/artifact-registry/docs/python/manage-packages

```
gcloud artifacts print-settings python --project=afrl-il2-sbx-rh-mm-lab-i9sv --repository=online-experiment-python-utilities --location=us-central1
```

Setup requires pip packages:

-   `hatchling`
-   `keyring`
-   `keyrings.google-artifactregistry-auth`

Build and deploy using deploy_package_gcp.py
Documentation on hatch: https://hatch.pypa.io/dev/

```
pip install keyring
pip install keyrings.google-artifactregistry-auth
keyring --list-backends
gcloud artifacts print-settings python --project=afrl-il2-sbx-rh-mm-lab-i9sv --repository=online-experiment-python-utilities --location=us-central1
gcloud auth login
```
