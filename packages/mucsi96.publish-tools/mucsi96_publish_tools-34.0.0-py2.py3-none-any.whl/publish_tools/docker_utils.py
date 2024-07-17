import sys
from subprocess import run
from pathlib import Path
from textwrap import dedent
from typing import List
from .github_utils import create_release


def build_and_push_docker_img(
    *,
    src: Path,
    version: int | None,
    tag_prefix: str,
    image_name: str,
    docker_username: str,
    docker_password: str,
    github_access_token: str,
):
    if version is None:
        return
    
    if not github_access_token:
        print('GitHub access token is missing', flush=True, file=sys.stderr)
        exit(1)

    run(['docker', 'login', '--username', docker_username,
        '--password-stdin'], input=docker_password.encode(), check=True)
    run(['docker', 'buildx', 'create', '--use'])
    run(['docker', 'buildx', 'build', '--platform', 'linux/amd64,linux/arm64/v8', '--tag', f'{docker_username}/{image_name}:latest', '--tag',
        f'{docker_username}/{image_name}:{version}', '--push', '.'], cwd=src, check=True)

    create_release(
        tag_prefix=tag_prefix,
        version=version,
        access_token=github_access_token,
        body=dedent(f'''
            [Docker image on DockerHub](https://hub.docker.com/repository/docker/{docker_username}/{image_name})

            ```yaml
            image: {docker_username}/{image_name}:{version}
            ```
        ''')
    )
    print(
        f'Docker image pushed successfully for {tag_prefix}:{version}', flush=True)
