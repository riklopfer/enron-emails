Mucking About with Enron Emails
===============================

Got a refurbished M1 Macbook Air for myself for Christmas. Got sick. Having fun waiting for the sickness to pass. Started [here](https://www.cs.cmu.edu/~enron/) which I heard about in [this podcast](https://99percentinvisible.org/episode/youve-got-enron-mail/) some time ago.


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

Install Tensorflow... Instructions came from [here](https://developer.apple.com/metal/tensorflow-plugin/). Since I started from [here](https://github.com/riklopfer/DarwinZSH)-ish, I already had miniforge setup. I am using Tensorflow because M1 GPU acceleration is available. 

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
PYTHONPATH=$PWD python bin/clean-dump.py --maildir data/maildir --box sent 

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
                            --output_dir=mlm_model \
                            --train_file=data/maildir_sent.txt \
                            --num_train_epochs=3 \
                            --max_seq_length=128 \
                            --per_device_train_batch_size=32 \
                            --per_device_eval_batch_size=8 \
                            --learning_rate=5e-5 

```

Hey! It worked! But, it looks like it's goin gto take way too long (6 hours per epoch) to train. 

Maybe we can reduce precision? Result is lol -- `loss: nan`. I imagine fp16 is just broken. 

Okay. Let's just do something super small that will finish quickly -- only the sent mail from this one lower-volume user `ring-a`

```shell
PYTHONPATH=$PWD python bin/clean-dump.py --maildir data/maildir --box sent --user ring-a
```

```shell
bin/run_mlm.py --model_name_or_path=google/mobilebert-uncased \
                            --output_dir=mlm_model \
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
bin/fill-blanks.py --model=mlm_model/ "this is a _ of a _"
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

Well that was more fun than I expected! That's nice. 

Generate Email
==============

Let's generate random emails seeded with an email sent from an enron user! I've done a bunch of clean up in the meantime, so that we can get a random email that _should be_ relatively clean. Now, we can try doing seeded generation... 

```shell
PYTHONPATH=$PWD python bin/gen-email.py --maildir data/maildir --box sent

```

It works! heheh. I had to do some truncation funny-business. Maybe I can find a fix later

```
....................
seed_text: Kim,  Thanks a lot. I appreciate your kind words.
....................
Kim,  Thanks a lot. I appreciate your kind words.  Flaming the bottle, my cheeks
were red…  When I saw you look so kind, I thought about something I've said
before.  It's a pity that we'll end up living together after all.  Hence it's
not only the same.  Even if we don't have a common goal, I think the time we
have should be something that can live up to it.  Fluid is the most basic
ingredient in life.  I don't think anyone could have achieved that after that.
It's like a big hole in your head.  And now, it's my turn.  And we shall start.
I hope you've enjoyed!
```

Let's try getting an email from `ring-a`...

```shell
PYTHONPATH=$PWD python bin/gen-email.py --maildir data/maildir --box sent --user ring-a
```

Ahhhhhh... classic `ring-a`

```
....................
seed_text: How are you?  Hope everything is going well.  Not much going on here
- I  think I'll go see the new movie with Richard Gere on Friday - wish you
....................
How are you?  Hope everything is going well.  Not much going on here - I  think
I'll go see the new movie with Richard Gere on Friday - wish you the best of
luck.. Well then, I have finally released my book of the month: The Best of
Richard Gere and Robert Altman. I'm looking forward to watching it, thinking
about my friends Richard and Robert and the others, and thinking about when I
can finally give everything and go back and read it again. Reply Delete Great
Book! The book will be just that awesome. It has a lot to offer. I love books so
much! It also has the perfect balance of characters and plot. I'm glad I made
the cover to use the original photos from David Cronenberg and Robert Altman on
the cover. I think that the people who bought the book in the first place just
love this book so much.
```


So the next thing would be to try to make the generated text look more consistently like emails stuff instead of a weird story! Could try to update the weights of the model with continued training like we did with MLM... 


CLM Training
============

Just like before... I'll grab the script and check it in. 

```shell
curl -o bin/run_clm.py https://raw.githubusercontent.com/huggingface/transformers/master/examples/tensorflow/language-modeling/run_clm.py && 
chmod +x bin/run_clm.py
```

can we just re use the parameters from MLM?? not really... 

* need to use `distilgpt2`
* `block_size` instead of `max_seq_length` [PR](https://github.com/huggingface/transformers/pull/15036)

```shell

bin/run_clm.py --model_name_or_path=distilgpt2 \
              --output_dir=clm_model \
              --train_file=data/maildir_ring-a_sent.txt \
              --num_train_epochs=3 \
              --block_size=256 \
              --per_device_train_batch_size=32 \
              --per_device_eval_batch_size=8 \
              --learning_rate=5e-5 

```

Almost working. Just need a little more data. let's add `pereira-s` who has similar volume to ring-a

```shell
PYTHONPATH=$PWD python bin/clean-dump.py --maildir data/maildir --box sent --user ring-a --user pereira-s

```

```shell
bin/run_clm.py --model_name_or_path=distilgpt2 \
              --output_dir=clm_model \
              --train_file=data/maildir_ring-a+pereira-s_sent.txt \
              --num_train_epochs=3 \
              --block_size=256 \
              --per_device_train_batch_size=32 \
              --per_device_eval_batch_size=8 \
              --learning_rate=5e-5 

```


Nice! But we forgot to save the tokenizer... so one more time. 

```
5/5 [==============================] - 221s 51s/step - loss: 3.4780 - val_loss: 3.5771
Configuration saved in clm_model/config.json
Model weights saved in clm_model/tf_model.h5
```

Okay.. now it's hanging for some reason... 

**GOING TO A CLOUD GPU**

let's get more data... :P

```shell
PYTHONPATH=$PWD python bin/clean-dump.py --maildir data/maildir --box sent

```

```shell
bin/run_clm.py --model_name_or_path=distilgpt2 \
              --output_dir=gpu_clm_model \
              --train_file=data/maildir_sent.txt \
              --num_train_epochs=3 \
              --block_size=256 \
              --per_device_train_batch_size=64 \
              --per_device_eval_batch_size=64 \
              --learning_rate=5e-5 \
              2>&1 | tee log

```

15 minutes later.... 

```shell
gcloud compute scp gpu-instance:~/enron-emails/gpu_clm_model.tar.gz .

gcloud compute instances stop gpu-instance 
```


Now let's try generating again! :D

```shell
PYTHONPATH=$PWD python bin/gen-email.py --model gpu_clm_model/ --maildir data/maildir --box sent --user ring-a

```

```
....................
seed_text: A Preacher wanted to raise money for his church, and being told that
there  was a fortune in Horse Racing, he decided to purchase a horse and enter
him  in the race.  However, at the local auction the going price for horses was
so steep that he ended up buying a Donkey instead.  He figured that since he
had it, he might as well go ahead and enter it in the races, and to his
surprise
....................
A Preacher wanted to raise money for his church, and being told that there  was
a fortune in Horse Racing, he decided to purchase a horse and enter him  in the
race.  However, at the local auction the going price for horses was   so steep
that he ended up buying a Donkey instead.  He figured that since he   had it, he
might as well go ahead and enter it in the races, and to his   surprise, he had
to spend much of his time driving it around to get some of the  pets  to the
finish line and that's ok.  How does  the new horses look?  They look so good.
I guess they are more  beautiful than the old ones...this is a good horse.  I
would like to have  them buy them.  I think there are many of those horses I've
already  been thinking about.
```

Hahah. Oh man ring-a... never fail to disappoint. :)


