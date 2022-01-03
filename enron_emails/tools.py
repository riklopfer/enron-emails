import glob
import logging
import os
import re
from typing import Set, Iterable, List, TextIO

logger = logging.getLogger(os.path.basename(__file__))


def _skip_until_newline(fp: TextIO):
    for header_line in fp:
        # print(header_line, end='')
        if header_line == "\n":
            break


def _clean_line(line: str) -> str:
    line = line.lstrip(" \t>?")

    return line


def _get_contents(mail_file: str) -> str:
    contents = ''
    with open(mail_file, 'r', encoding='utf8') as ifp:
        # skip standard meta data
        _skip_until_newline(ifp)

        for line in ifp:

            if re.search(r'--+ ?Original Message ?--+', line):
                continue

            if re.search(r"---+ ?Forwarded by", line):
                continue

            line = _clean_line(line)

            contents += line
    return contents


T_SEP_PATS = [
    re.compile(r"^\s*(:?To:|From:|cc:|CC:).+$", flags=re.MULTILINE),
    re.compile(r"----+"),
    re.compile(r"Please respond to <"),
    re.compile(r'^ *".+?" <.+?@.+?>\s(on)?\d\d/\d\d/\d\d\d\d', re.MULTILINE)
]


def _is_thread_separator(segment: str) -> bool:
    for pat in T_SEP_PATS:
        if pat.search(segment):
            return True

    return False


_seg_delimiter = "\n\n"


def _clean_segment(segment: str) -> str:
    # random things
    segment = re.sub(r"==?\n?[\dA-F]{2};?", "", segment)
    segment = re.sub(r"(?<=[a-zA-Z])=\n?(?=[a-zA-Z])", "", segment)
    return segment


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
            segment = _clean_segment(segment)
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
