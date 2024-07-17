import json
import sys

from subprocess import run
from pathlib import Path
from textwrap import dedent
from typing import List
from .github_utils import create_release

def get_package_name(root_path: Path):
    with open(root_path / 'package.json', 'r') as file:
        package_data = json.load(file)

    return package_data['name']


def set_package_version(root_path: Path, version: int):
    with open(root_path / 'package.json', 'r') as file:
        package_data = json.load(file)

    package_data['version'] = f'{version}.0.0'

    with open(root_path / 'package.json', 'w') as file:
        json.dump(package_data, file, indent=2)


def authenticate(src: Path, npm_access_token: str):
    with open(src / '.npmrc', 'w') as file:
        file.write(
            f'//registry.npmjs.org/:_authToken={npm_access_token}')
        file.close()
    run(['npm', 'whoami'], cwd=src, check=True)


def publish_npm_package(
    *,
    src: Path,
    version: int | None,
    tag_prefix: str,
    npm_access_token: str,
    github_access_token: str
):
    if version is None:
        return
    
    if not npm_access_token:
        print('NPM access token is missing', flush=True, file=sys.stderr)
        exit(1)

    if not github_access_token:
        print('GitHub access token is missing', flush=True, file=sys.stderr)
        exit(1)

    package_name = get_package_name(src)

    authenticate(src, npm_access_token)

    set_package_version(src, version)

    run(['npm', 'publish', '--access=public'], cwd=src, check=True)

    create_release(
        tag_prefix=tag_prefix,
        version=version,
        access_token=github_access_token,
        body=dedent(f'''
            [NPM package](https://www.npmjs.com/package/{package_name})

            ```json
            "{package_name}": "^{version}.0.0"
            ```
        ''')
    )
    print(
        f'NPM package pushed successfully for {tag_prefix}:{version}', flush=True)
