Mucking About with Enron Emails
=========

Let's see

Started [here](https://www.cs.cmu.edu/~enron/)


Download the data (423M)

```shell
curl -o - https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz | tar xzvf - -C data

```

Dump the "clean" text

```shell
python bin/clean-dump.py --maildir data/maildir --box all_documents 

```

Rust is required for HF tokenizers

```shell
brew install rust
```

Train tokenizer

```shell
python bin/train-tokenizer.py data/maildir-clean.txt
```
