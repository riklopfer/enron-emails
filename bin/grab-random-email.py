#!/usr/bin/env python
# coding=utf-8
import argparse
import logging
import os
import random
import re
import sys
from typing import List

from enron_emails import tools

logger = logging.getLogger(os.path.basename(__file__))


def _is_good_segment(segment: str) -> bool:
    if not segment:
        return False

    if re.search(r"^(:?To:|From:|cc:|Subject:).+@.+$", segment, flags=re.MULTILINE):
        return False

    return True


def random_text(mail_files: List[str], seed=None):
    rng = random.Random(seed)
    rng.shuffle(mail_files)

    for file in mail_files:
        contents = tools.get_contents(file)

        segments = [_ for _ in contents.split("\n\n") if _is_good_segment(_)]
        if segments:
            return segments[0]


def main(args: argparse.Namespace):
    maildir = args.maildir
    boxes = set(args.boxes) if args.boxes else ()
    users = set(args.users) if args.users else ()
    out_file = args.out_file

    files = list(tools.find_files(maildir, boxes, users))

    while True:
        text = random_text(files)
        print(text)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--maildir', help="path to the top mail dir", required=True)
    parser.add_argument('--box', help="target box", type=str, action='append', dest='boxes')
    parser.add_argument('--user', help="target user", type=str, action='append', dest='users')
    parser.add_argument('--out-file', help="output file", default=None)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    sys.exit(main(args))
