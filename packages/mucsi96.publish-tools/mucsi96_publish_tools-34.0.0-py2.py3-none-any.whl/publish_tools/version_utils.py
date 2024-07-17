import re
import sys

from pathlib import Path
from subprocess import run
from typing import List


def get_previous_tag(tag_prefix):
    result = run(['git', 'describe', '--tags',
                 f'--match={tag_prefix}-[1-9]*', '--abbrev=0'], capture_output=True, text=True)
    if result.stderr:
        print(result.stderr, file=sys.stderr, flush=True)

    if result.returncode or not result.stdout:
        return None

    return result.stdout.strip()


def has_source_code_changed(src: Path, prev_tag: str, ignore: List[str]):
    ignore_str = ' '.join(map(lambda x: f'\':!{x}\'', ignore))
    print(f'Detecting changes in {src} since {prev_tag}', flush=True)
    args = list(filter(bool, ['git', 'diff', '--name-only',
                              'HEAD', prev_tag, '--', '.', ignore_str]))
    result = run(args, cwd=src, capture_output=True, text=True)

    if result.stderr:
        print(result.stderr, file=sys.stderr, flush=True)

    if result.stdout:
        print(result.stdout, flush=True)

    return bool(result.stdout)


def get_latest_version(tag_prefix: str):
    result = run(['git', 'tag', '--list', '--sort=-v:refname',
                 f'{tag_prefix}-[1-9]*'], capture_output=True, text=True)

    if result.stderr:
        print(result.stderr, flush=True, file=sys.stderr)

    if result.returncode or not result.stdout:
        return None

    tags = result.stdout.splitlines()
    latest_tag = tags[0]

    return int(
        re.sub(rf'^{tag_prefix}-', '', latest_tag))


def get_version(*, src: Path, tag_prefix: str, ignore: List[str] = []) -> int | None:
    prev_tag = get_previous_tag(tag_prefix)

    if prev_tag:
        if has_source_code_changed(src, prev_tag, ignore) is False:
            version = re.sub(rf'^{tag_prefix}-', '', prev_tag)
            print(
                f'No changes detected since {tag_prefix}:{version} in {src}.', flush=True)
            
            return None

    latest_version = get_latest_version(tag_prefix)

    if latest_version:
        new_version = latest_version + 1
    else:
        new_version = 1

    print(
        f'Changes detected for {tag_prefix}. New version: {new_version}', flush=True)
    return new_version


def set_version(tag_prefix: str, version: int) -> None:
    print(f'Tagging with {tag_prefix}-{version}', flush=True)
    run(['git', 'tag', f'{tag_prefix}-{version}'], check=True)
    run(['git', 'push', '--tags'], check=True)