"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from sesvis.models import *

class SimpleTest(TestCase):

    def setUp(self):
        self.c = Corpus(name='try', description="try corpus")
        self.c.save()

        self.sc = SubCorpus(name='trysc', corpus=self.c, description='try sc')
        self.sc.save()

        self.t = Topic(corpus=self.c, corpus_topic_id=3)
        self.t.save()

        self.pwgt = ProbWordGivenTopic(topic=self.t, word='blah', prob=0.53)
        self.pwgt.save()

        self.pwgta = ProbWordGivenTopic(topic=self.t, word='hannah', prob=0.82)
        self.pwgta.save()
        self.pwgtb = ProbWordGivenTopic(topic=self.t, word='bananas', prob=0.12)
        self.pwgtb.save()

        self.d = Document(title="mydoc", corpus=self.c)
        self.d.save()

        self.doc_content = DocumentContent(document=self.d, 
                                           text="This is the content of a document...")
        self.doc_content.save()
        
        self.ptgd = ProbTopicGivenDoc(topic=self.t, document=self.d, prob=0.67)
        self.ptgd.save()

        self.scc = SubCorpusContent(subcorpus=self.sc, document=self.d)
        self.scc.save()

        self.tlta = TokenLevelTopicAllocation(topic=self.t, document=self.d, token_id=57, 
                                     word='testsareawesome')
        self.tlta.save()


    def test_create_corpus(self):
        assert unicode(self.c) == u'try'

    def test_create_subcorpus(self):
        assert unicode(self.sc) == u'try:trysc'

    def test_create_topic(self):
        assert unicode(self.t) == u'try:1:3'

    def test_create_probwordgiventopic(self):
        assert unicode(self.pwgt) == u'try:1:blah'
        
    def test_document(self):
        assert unicode(self.d) == u'try:mydoc'

    def test_document_content(self):
        assert unicode(self.doc_content) == u'try:mydoc:This is the content '

    def test_probtopicgivendoc(self):
        assert unicode(self.ptgd) == u'try:mydoc:1'
    
    def test_probtopicgivendoc_best_k_words(self):
        assert self.t.best_k_words(k=2) == ['hannah', 'blah']

    def test_probtopicgivendoc_best_k_words_probs(self):
        assert self.t.best_k_words(k=2, probs=True) == [('hannah',0.82), ('blah',0.53)]

    def test_subcorpuscontent(self):
        assert unicode(self.scc) == u'try:trysc:mydoc'

    def test_tokenleveltopicallocation(self):
        assert unicode(self.tlta) == u'try:mydoc:1:57:testsareawesome'
