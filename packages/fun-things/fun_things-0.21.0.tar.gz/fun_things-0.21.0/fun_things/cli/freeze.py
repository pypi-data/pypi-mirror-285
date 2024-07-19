import os
import re
from argparse import _SubParsersAction

RX_BITBUCKET = r"^-e git\+https://(.+)@bitbucket\.org\/(.+)\/(.+)\.git@(.+)#egg"
IGNORES = [
    "pkg_resources==0.0.0",
]


def _bitbucket(line: str):
    match = re.match(RX_BITBUCKET, line)

    if match == None:
        return None

    access_token = match[1]
    path = match[2]
    name = match[3]
    commit_hash = match[4]

    return (
        f"{name} @ git+https://{access_token}@bitbucket.org/{path}/{name}@{commit_hash}"
    )


def _selector(line: str):
    line = line.strip()

    if line in IGNORES:
        return ""

    bitbucket = _bitbucket(line)

    if bitbucket != None:
        line = bitbucket

    print(line)
    return line + "\r\n"


def _main(args):
    file = args.f

    os.system(f"pip freeze > {file}")

    with open(file, "r") as f:
        lines = f.readlines()
        lines = map(_selector, lines)

    with open(file, "w") as f:
        f.writelines(lines)


def freeze(subparsers: _SubParsersAction):
    parser = subparsers.add_parser(
        "freeze",
        help="pip freeze",
    )
    parser.add_argument(
        "-f",
        type=str,
        help="filepath",
        default="requirements.txt",
        required=False,
    )
    parser.set_defaults(func=_main)
