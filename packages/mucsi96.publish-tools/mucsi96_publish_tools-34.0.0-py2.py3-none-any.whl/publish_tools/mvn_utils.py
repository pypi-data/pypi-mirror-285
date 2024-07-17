from os import environ
from tempfile import NamedTemporaryFile
import xml.etree.ElementTree as xml
import sys

from subprocess import run
from pathlib import Path
from textwrap import dedent
from typing import List
from .github_utils import create_release

maven_namespace = "http://maven.apache.org/POM/4.0.0"


def get_package_info(root_path: Path):
    root = xml.parse(root_path / "pom.xml").getroot()
    namespace = {"maven": maven_namespace}
    group_id = root.find("maven:groupId", namespace)
    artifact_id = root.find("maven:artifactId", namespace)

    return {
        "group_id": group_id.text,  # type: ignore
        "artifact_id": artifact_id.text,  # type: ignore
    }


def set_package_version(root_path: Path, version: int):
    tree = xml.parse(root_path / "pom.xml")
    root = tree.getroot()
    namespace = {"maven": maven_namespace}
    version_tag = root.find("maven:version", namespace)

    version_tag.text = f"{version}.0.0"  # type: ignore

    tree.write(
        root_path / "pom.xml",
        encoding="utf-8",
        xml_declaration=True,
        default_namespace=maven_namespace,
    )


def import_gpg_key(gpg_private_key: str):
    with NamedTemporaryFile(mode="w") as key_file:
        key_file.write(dedent(gpg_private_key))
        key_file.flush()

        run(
            ["gpg", "--batch", "--import", key_file.name],
            check=True,
        )


def add_release_profile(root_path: Path):
    namespace = {"maven": maven_namespace}
    template_root = xml.parse(Path(__file__).parent / "template/pom.xml").getroot()
    template_profiles = template_root.find("maven:profiles", namespace)

    if template_profiles is None:
        raise Exception("No profiles found in template")

    tree = xml.parse(root_path / "pom.xml")
    root = tree.getroot()
    profiles = root.find("maven:profiles", namespace)

    if profiles is None:
        root.append(template_profiles)
    else:
        profiles.append(template_profiles[0])

    tree.write(
        root_path / "pom.xml",
        encoding="utf-8",
        xml_declaration=True,
        default_namespace=maven_namespace,
    )


def publish_mvn_package(
    *,
    src: Path,
    version: int | None,
    tag_prefix: str,
    maven_username: str,
    maven_password: str,
    gpg_private_key: str,
    gpg_passphrase: str,
    github_access_token: str,
):

    if version is None:
        return
    
    if not maven_username:
        print("Maven username is missing", flush=True, file=sys.stderr)
        exit(1)

    if not maven_password:
        print("Maven password is missing", flush=True, file=sys.stderr)
        exit(1)

    if not gpg_private_key:
        print("GPG private key is missing", flush=True, file=sys.stderr)
        exit(1)

    if not gpg_passphrase:
        print("GPG passphrase is missing", flush=True, file=sys.stderr)
        exit(1)

    if not github_access_token:
        print("GitHub access token is missing", flush=True, file=sys.stderr)
        exit(1)

    package_info = get_package_info(src)

    set_package_version(src, version)

    import_gpg_key(gpg_private_key)

    add_release_profile(src)

    settings_path = Path(__file__).parent / "settings.xml"

    run(
        [
            "mvn",
            "deploy",
            "--batch-mode",
            "--activate-profiles",
            "release",
            "--settings",
            settings_path,
        ],
        cwd=src,
        check=True,
        env={
            **dict(
                MAVEN_USERNAME=maven_username,
                MAVEN_PASSWORD=maven_password,
                GPG_PASSPHRASE=gpg_passphrase,
            ),
            **dict(environ),
        },
    )

    create_release(
        tag_prefix=tag_prefix,
        version=version,
        access_token=github_access_token,
        body=dedent(
            f"""
            [MVN package](https://mvnrepository.com/artifact/{package_info['group_id']}/{package_info['artifact_id']})

            ```xml
                <!-- https://mvnrepository.com/artifact/{package_info['group_id']}/{package_info['artifact_id']} -->
                <dependency>
                    <groupId>{package_info['group_id']}</groupId>
                    <artifactId>{package_info['artifact_id']}</artifactId>
                    <version>{version}.0.0</version>
                </dependency>
            ```
        """
        ),
    )
    print(f"MVN package pushed successfully for {tag_prefix}:{version}", flush=True)
