#!/usr/bin/env python
# coding=utf-8
import argparse
import collections
import glob
import json
import logging
import os
import re
import sys
import typing
from typing import Set, Iterable

import tqdm

logger = logging.getLogger(os.path.basename(__file__))


def _skip_until_newline(fp):
    for header_line in fp:
        # print(header_line, end='')
        if header_line == "\n":
            break


def get_contents(mail_file: str) -> str:
    content = ''
    with open(mail_file, 'r', encoding='utf8') as ifp:
        _skip_until_newline(ifp)

        for line in ifp:
            if re.search(r'--+ ?Original Message ?--+', line):
                _skip_until_newline(ifp)
                continue

            if line.startswith(">"):
                continue

            content += line
            pass

    return content


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


def print_contents(mail_files: Iterable[str], ofp: typing.TextIO):
    mail_files = list(mail_files)

    files_dumped = collections.Counter()
    for mail_file in tqdm.tqdm(mail_files):
        if not os.path.isfile(mail_file):
            continue
        try:
            contents = get_contents(mail_file)
            print(contents, file=ofp)
            files_dumped[os.path.dirname(mail_file)] += 1
        except UnicodeDecodeError:
            pass

    dump_info = collections.OrderedDict(sorted(files_dumped.items(), key=lambda _: _[1], reverse=True))
    total_dumped = sum(dump_info.values())
    logger.info("%d files dumped\n%s", total_dumped, json.dumps(dump_info, indent=2))


def main(args: argparse.Namespace):
    maildir = args.maildir
    boxes = set(args.boxes) if args.boxes else ()
    users = set(args.users) if args.users else ()
    out_file = args.out_file

    if out_file is None:
        out_file = maildir
        if users:
            out_file += f'_{"+".join(users)}'
        if boxes:
            out_file += f'_{"+".join(boxes)}'
        out_file += ".txt"

    files = find_files(maildir, boxes, users)

    with open(out_file, 'w', encoding='utf8') as ofp:
        print_contents(files, ofp)

    logger.info("Saved text to '%s'", out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--maildir', help="path to the top mail dir", required=True)
    parser.add_argument('--box', help="target box", type=str, action='append', dest='boxes')
    parser.add_argument('--user', help="target user", type=str, action='append', dest='users')
    parser.add_argument('--out-file', help="output file", default=None)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    sys.exit(main(args))
