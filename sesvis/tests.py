"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from sesvis.models import *

class SimpleTest(TestCase):
    c = Corpus(name='try', description="try corpus")
    sc = SubCorpus(name='trysc', corpus=c, description='try sc')
    t = Topic(corpus=c)
    pwgt = ProbWordGivenTopic(topic=t, word='blah', prob=0.53)
    d = Document(title="mydoc", corpus=c)
    doc_content = DocumentContent(document=d, 
                                  text="This is the content of a document...")
    ptgd = ProbTopicGivenDoc(topic=t, document=d, prob=0.67)
    scc = SubCorpusContent(subcorpus=sc, document=d)
    tlta = TokenLevelTopicAllocation(topic=t, document=d, token_id=57, 
                                     word='testsareawesome')

    def test_basic_addition(self):
        """
        Tests that 1 + 1 always equals 2.
        """
        self.assertEqual(1 + 1, 2)

    def test_create_corpus(self):
        assert unicode(SimpleTest.c) == u'try'

    def test_create_subcorpus(self):
        assert unicode(SimpleTest.sc) == u'try:trysc'

    def test_create_topic(self):
        assert unicode(SimpleTest.t) == u'try:None'

    def test_create_probwordgiventopic(self):
        assert unicode(SimpleTest.pwgt) == u'try:None:blah'
        
    def test_document(self):
        assert unicode(SimpleTest.d) == u'try:mydoc'

    def test_document_content(self):
        assert unicode(SimpleTest.doc_content) == u'try:mydoc:This is the content '

    def test_probtopicgivendoc(self):
        assert unicode(SimpleTest.ptgd) == u'try:mydoc:None'
    
    def test_subcorpuscontent(self):
        assert unicode(SimpleTest.scc) == u'try:trysc:mydoc'

    def test_tokenleveltopicallocation(self):
        assert unicode(SimpleTest.tlta) == u'try:mydoc:None:57:testsareawesome'
