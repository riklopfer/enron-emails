#!/usr/bin/env python
# coding=utf-8
import argparse
import logging
import os
import random
import sys
import textwrap
from typing import List

import transformers

from enron_emails import tools

logger = logging.getLogger(os.path.basename(__file__))

from transformers.pipelines import pipeline


def random_text(mail_files: List[str], seed=None) -> str:
    rng = random.Random(seed)
    rng.shuffle(mail_files)

    for file in mail_files:
        thread = tools.get_thread(file)
        if thread:
            return thread[0]
            # return rng.sample(thread, k=1)[0]


def generate(model: str, seed_text: str, max_length: int) -> str:
    generator = pipeline('text-generation', model=model)

    result = generator(seed_text, max_length=max_length)
    gen_text = result.pop()['generated_text']
    return gen_text


def main(args: argparse.Namespace):
    maildir = args.maildir
    boxes = set(args.boxes) if args.boxes else ()
    users = set(args.users) if args.users else ()
    max_length = args.max_length

    files = list(tools.find_files(maildir, boxes, users))

    seed_text = random_text(files)
    tokenizer = transformers.AutoTokenizer.from_pretrained(args.model)
    tokens = tokenizer.tokenize(seed_text)
    if len(tokens) > max_length:
        # truncate to half max length
        logger.warning("Truncating seed text:\n%s", seed_text)
        seed_text = tokenizer.convert_tokens_to_string(tokens[:max_length // 2])

    generated = generate(args.model, seed_text, max_length)

    print("." * 20)
    print(f"seed_text: {seed_text[:100]}{'...' if len(seed_text) > 100 else ''}")
    print("." * 20)
    print(textwrap.fill(generated, width=80))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--maildir', help="path to the top mail dir", required=True)
    parser.add_argument('--box', help="target box", type=str, action='append', dest='boxes')
    parser.add_argument('--user', help="target user", type=str, action='append', dest='users')

    parser.add_argument('--model', help="model name or path", type=str, default='gpt2')
    parser.add_argument('--max_length', help="max generation length", type=int, default=100)
    sys.exit(main(parser.parse_args()))
