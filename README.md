Mucking About with Enron Emails
===============================

Got sick. Got a new laptop. Having fun waiting for the sickness to pass. 

Started [here](https://www.cs.cmu.edu/~enron/)

Download the data (423M)

```shell
curl -o - https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz | tar xzf - -C data

```

Rust is required for HF tokenizers

```shell
brew install rust
```

Install requirements

```shell
pip install -r requirements.txt
```

Dump the "clean" text

```shell
python bin/clean-dump.py --maildir data/maildir --box all_documents 

```

Train tokenizer

```shell
python bin/train-tokenizer.py data/maildir-clean.txt -o data/tokenizer.json
```

Hmmm... Well that was fun. Let's poke around with a bit more later. 


MLM Training
============

Let's grab the MLM training script... (I'll check it in)

```shell
curl -o bin/run_mlm.py https://raw.githubusercontent.com/huggingface/transformers/master/examples/tensorflow/language-modeling/run_mlm.py && 
chmod +x bin/run_mlm.py
```


