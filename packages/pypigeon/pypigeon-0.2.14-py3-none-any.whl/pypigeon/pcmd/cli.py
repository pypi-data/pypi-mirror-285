import argparse
import json
import os.path
import sys
from getpass import getpass
from typing import Optional
from urllib.parse import urlparse

from pypigeon.client import login as interactive_login
from pypigeon.client import make_base_url
from pypigeon.client import PigeonClient
from pypigeon.pigeon_core import Client as CoreClient
from pypigeon.pigeon_core.errors import UnexpectedStatus
from pypigeon.pigeon_core.login import Login
from pypigeon.pigeon_core.login import LoginError
from pypigeon.pigeon_core.login import to_token_file
from pypigeon.pigeon_core.login import token_file_get_base_url

from .commands import Commands


def login(base_url: str, token_file: str, username: Optional[str]) -> PigeonClient:
    core = CoreClient(base_url=base_url)

    # first try to log in with the token file
    if os.path.exists(token_file):
        try:
            authenticated = Login(core).from_token_file(token_file)
            return PigeonClient(authenticated)
        except LoginError:
            print("Previous session is invalid...")

    # that didn't work, if the username is provided, perform a
    # semi-interactive login
    if username:
        password = getpass()
        authenticated = Login(core).with_password(username, password)
        return PigeonClient(authenticated)

    # perform a full interactive login
    parsed_url = urlparse(base_url)
    return interactive_login(parsed_url.netloc, parsed_url.scheme)


def main() -> None:
    argparser = argparse.ArgumentParser(
        prog="pcmd",
    )
    argparser.add_argument(
        "-H", "--hostname", metavar="HOSTNAME", help="connect to HOSTNAME"
    )
    argparser.add_argument(
        "--insecure",
        dest="scheme",
        default="https",
        action="store_const",
        const="http",
        help="connect using http rather than https",
    )
    argparser.add_argument(
        "-k",
        "--token-file",
        default="~/.pcmd-token",
        metavar="FN",
        help="use FN as the file to hold the login token",
    )
    argparser.add_argument(
        "-u",
        "--username",
        metavar="USERNAME",
        help="disable interactive login; log in with USERNAME",
    )
    argparser.add_argument(
        "-O",
        "--output-type",
        default="auto",
        choices=["auto", "yaml", "json", "table"],
        help="set output type",
    )
    Commands._add_to_parser(argparser.add_subparsers(title="commands", required=True))

    args = argparser.parse_args()

    token_file = os.path.expanduser(args.token_file)
    if os.path.exists(token_file) and not args.hostname:
        base_url = token_file_get_base_url(token_file)
    elif args.hostname:
        base_url = make_base_url(args.hostname, args.scheme)
    else:
        print(
            "No hostname specified! Use the `-H` option to specify the name of your"
            " Pigeon instance."
        )
        sys.exit(1)

    client = login(base_url, token_file, args.username)
    if token_file:
        to_token_file(client._client, token_file)

    if hasattr(args, "func"):
        try:
            args.func(args.cls(client, args))
        except UnexpectedStatus as ex:
            print(str(ex))
            try:
                parsed = json.loads(ex.content)
                print("error:", parsed["error"])
                if parsed["detail"]:
                    print("detail:", parsed["detail"])
            except (json.JSONDecodeError, KeyError):
                print(ex.content)

    else:
        argparser.print_usage()
