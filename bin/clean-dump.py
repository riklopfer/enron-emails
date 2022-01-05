#!/usr/bin/env python
# coding=utf-8
import argparse
import collections
import json
import logging
import os
import sys
from typing import TextIO, List

import tqdm

from enron_emails import tools

logger = logging.getLogger(os.path.basename(__file__))


def print_contents(mail_files: List[str], ofp: TextIO):
    files_dumped = collections.Counter()
    for mail_file in tqdm.tqdm(mail_files):
        if not os.path.isfile(mail_file):
            continue
        try:
            thread = tools.get_thread(mail_file)
            print("\n\n".join(thread), file=ofp)
            files_dumped[os.path.dirname(mail_file)] += 1
        except UnicodeDecodeError:
            pass

    dump_info = collections.OrderedDict(sorted(files_dumped.items(), key=lambda _: _[1], reverse=True))
    total_dumped = sum(dump_info.values())
    logger.info("%d files dumped\n%s", total_dumped, json.dumps(dump_info, indent=2))


def main(args: argparse.Namespace):
    maildir = args.maildir
    boxes = args.boxes if args.boxes else ()
    users = args.users if args.users else ()
    out_file = args.out_file

    files = list(tools.find_files(maildir, boxes, users))

    if out_file is None:
        out_file = maildir
        if users:
            out_file += f'_{"+".join(users)}'
        if boxes:
            out_file += f'_{"+".join(boxes)}'
        out_file += ".txt"

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
