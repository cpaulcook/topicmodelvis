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
    # documents = sorted(Document.objects.filter(corpus__name=c), 
    #                    key=lambda x : x.title)
    words_for_topic={}
    for t in c.topic_set.all():
        words_for_topic[t] = t.best_k_words(k=10)

    return render_to_response('corpus.html', {'corpus': c,
                                              'words_for_topic': words_for_topic})

def topic(request, corpus_name, topic_id):
    # ***** Working here. Need to add a topic_id to Topic *****
    pass

def document(request, corpus_name, document_title):
    c = Corpus.objects.get(name=corpus_name)
    d = Document.objects.all().get(corpus__name=c,title=document_title)
    text = d.documentcontent.text
    return render_to_response('document.html', {'title': d.title,'text': text})

