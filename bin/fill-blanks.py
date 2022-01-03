#!/usr/bin/env python
# coding=utf-8
import argparse
import sys

from transformers.pipelines import pipeline


def maybe_make_mask(tok: str) -> str:
    """replace all _ with [MASK]"""
    if all(c == "_" for c in tok):
        return "[MASK]"
    return tok


def fill_blanks(model: str, text: str) -> str:
    """Fill blanks (_'s) in text"""
    masked_tokens = [maybe_make_mask(_) for _ in text.split(" ")]
    text = " ".join(masked_tokens)
    filler = pipeline(task='fill-mask', model=model)
    results = filler(text)

    # replace masked tokens
    replaced_tokens = []
    for token in masked_tokens:
        if token == "[MASK]":
            result = results.pop(0)
            replaced_tokens.append(f"[{result[0]['token_str']}]")
        else:
            replaced_tokens.append(token)

    return " ".join(replaced_tokens)


def main(args: argparse.Namespace):
    filled = fill_blanks(args.model, args.text)

    print("*" * 20)
    print(args.text)
    print(filled)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('text', help="some text with _ to be filled", type=str)
    parser.add_argument('--model', help="model name or path", type=str, required=True)
    sys.exit(main(parser.parse_args()))
