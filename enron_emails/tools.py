import glob
import logging
import os
import re
from typing import Set, Iterable, List, TextIO

logger = logging.getLogger(os.path.basename(__file__))


def _strip_junk(contents: str) -> str:
    while True:
        stripped = contents.strip().strip(">")
        if stripped == contents:
            break
        contents = stripped
    return stripped


def _skip_until_newline(fp: TextIO):
    for header_line in fp:
        # print(header_line, end='')
        if header_line == "\n":
            break


def _get_contents(mail_file: str) -> str:
    contents = ''
    with open(mail_file, 'r', encoding='utf8') as ifp:
        _skip_until_newline(ifp)

        for line in ifp:
            line = line.lstrip(" \t>?")

            if re.search(r'--+ ?Original Message ?--+', line):
                continue

            if re.search(r"---+ ?Forwarded by", line):
                continue

            contents += line
    return contents


META_PAT = re.compile(r"^\s*(:?To:|From:|cc:|CC:).+$", flags=re.MULTILINE)


def _is_thread_separator(segment: str) -> bool:
    if META_PAT.search(segment):
        return True

    if re.search(r"----+", segment):
        return True

    return False


_seg_delimiter = "\n\n"


def get_thread(mail_file: str) -> List[str]:
    contents = _get_contents(mail_file)

    segments = contents.split(_seg_delimiter)
    # each thread item consists of a list of text segments
    thread_items: List[List[str]] = [list()]

    for segment in segments:
        if not segment:
            continue
        elif _is_thread_separator(segment):
            if thread_items[-1]:
                thread_items.append(list())
        else:
            thread_items[-1].append(segment)

    joined_segments = [_seg_delimiter.join(items).strip() for items in thread_items]
    return joined_segments


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
