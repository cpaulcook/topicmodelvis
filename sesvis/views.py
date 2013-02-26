# Create your views here.

from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext, loader
from django.http import HttpResponse
from sesvis.models import *
from django.contrib.auth import login, authenticate

# ***** Need to return 404s when invalid corpus, doc, etc. is passed *****

def corpora(request):
    available_corpora = sorted(Corpus.objects.all(), key=lambda x : x.name)
    return render_to_response('corpora.html', 
                              {'available_corpora': available_corpora})

def corpus(request, corpus_name):
    c = Corpus.objects.get(name=corpus_name)
    sorted_topics = sorted(c.topic_set.all(), key=lambda x : x.corpus_topic_id)
    words_for_topic = [(t, t.best_k_words()) for t in sorted_topics]
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
    sc = SubCorpus.objects.get(corpus__name=corpus_name, name=subcorpus_name)
    best_topics = sc.best_k_topics(k=5)
    words_for_topic = [(t, t.best_k_words()) for t in best_topics]

    return render_to_response('subcorpus.html', 
                              {'corpus_name': corpus_name,
                               'subcorpus_name': subcorpus_name,
                               'words_for_topic': words_for_topic})

def document(request, corpus_name, document_title):
    c = Corpus.objects.get(name=corpus_name)
    d = Document.objects.all().get(corpus__name=c, title=document_title)
    text = d.documentcontent.text
    return render_to_response('document.html', {'title': d.title,'text': text})

def compare_subcorpora(request, corpus_name):
    subcorpus_name1 = request.GET.get('subcorpus_name1')
    subcorpus_name2 = request.GET.get('subcorpus_name2')

    sc1 = SubCorpus.objects.get(corpus__name=corpus_name, 
                                name=subcorpus_name1)
    sc2 = SubCorpus.objects.get(corpus__name=corpus_name, 
                                name=subcorpus_name2)

    sc1_topic_probs = sc1.ave_prob_topic_given_doc()
    sc2_topic_probs = sc2.ave_prob_topic_given_doc()

    topic_prob_ratios = {}
    for t in sc1_topic_probs:
        topic_prob_ratios[t] = sc1_topic_probs[t] / sc2_topic_probs[t]
    
    # Num top words to display per topic
    k = 10
    def best_topic_words_helper(helper_f):
        return [(x[0],x[0].best_k_words()) for x in helper_f(k, topic_prob_ratios.items(), 
                                                             key=lambda x : x[1])]
    sc1_best_topic_words = best_topic_words_helper(heapq.nlargest)
    sc2_best_topic_words = best_topic_words_helper(heapq.nsmallest)

    return render_to_response('compare.html', {'corpus_name': corpus_name,
                                               'subcorpus_name1': subcorpus_name1,
                                               'subcorpus_name2': subcorpus_name2,
                                               'sc1_best_topic_words': sc1_best_topic_words,
                                               'sc2_best_topic_words': sc2_best_topic_words})

def search(request, corpus_name):
    search_term = request.GET.get('q')
    pwgts = ProbWordGivenTopic.objects.filter(word=search_term).filter(topic__corpus__name=corpus_name)
    num_results = 5
    best_pwgts = heapq.nlargest(num_results, pwgts, key=lambda x : x.prob)
    word_prob_topics = [(x.topic,
                         x.prob,
                         x.topic.best_k_words()) for x in best_pwgts]

    return render_to_response('search.html', {'corpus_name': corpus_name,
                                              'search_term': search_term,
                                              'word_prob_topics': word_prob_topics})
    
#def login(request):
#    uname = request.POST['username']
#    pword = request.POST['password']
#    user = authenticate(username=uname, password=pword)
#    if user is not None:
#        # We probably don't need this as we're unlikely to 
#        # de-activate users. -KG
#        if user.is_active:
#            login(request, user)
#            return render_to_response('corpora.html', "user": user)
#        else:
            
def sesvis(request):
    form = {'username': 'username',
            'uname_label': 'username: ',
            'pword_label': 'password: ',
            'password': 'password'
           } 
    
    return render_to_response('index.html', {'form':form}, 
                context_instance=RequestContext(request))
