from django.db import models
import heapq
from django.contrib.auth.models import User
from django.conf import settings

def is_prob_dist(l):
    """
    Returns True if the list l is a probability distribution, and
    False otherwise.
    """
    return 0.99 < sum(l) < 1.01 and all([0 < x < 1 for x in l])

def build_unicode(*l):
    return ':'.join([unicode(x) for x in l])

def get_subcorpus_access(uname, corpus_name):
    """
    Returns the list of sub-corpora the user has access to, 
    given the current corpus.
    """
    u = User.objects.get_by_natural_key(uname)
    sc = SubCorpus.objects.get_query_set(users=u)
    return filter(lambda x: x.corpus.name == corpus_name, sc)

class Corpus(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField()

    def __unicode__(self):
        return build_unicode((self.name))

class SubCorpus(models.Model):
    name = models.TextField()
    corpus = models.ForeignKey(Corpus)
    description = models.TextField()
    users = models.ManyToManyField(User)
    
    def __unicode__(self):
        return build_unicode(self.corpus.name, self.name)

    def ave_prob_topic_given_doc(self):
        """
        Returns p(topic|doc) averaged over all documents in SubCorpus.
        """

        documents = [x.document for x in self.subcorpuscontent_set.all()]

        topic_probs = {}
        num_docs = len(documents)
        for t in self.corpus.topic_set.all():
            probs = \
                [d.probtopicgivendoc_set.get(topic=t).prob for d in documents]
            topic_probs[t] = sum(probs) / num_docs
        
        if settings.DEBUG:
            assert is_prob_dist(topic_probs.values())

        return topic_probs

    def best_k_topics(self, k=10):
        """
        Returns the best k topics for this SubCorpus.
        """

        topic_probs = self.ave_prob_topic_given_doc()
        best_topic_probs = heapq.nlargest(k, topic_probs.items(), 
                                          key=lambda x : x[1])
        return [x[0] for x in best_topic_probs]
            
class Topic(models.Model):
    corpus_topic_id = models.IntegerField()
    corpus = models.ForeignKey(Corpus)

    def __unicode__(self):
        return build_unicode(self.corpus.name, self.id, self.corpus_topic_id)

    def best_k_words(self, k=10, probs=False):
        '''
        Returns the best k words for this topic. If probs is True
        return (word,prob) tuples for the best k words.
        '''

        best_pwgts = heapq.nlargest(k, self.probwordgiventopic_set.all(),
                                    key=lambda x : x.prob)

        if probs:
            return [(x.word,x.prob) for x in best_pwgts]
        else:
            return [x.word for x in best_pwgts]

    def best_k_documents(self, k=10):
        '''
        Returns the best k documents in terms of prob(t|d)
        '''
        return [x.document for x in sorted(self.probtopicgivendoc_set.all(), 
                                           key=lambda x : x.prob, 
                                           reverse=True)[:k]]

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
        return build_unicode(self.document.corpus.name, 
                             self.document.title, self.text[:20])

class ProbTopicGivenDoc(models.Model):
    topic = models.ForeignKey(Topic, db_index=True)
    document = models.ForeignKey(Document, db_index=True)
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
