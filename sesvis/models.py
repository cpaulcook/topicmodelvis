from django.db import models

def build_unicode(*l):
    return ':'.join([unicode(x) for x in l])

class Corpus(models.Model):
    name = models.TextField()
    description = models.TextField()

    def __unicode__(self):
        return build_unicode((self.name))

class SubCorpus(models.Model):
    name = models.TextField()
    corpus = models.ForeignKey(Corpus)
    description = models.TextField()
    
    def __unicode__(self):
        return build_unicode(self.corpus.name, self.name)

class Topic(models.Model):
    corpus = models.ForeignKey(Corpus)

    def __unicode__(self):
        return build_unicode(self.corpus.name, self.id)

class ProbWordGivenTopic(models.Model):
    topic = models.ForeignKey(Topic)
    word = models.TextField()
    prob = models.FloatField()

    def __unicode__(self):
        return build_unicode(self.topic.corpus.name, self.topic.id, self.word)

class Document(models.Model):
    title = models.TextField()
    corpus = models.ForeignKey(Corpus)

    def __unicode__(self):
        return build_unicode(self.corpus.name, self.title)

class DocumentContent(models.Model):
    document = models.ForeignKey(Document)
    text = models.TextField()
    
    def __unicode__(self):
        return build_unicode(self.document.corpus.name, self.document.title, self.text[:20])

class ProbTopicGivenDoc(models.Model):
    topic = models.ForeignKey(Topic)
    document = models.ForeignKey(Document)
    prob = models.FloatField()

    def __unicode__(self):
        return build_unicode(self.document.corpus.name, self.document.title,
                             self.topic.id)

class SubCorpusContent(models.Model):
    subcorpus = models.ForeignKey(SubCorpus)
    document = models.ForeignKey(Document)

    def __unicode__(self):
        return build_unicode(self.subcorpus.corpus.name, self.subcorpus.name,
                             self.document.title)

class TokenLevelTopicAllocation(models.Model):
    topic = models.ForeignKey(Topic)    
    document = models.ForeignKey(Document)    
    token_id = models.TextField()
    word = models.TextField()

    def __unicode__(self):
        return build_unicode(self.topic.corpus.name, self.document.title, 
                             self.topic.id, self.token_id, self.word)
