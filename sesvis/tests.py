"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from sesvis.models import *
from sesvis.views import *
from django.contrib.auth.models import User



class ModelTest(TestCase):

    def setUp(self):
        self.c = Corpus(name='try', description="try corpus")
        self.c.save()

        self.sc = SubCorpus(name='trysc', corpus=self.c, description='try sc')
        self.sc.save()

        self.sc2 = SubCorpus(name='trysc', corpus=self.c, description='try sc2')
        self.sc2.save()

        self.t = Topic(corpus=self.c, corpus_topic_id=3)
        self.t.save()
        self.t2 = Topic(corpus=self.c, corpus_topic_id=4)
        self.t2.save()
        self.t3 = Topic(corpus=self.c, corpus_topic_id=5)
        self.t3.save()

        self.pwgt = ProbWordGivenTopic(topic=self.t, word='blah', prob=0.53)
        self.pwgt.save()
        ProbWordGivenTopic(topic=self.t, word='hannah', prob=0.82).save()
        ProbWordGivenTopic(topic=self.t, word='bananas', prob=0.12).save()

        self.d = Document(title="mydoc", corpus=self.c)
        self.d.save()
        self.d2 = Document(title="mydoc2", corpus=self.c)
        self.d2.save()
        self.d3 = Document(title="mydoc3", corpus=self.c)
        self.d3.save()

        self.doc_content = DocumentContent(document=self.d, 
                                           text="This is the content of a document...")
        self.doc_content.save()
        
        self.ptgd = ProbTopicGivenDoc(topic=self.t, document=self.d, prob=0.1)
        self.ptgd.save()
        ProbTopicGivenDoc(topic=self.t2, document=self.d, prob=0.7).save()
        ProbTopicGivenDoc(topic=self.t3, document=self.d, prob=0.2).save()
        ProbTopicGivenDoc(topic=self.t, document=self.d2, prob=0.2).save()
        ProbTopicGivenDoc(topic=self.t2, document=self.d2, prob=0.3).save()
        ProbTopicGivenDoc(topic=self.t3, document=self.d2, prob=0.5).save()

        ProbTopicGivenDoc(topic=self.t, document=self.d3, prob=0.1).save()
        ProbTopicGivenDoc(topic=self.t2, document=self.d3, prob=0.5).save()
        ProbTopicGivenDoc(topic=self.t3, document=self.d3, prob=0.4).save()

        self.scc = SubCorpusContent(subcorpus=self.sc, document=self.d)
        self.scc.save()
        SubCorpusContent(subcorpus=self.sc2, document=self.d).save()
        SubCorpusContent(subcorpus=self.sc2, document=self.d2).save()

        self.tlta = TokenLevelTopicAllocation(topic=self.t, document=self.d, token_id=57, 
                                     word='testsareawesome')
        self.tlta.save()

    def test_is_prob_dist_prob(self):
        self.assertTrue(is_prob_dist([0.5, 0.5]))

    def test_is_prob_dist_not_prob_dist(self):
        self.assertFalse(is_prob_dist([0.5, 0.6]))

    def test_is_prob_dist_item_not_prob(self):
        self.assertFalse(is_prob_dist([0.5, 1.1]))

    def test_build_unicode(self):
        assert build_unicode('a','b','c') == u'a:b:c'

    def test_get_subcorpus_access(self):
        # Need to test this function
        assert False

    def test_corpus_unicode(self):
        assert unicode(self.c) == u'try'

    def test_subcorpus_unicode(self):
        assert unicode(self.sc) == u'try:trysc'

    def test_subcorpus_ave_prob_topic_given_doc_1(self):
        assert self.sc.ave_prob_topic_given_doc() == {self.t:0.1, self.t2:0.7,
                                                      self.t3:0.2}

    def test_subcorpus_ave_prob_topic_given_doc_2(self):
        result =  self.sc2.ave_prob_topic_given_doc()
        expected = {self.t:0.15, self.t2:0.5, self.t3:0.35}
        for t in expected:
            self.assertAlmostEqual(expected[t], result[t])

    def test_subcorpus_best_k_topics(self):
        assert self.sc2.best_k_topics(k=2) == [self.t2, self.t3]

    def test_topic_unicode(self):
        assert unicode(self.t) == u'try:1:3'

    def test_topic_best_k_words(self):
        assert self.t.best_k_words(k=2) == ['hannah', 'blah']

    def test_topic_best_k_words_probs(self):
        assert self.t.best_k_words(k=2, 
                                   probs=True) == [('hannah',0.82), 
                                                   ('blah',0.53)]

    def test_topic_best_k_documents(self):
        assert self.t3.best_k_documents(k=2) == [self.d2, self.d3]

    def test_probwordgiventopic_unicode(self):
        assert unicode(self.pwgt) == u'try:1:blah'
        
    def test_document_unicode(self):
        assert unicode(self.d) == u'try:mydoc'

    def test_document_content_unicode(self):
        assert unicode(self.doc_content) == u'try:mydoc:This is the content '

    def test_probtopicgivendoc_unicode(self):
        assert unicode(self.ptgd) == u'try:mydoc:1'
    
    def test_subcorpuscontent_unicode(self):
        assert unicode(self.scc) == u'try:trysc:mydoc'

    def test_tokenleveltopicallocation_unicode(self):
        assert unicode(self.tlta) == u'try:mydoc:1:57:testsareawesome'

class ViewTest(TestCase):
    
    def setUp(self):
        user = self.client.login(username='fakeuser', password='fakepasswd')

    def test_corpora_nologin(self):
        resp = self.client.get('/corpora/')
        self.assertEqual(resp.status_code, 302)        

    def test_corpora_login(self):
        User.objects.create_user('fakeuser', 'fake@email.com', 'fakepasswd')
        user = self.client.login(username='fakeuser', password='fakepasswd')
        resp = self.client.get('/corpora/')
        print resp
        self.assertEqual(resp.status_code, 200)

    
