import argparse
import glob
import logging
import os.path
import sys

from tokenizers import Tokenizer
from tokenizers.models import BPE
from tokenizers.pre_tokenizers import Whitespace, Digits, Sequence
from tokenizers.trainers import BpeTrainer

logger = logging.getLogger(os.path.basename(__file__))


def main(args: argparse.Namespace):
    files = glob.glob(args.input_glob)
    out_path = args.out_path

    assert files, \
        f"did not find any files with glob: {args.input_glob}"

    tokenizer = Tokenizer(BPE(unk_token="[UNK]"))
    tokenizer.pre_tokenizer = Sequence([Whitespace(), Digits()])

    trainer = BpeTrainer(special_tokens=["[UNK]", "[CLS]", "[SEP]", "[PAD]", "[MASK]"])
    tokenizer.train(files, trainer)

    tokenizer.save(out_path)
    logger.info("Saved tokenizer to %s", out_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_glob', help="glob for input files")
    parser.add_argument('--out-path', '-o', help="write tokenizer to this file", default='tokenizer.json')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    sys.exit(main(args))
