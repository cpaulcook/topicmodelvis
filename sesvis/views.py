# Create your views here.

from django.shortcuts import render_to_response, get_object_or_404
from django.template import Context, loader
from django.http import HttpResponse
from sesvis.models import *

def corpora(request):
    available_corpora = sorted(Corpus.objects.all(), key=lambda x : x.name)
    t = loader.get_template('corpora.html')
    c = Context({
            'available_corpora': available_corpora,
    })
    return HttpResponse(t.render(c))

def corpus(request, corpus_name):
    c = Corpus.objects.get(name=corpus_name)
    words_for_topic={}
    for t in c.topic_set.all():
        words_for_topic[t] = t.best_k_words()
    subcorpus_names = [x.name for x in c.subcorpus_set.all()]

    return render_to_response('corpus.html', 
                              {'corpus': c, 
                               'words_for_topic': words_for_topic,
                               'subcorpus_names':subcorpus_names})

def topic(request, corpus_name, corpus_topic_id):
    t = Topic.objects.get(corpus__name=corpus_name,
                          corpus_topic_id=corpus_topic_id)
    best_words = t.best_k_words()
    best_documents = [x.title for x in t.best_k_documents()]

    return render_to_response('topic.html', 
                              {'corpus_name': corpus_name,
                               'corpus_topic_id': corpus_topic_id,
                               'best_words': best_words,
                               'best_documents': best_documents})

def subcorpus(request, corpus_name, subcorpus_name):
    return render_to_response('subcorpus.html', 
                              {'corpus_name': corpus_name,
                               'subcorpus_name': subcorpus_name})


def document(request, corpus_name, document_title):
    c = Corpus.objects.get(name=corpus_name)
    d = Document.objects.all().get(corpus__name=c,title=document_title)
    text = d.documentcontent.text
    return render_to_response('document.html', {'title': d.title,'text': text})

