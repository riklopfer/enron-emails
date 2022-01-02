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

python bin/clean-dump.py --maildir data/maildir --box inbox

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

```shell
bin/run_mlm.py --model_name_or_path=google/mobilebert-uncased \
				--output_dir=model \
				--train_file=data/maildir-inbox-clean.txt \
				--max_seq_length=128 \
				--learning_rate=5e-5 

```

Hey! It worked! But, it looks like it's goin gto take way too long to train. 

```
  267/62905 [..............................] - ETA: 16:40:51 - loss: 2.7156 
```


Installing Tensorflow
=====================

Instructions came from [here](https://developer.apple.com/metal/tensorflow-plugin/). Since I started from [here](https://github.com/riklopfer/DarwinZSH)-ish, I already had miniforge setup. 

```shell
conda install -c apple tensorflow-deps
python -m pip install tensorflow-macos
python -m pip install tensorflow-metal

```

