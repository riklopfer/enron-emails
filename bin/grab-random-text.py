#!/usr/bin/env python
# coding=utf-8
import argparse
import logging
import os
import random
import sys
from typing import List

from enron_emails import tools

logger = logging.getLogger(os.path.basename(__file__))


def random_text(mail_files: List[str], seed=None) -> str:
    rng = random.Random(seed)
    rng.shuffle(mail_files)

    for file in mail_files:
        thread = tools.get_thread(file)
        if thread:
            return rng.sample(thread, k=1)[0]


def main(args: argparse.Namespace):
    maildir = args.maildir
    boxes = args.boxes if args.boxes else ()
    users = args.users if args.users else ()
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
