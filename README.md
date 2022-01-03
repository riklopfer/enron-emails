Mucking About with Enron Emails
===============================

Got sick. Got a new M1 Macbook Air. Having fun waiting for the sickness to pass. 

Started [here](https://www.cs.cmu.edu/~enron/)


Set up
======

Download the data (423M)

```shell
curl -o - https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz | tar xzf - -C data

```

Rust is required for HF tokenizers

```shell
brew install rust
```

Install Tensorflow... Instructions came from [here](https://developer.apple.com/metal/tensorflow-plugin/). Since I started from [here](https://github.com/riklopfer/DarwinZSH)-ish, I already had miniforge setup. 

```shell
# create & activate env
conda create -n enron-emails python=3.9
conda activate enron-emails
# install stuff
conda install -c apple tensorflow-deps
python -m pip install tensorflow-macos
python -m pip install tensorflow-metal

```

Install everything else

```shell
pip install -r requirements.txt
```



Train tokenizer
===============

Dump some "clean" text

```shell
python bin/clean-dump.py --maildir data/maildir --box sent 

```

```shell
python bin/train-tokenizer.py data/maildir_sent.txt -o data/tokenizer.json
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
				--train_file=data/maildir_sent.txt \
				--num_train_epochs=3 \
				--max_seq_length=128 \
				--per_device_train_batch_size=32 \
				--per_device_eval_batch_size=8 \
				--learning_rate=5e-5 

```

Hey! It worked! But, it looks like it's goin gto take way too long (6 hours per epoch) to train. 

Maybe we can reduce precision? Result is lol -- `loss: nan`. I imagine fp16 is just broken. 

Okay. Let's just do something super small that will finish quickly. 

```shell
python bin/clean-dump.py --maildir data/maildir --box sent --user ring-a
```

```shell
bin/run_mlm.py --model_name_or_path=google/mobilebert-uncased \
				--output_dir=model \
				--train_file=data/maildir_ring-a_sent.txt \
				--num_train_epochs=3 \
				--max_seq_length=128 \
				--per_device_train_batch_size=32 \
				--per_device_eval_batch_size=8 \
				--learning_rate=5e-5 

```


Hooray! Success! 

```
  Final train loss: 1.818
  Final train perplexity: 6.158
  Final validation loss: 1.673
  Final validation perplexity: 5.327
Configuration saved in model/config.json
Model weights saved in model/tf_model.h5
```

That was fun too. Can't do text generation... but we can do mask filling which is a little less entertaining. 


Mask Filling
============

```shell
bin/fill-blanks.py --model=model/ "this is a _ of a _"
```

yay. success! 

```
********************
this is a _ of a _
this is a [reconstruction] of a [family]
```

I wonder if we get something different when we the original model instead of the one we continued training with emails... 

```shell
bin/fill-blanks.py --model=google/mobilebert-uncased "this is a _ of a _"
```

Indeed it is! Quite different. 

```
********************
this is a _ of a _
this is a [list] of a [.]
```

Did `ring-a` mention recontruction or family? (i.e. were these words in our training corpus?)

reconstruction... no

```
❯ grep reconstruct data/maildir/ring-a/sent/* | wc -l
       0
```

family... yes! 

```
❯ grep family data/maildir/ring-a/sent/* | wc -l
       5
```