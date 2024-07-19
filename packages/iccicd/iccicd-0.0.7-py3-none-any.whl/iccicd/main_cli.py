#!/usr/bin/env python3

import os
import argparse
import logging
from pathlib import Path

from iccore import logging_utils
from iccore import runtime

from iccicd.packaging import PyPiContext, PythonPackage
from iccicd.repo import PythonRepo
from iccicd.version import Version
from iccicd.version_control.gitlab import GitlabInterface, GitlabProject
from iccicd.version_control.git_repo import GitRepo, GitRemote, GitUser

logger = logging.getLogger(__name__)


def launch_common(args):
    runtime.ctx.set_is_dry_run(args.dry_run)
    logging_utils.setup_default_logger()


def deploy(args):
    launch_common(args)

    logger.info("Doing deployment")

    pypi_ctx = PyPiContext(args.token, args.use_test_repo)
    package = PythonPackage(args.repo_dir)
    package.build()
    package.upload(pypi_ctx)

    logger.info("Finished deployment")


def set_version(args):
    launch_common(args)

    logger.info("Setting version number")

    repo = PythonRepo(args.repo_dir)
    repo.set_version(Version(args.version))

    logger.info("Finished setting version number")


def increment_tag(args):
    launch_common(args)

    logger.info("Incrementing tag")

    git = GitRepo(args.repo_dir, read_user=False)
    if args.user_name:
        git.set_user(GitUser(args.user_name, args.user_email))
    if args.url:
        url_prefix = f"https://oauth2:{args.token}"
        git.add_remote(GitRemote("oauth_remote", f"{url_prefix}@{args.url}"))

    git.increment_tag(field=args.field)

    logger.info("Finished incrementing tag")


def gitlab_ci_push(args):
    launch_common(args)

    logger.info("CI pushing state of current checkout")

    user = GitUser(args.user_name, args.user_email)
    project = GitlabProject(args.instance_url, args.repo_url)

    gitlab = GitlabInterface(project, user, args.access_token)
    gitlab.push_change(args.message)

    logger.info("CI finished pushing state of current checkout")


def main_cli():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dry_run",
        type=int,
        default=0,
        help="Dry run script - 0 can modify, 1 can read, 2 no modify - no read",
    )
    subparsers = parser.add_subparsers(required=True)

    deploy_parser = subparsers.add_parser("deploy")
    deploy_parser.add_argument(
        "--repo_dir",
        type=Path,
        default=Path(os.getcwd()),
        help="Path to the repo to be deployed",
    )

    deploy_parser.add_argument(
        "--token",
        type=str,
        default="",
        help="Authentication token for the target repo",
    )

    deploy_parser.add_argument(
        "--use_test_repo",
        type=bool,
        default=False,
        help="If there is an available test repo use it.",
    )
    deploy_parser.set_defaults(func=deploy)

    set_version_parser = subparsers.add_parser("set_version")
    set_version_parser.add_argument(
        "--repo_dir",
        type=Path,
        default=Path(os.getcwd()),
        help="Path to the repo to set the version",
    )

    set_version_parser.add_argument(
        "version",
        type=str,
        help="The version to set",
    )
    set_version_parser.set_defaults(func=set_version)

    increment_tag_parser = subparsers.add_parser("increment_tag")
    increment_tag_parser.add_argument(
        "--repo_dir",
        type=Path,
        default=Path(os.getcwd()),
        help="Path to the repo to increment the tag",
    )

    increment_tag_parser.add_argument(
        "--field",
        type=str,
        default="patch",
        help="The tag field to increment: 'major', 'minor' or 'patch'",
    )
    increment_tag_parser.add_argument(
        "--user_name", type=str, default="", help="Name of the CI user"
    )
    increment_tag_parser.add_argument(
        "--user_email", type=str, default="", help="Email of the CI user"
    )
    increment_tag_parser.add_argument(
        "--url", type=str, default="", help="Url for the repo remote"
    )
    increment_tag_parser.add_argument(
        "--token", type=str, default="", help="Oath access token for the repo"
    )
    increment_tag_parser.set_defaults(func=increment_tag)

    ci_push_parser = subparsers.add_parser("ci_push")
    ci_push_parser.add_argument("--user_name", type=str, help="Name of the CI user")
    ci_push_parser.add_argument("--user_email", type=str, help="Email of the CI user")
    ci_push_parser.add_argument(
        "--instance_url", type=str, help="Url for the target ci instance"
    )
    ci_push_parser.add_argument(
        "--repo_url", type=str, help="Url for the repo relative to the ci instance"
    )
    ci_push_parser.add_argument(
        "--access_token", type=str, help="Oath access token for the repo"
    )
    ci_push_parser.add_argument("--message", type=str, help="Commit message")
    ci_push_parser.set_defaults(func=gitlab_ci_push)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main_cli()
