#!/usr/bin/env python
# coding=utf-8
import argparse
import logging
import os
import random
import sys
import textwrap
from typing import List, Tuple

import transformers
from transformers.pipelines import pipeline

from enron_emails import tools

logger = logging.getLogger(os.path.basename(__file__))


def random_text(mail_files: List[str], seed=None) -> str:
    rng = random.Random(seed)
    rng.shuffle(mail_files)

    for file in mail_files:
        thread = tools.get_thread(file)
        if thread:
            return thread[0]
            # return rng.sample(thread, k=1)[0]


class Generator(object):
    def __init__(self, model: str):
        self.generator = pipeline('text-generation', model=model)
        self.tokenizer = transformers.AutoTokenizer.from_pretrained(model)

    def _truncate_seed(self, seed_text: str, max_length: int) -> str:
        tokens = self.tokenizer.tokenize(seed_text)
        # truncate to half max length
        seed_max_length = max_length // 2
        if len(tokens) > seed_max_length:
            logger.warning("Truncating seed text:\n%s", seed_text)
            return self.tokenizer.convert_tokens_to_string(tokens[:seed_max_length])
        else:
            return seed_text

    def _end_on_eos(self, text: str) -> str:
        # end on a sentence boundary? this assumes we have a
        end_idx = max(text.rfind('.'), text.rfind('?'), text.rfind('!'))
        if end_idx > -1:
            return text[:end_idx + 1]
        else:
            return text

    def generate(self, seed_text: str, max_length: int) -> Tuple[str, str]:
        seed_text = self._truncate_seed(seed_text, max_length)
        seed_text = self._end_on_eos(seed_text)

        result = self.generator(seed_text, max_length=max_length)
        generated = result.pop()['generated_text']

        generated = self._end_on_eos(generated)
        return seed_text, generated


def main(args: argparse.Namespace):
    maildir = args.maildir
    boxes = set(args.boxes) if args.boxes else ()
    users = set(args.users) if args.users else ()
    max_length = args.max_length
    model = args.model

    generator = Generator(model)

    files = list(tools.find_files(maildir, boxes, users))

    # keep going util killed
    while True:
        rand_text = random_text(files)
        seed_text, generated = generator.generate(rand_text, max_length)

        print("." * 20)
        print(textwrap.fill(f"seed_text: {seed_text}", width=80))
        print("." * 20)
        print(textwrap.fill(generated, width=80))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--maildir', help="path to the top mail dir", required=True)
    parser.add_argument('--box', help="target box", type=str, action='append', dest='boxes')
    parser.add_argument('--user', help="target user", type=str, action='append', dest='users')

    parser.add_argument('--model', help="model name or path", type=str, default='gpt2')
    parser.add_argument('--max_length', help="max generation length", type=int, default=200)
    sys.exit(main(parser.parse_args()))
