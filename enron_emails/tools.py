import glob
import logging
import os
import re
import typing
from typing import Set, Iterable

logger = logging.getLogger(os.path.basename(__file__))


# def _strip_junk(contents: str) -> str:
#     while True:
#         stripped = contents.strip().strip("'\"")
#         if stripped == contents:
#             break
#         contents = stripped
#     return stripped


def _skip_until_newline(fp: typing.TextIO):
    for header_line in fp:
        # print(header_line, end='')
        if header_line == "\n":
            break


def get_contents(mail_file: str) -> str:
    contents = ''
    with open(mail_file, 'r', encoding='utf8') as ifp:
        _skip_until_newline(ifp)

        for line in ifp:
            if line.startswith(">"):
                continue

            if re.search(r'--+ ?Original Message ?--+', line):
                _skip_until_newline(ifp)
                continue

            if re.search(r"---+ ?Forwarded by", line):
                _skip_until_newline(ifp)
                _skip_until_newline(ifp)
                continue

            contents += line
            pass

    return contents.strip()


def find_files(maildir: str, boxes: Set[str], users: Set[str]) -> Iterable:
    for user in os.listdir(maildir):
        if users and user not in users:
            continue

        user_dir = os.path.join(maildir, user)

        for box in os.listdir(user_dir):
            if boxes and box not in boxes:
                continue
            box_dir = os.path.join(user_dir, box)

            for mail_file in glob.glob(f'{box_dir}/**', recursive=True):
                if os.path.isfile(mail_file):
                    yield mail_file
