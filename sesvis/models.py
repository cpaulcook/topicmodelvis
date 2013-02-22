from django.db import models

class Corpus(models.Model):
    corpus_id = models.IntegerField()
    name = models.TextField()
    description = models.TextField()

class SubCorpus(models.Model):
    sub_corpus_id = models.IntegerField()
    name = models.TextField()
    corpus = models.ForeignKey(Corpus)
    description = models.TextField()
    
class Topic(models.Model):
    topic_id = models.IntegerField()
    corpus = models.ForeignKey(Corpus)

class ProbWordGivenTopic(models.Model):
    topic = models.ForeignKey(Topic)
    word = models.TextField()
    prob = models.FloatField()

class Document(models.Model):
    doc_id = models.IntegerField()
    title = models.TextField()
    text = models.TextField()
    corpus = models.ForeignKey(Corpus)

class ProbTopicGivenDoc(models.Model):
    topic = models.ForeignKey(Topic)
    document = models.ForeignKey(Document)
    prob = models.FloatField()

class SubCorpusContent(models.Model):
    subcorpus = models.ForeignKey(SubCorpus)
    document = models.ForeignKey(Document)

class TokenLevelTopicAllocation(models.Model):
    topic = models.ForeignKey(Topic)    
    document = models.ForeignKey(Document)    
    token_id = models.TextField()
    word = models.TextField()
