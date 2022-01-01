Mucking About with Enron Emails
=========

Let's see

Started [here](https://www.cs.cmu.edu/~enron/)


Download the data (423M)

```shell
curl -o - https://www.cs.cmu.edu/~enron/enron_mail_20150507.tar.gz | tar xzvf -

```

Dump the "clean" text

```shell
python clean-dump.py 
```
