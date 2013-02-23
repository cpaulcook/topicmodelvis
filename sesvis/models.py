from django.db import models

def build_unicode(*l):
    return ':'.join([unicode(x) for x in l])

class Corpus(models.Model):
    name = models.TextField(unique=True)
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

    def best_k_words(self, k, probs=False, prob_threshold=0.001):
        '''Return the best k words for this topic. If probs is True,
        return (word,prob) tuples instead of just
        words. 

        prob_threshold is a lower bound on the probability for a word
        to be returned. Setting it higher speeds things up, but if one
        of the top-k words has probability below this threshould we'll
        miss it.'''

        salient_pwgts = self.probwordgiventopic_set.filter(prob__gt=prob_threshold)
        sorted_pwgts = sorted(salient_pwgts, key=lambda x : x.prob, 
                              reverse=True)
        best_pwgts = sorted_pwgts[:k]
        if probs:
            return [(x.word,x.prob) for x in best_pwgts]
        else:
            return [x.word for x in best_pwgts]

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
    document = models.OneToOneField(Document)
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
