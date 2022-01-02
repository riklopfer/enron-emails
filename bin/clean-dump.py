#!/usr/bin/env python
# coding=utf-8
import argparse
import glob
import logging
import os
import re
import sys
from typing import Set

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


def print_contents(maildir: str, boxes: Set[str], ofp):
    files_dumped = 0
    for person in os.listdir(maildir):
        person_dir = os.path.join(maildir, person)

        for box in os.listdir(person_dir):
            if box not in boxes:
                continue
            box_dir = os.path.join(person_dir, box)

            for mail_file in glob.glob(f'{box_dir}/**', recursive=True):
                if not os.path.isfile(mail_file):
                    continue
                # print(mail_file)

                try:
                    contents = get_contents(mail_file)
                    print(contents, file=ofp)
                    files_dumped += 1
                except UnicodeDecodeError:
                    pass
    logger.info("%d files dumped", files_dumped)


def main(args: argparse.Namespace):
    maildir = args.maildir
    boxes = set(_.strip() for _ in args.boxes)
    out_file = args.out_file
    if out_file is None:
        out_file = f'{maildir}-{"-".join(args.boxes)}-clean.txt'

    with open(out_file, 'w', encoding='utf8') as ofp:
        print_contents(maildir, boxes, ofp)

    logger.info("Saved text to '%s'", out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--maildir', help="path to the top mail dir", required=True)
    parser.add_argument('--box', help="target box", type=str, nargs='+', dest='boxes')
    parser.add_argument('--out-file', help="output file", default=None)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    sys.exit(main(args))
