import os
import re
import subprocess
from enum import Enum
from pathlib import Path


def main():
    msgs = messages(target_sha(), current_sha())
    major, minor, patch = version()
    if any(i.breaking_change for i in msgs):
        set_version(major + 1, 0, 0)
    elif any(i.type == MessageType.FEATURE for i in msgs):
        set_version(major, minor + 1, 0)
    else:
        set_version(major, minor, patch + 1)


def current_sha():
    return os.environ.get('CI_COMMIT_SHA') or \
           subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('utf8').strip()


def target_sha():
    return os.environ.get('CI_MERGE_REQUEST_TARGET_BRANCH_SHA') or \
           os.environ.get('CI_COMMIT_BEFORE_SHA') or \
           subprocess.check_output(['git', 'rev-parse', 'HEAD~1']).decode('utf8').strip()


def messages(sha1, sha2):
    out = subprocess.check_output(['git', 'log', '--pretty=oneline', f'{sha1}...{sha2}']).decode('utf8').strip()
    messages = [Message(i) for i in out.split('\n')]
    print('calculating new version from messages:')
    print('\n'.join(i.message for i in messages))
    return messages


def version():
    version_strs = [
        i.split(' ')[1]
        for i in subprocess.check_output(['yolk', '-V', 'stringanalysis']).decode('utf8').strip().split('\n')
    ]

    versions = []
    for i in version_strs:
        result = re.search(r'(\d+)\.(\d+)\.(\d+)', i)
        versions.append(tuple(int(i) for i in result.groups()[0:3]))

    versions = sorted(versions, reverse=True)
    current_version = versions[0]
    print(f'current version={current_version}')
    return current_version


def set_version(major, minor, patch):
    set_cargo_version(major, minor, patch)
    set_pyproject_version(major, minor, patch)


def set_cargo_version(major, minor, patch):
    cargo_file = Path(__file__).absolute().parent / 'Cargo.toml'
    cargo_file.write_text(re.sub(
        f'\[package\]\nname = "stringanalysis"\nversion = "\d+\.\d+\.\d+"',
        f'[package]\nname = "stringanalysis"\nversion = "{major}.{minor}.{patch}"',
        cargo_file.read_text()
    ))


def set_pyproject_version(major, minor, patch):
    cargo_file = Path(__file__).absolute().parent / 'pyproject.toml'
    cargo_file.write_text(re.sub(
        f'version = "\d+\.\d+\.\d+"',
        f'version = "{major}.{minor}.{patch}"',
        cargo_file.read_text()
    ))



class MessageType(Enum):
    FEATURE = 1
    FIX = 2
    REFACTOR = 3
    UNKNOWN = 4


class Message:
    def __init__(self, text):
        result = re.search(r'(feat|fix|refactor)(!?): (.*?)($|\n)', text)

        if not result:
            self.type = MessageType.UNKNOWN
            self.breaking_change = False
            self.message = text
            return

        self.type = {
            'feat': MessageType.FEATURE,
            'fix': MessageType.FIX,
            'refactor': MessageType.REFACTOR
        }[result.groups()[0]]
        self.breaking_change = result.groups()[1] == '!'
        self.message = result.groups()[2]


if __name__ == '__main__':
    main()
