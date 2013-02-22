from django.db import models

# Create your models here.
class Corpus(models.Model):
    corpus_id = models.IntegerField()
    name = models.TextField()
    description = models.TextField()

class SubCorpus(models.Model):
    sub_corpus_id = models.IntegerField()
    name = models.TextField()
    description = models.TextField()
    corpus = models.ForeignKey(Corpus)
    
    



# class Poll(models.Model):
#     question = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')

# class Choice(models.Model):
#     poll = models.ForeignKey(Poll)
#     choice = models.CharField(max_length=200)
#     votes = models.IntegerField()
