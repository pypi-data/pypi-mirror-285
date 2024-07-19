# iccicd

This project is a collection of utilities for managing CI/CD pipelines at ICHEC.

It provides opinionated interfaces to encourage standarization of our project structures and workflows.

# Install

The package is available from PyPI:

```sh
pip install iccicd
```

# Features #

## Deploy a Package to a Repository

From the package's top-level directory:

```sh
iccicd deploy --token $REPO_TOKEN
```

As an example, for a Python project this might be the PyPI repository's token.

## Set a Package's Version Number

From the package's top-level directory:

```sh
iccicd set_version $VERSION
```

## Increment a Repository's Tag ##

From the repository's top-level directory, and on the branch the tag will be dervied from:

``` sh
iccicd increment_tag --field patch
```

Here `semver` tag versioning is assumed with a `major.minor.patch` scheme. Note: in a CI/CD pipeline some more input options are needed to initialize the git repo for pushing the tag to. You can use the `--help` flag for more details.


# Licensing #

This project is licensed under the GPLv3+. See the accompanying `LICENSE.txt` file for details.

