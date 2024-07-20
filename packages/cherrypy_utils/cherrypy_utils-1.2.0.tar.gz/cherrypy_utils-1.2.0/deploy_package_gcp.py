### This script assumes you have followed the necessary steps to configure the GCP python repository as described at these links:
### https://cloud.google.com/artifact-registry/docs/python/manage-packages
### https://cloud.google.com/artifact-registry/docs/python/authentication#sa-key
### It also uses this python documentation to determine how building should be done:
### https://packaging.python.org/en/latest/tutorials/packaging-projects/
import argparse
import os
import subprocess

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        "Utility to build the package and deploy to GCP pypi repository"
    )
    parser.add_argument(
        "--release_type", help="The release type, major, minor, patch", default="patch"
    )
    parser.add_argument(
        "--repository",
        help="The name of the pypi repository",
        default="online-experiment-python-utilities",
    )
    parser.add_argument(
        "--region", help="The region location of the repository", default="us-central1"
    )
    parser.add_argument(
        "--project",
        help="The GCP Project the repository belongs to",
        default="afrl-il4-sbx-rhmindmodel-dk29",
    )

    args = parser.parse_args()

    os.system("rm -rf dist/")

    exit_code = os.system("hatch version {0}".format(args.release_type))

    if exit_code:
        raise RuntimeError("hatch version update failed!")

    project_name = (
        str(
            subprocess.run(
                "hatch project metadata name", shell=True, stdout=subprocess.PIPE
            ).stdout
        )
        .strip()
        .replace("-", "_")
    )
    version_number = str(
        subprocess.run("hatch version", shell=True, stdout=subprocess.PIPE).stdout
    ).strip()

    # We temporarily move your pip config file because we need to disable the GCP pip repository otherwise hatch will never complete.
    # For some reason, hatch doesn't support GCP authentication using keyring to query the pip repository, so it never finishes when trying to resolve dependencies.
    os.system("mv ~/.pip/pip.conf ~/.pip/pip.conf.disabled")

    exit_code = os.system("hatch build")

    if exit_code:
        os.system("mv ~/.pip/pip.conf.disabled ~/.pip/pip.conf")
        raise RuntimeError("hatch build failed!")

    # Restore the pip config now that we've built successfully.
    os.system("mv ~/.pip/pip.conf.disabled ~/.pip/pip.conf")

    command_string = "twine upload --repository-url https://{0}-python.pkg.dev/{1}/{2}/ dist/* --verbose".format(
        args.region, args.project, args.repository
    )
    exit_code = os.system(command_string)

    if exit_code:
        raise RuntimeError("twine upload failed!")
