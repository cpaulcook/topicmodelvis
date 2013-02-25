from django.db import models

def is_prob_dist(l):
    return 0.99 < sum(l) < 1.01 and all([0 < x < 1 for x in l])

def build_unicode(*l):
    return ':'.join([unicode(x) for x in l])

class Corpus(models.Model):
    name = models.TextField(unique=True)
    description = models.TextField()

    def __unicode__(self):
        return build_unicode((self.name))

class SubCorpus(models.Model):
    # **** name,corpus has to be unique, but not sure how to enforce
    # **** this in Django ****
    name = models.TextField()
    corpus = models.ForeignKey(Corpus)
    description = models.TextField()
    
    def __unicode__(self):
        return build_unicode(self.corpus.name, self.name)

    def ave_prob_topic_given_doc(self):
        documents = [x.document for x in self.subcorpuscontent_set.all()]

        topic_probs = {}
        num_docs = len(documents)
        for t in self.corpus.topic_set.all():
            probs = \
                [d.probtopicgivendoc_set.get(topic=t).prob for d in documents]
            topic_probs[t] = sum(probs) / num_docs

        assert is_prob_dist(topic_probs.values())

        return topic_probs

    def best_k_topics(self, k=10):
        topic_probs = self.ave_prob_topic_given_doc()
        sorted_topics = [x[0] for x in sorted(topic_probs.items(),
                                              key=lambda x : x[1],
                                              reverse=True)]
        return sorted_topics[:k]
            
class Topic(models.Model):
    # corpus_id,corpus_topic_id fields should be unique but Django
    # doesn't appear to have any way to enforce this.
    corpus_topic_id = models.IntegerField()
    corpus = models.ForeignKey(Corpus)

    def __unicode__(self):
        return build_unicode(self.corpus.name, self.id, self.corpus_topic_id)

    def best_k_words(self, k=10, probs=False, prob_threshold=0.001):
        '''Return the best k words for this topic. If probs is True,
        return (word,prob) tuples instead of just
        words. 

        prob_threshold is a lower bound on the probability for a word
        to be returned. Setting it higher speeds things up, but if one
        of the top-k words has probability below this threshould we'll
        miss it.'''

        salient_pwgts = \
            self.probwordgiventopic_set.filter(prob__gt=prob_threshold)
        sorted_pwgts = sorted(salient_pwgts, key=lambda x : x.prob, 
                              reverse=True)
        best_pwgts = sorted_pwgts[:k]
        if probs:
            return [(x.word,x.prob) for x in best_pwgts]
        else:
            return [x.word for x in best_pwgts]

    def best_k_documents(self, k=10):
        '''Return the top-k documents in terms of prob(t|d)'''
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
        return build_unicode(self.document.corpus.name, self.document.title, self.text[:20])

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
