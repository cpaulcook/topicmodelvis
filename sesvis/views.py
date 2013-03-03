from django.shortcuts import render_to_response, get_object_or_404, get_list_or_404
from django.template import RequestContext, loader
from django.http import HttpResponseRedirect, Http404
from sesvis.models import *
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth import logout

def corpora(request):
    if not request.user.is_authenticated():
        return redirect_to_login(request.path, login_url='/login/') 
    available_corpora = sorted(Corpus.objects.all(), key=lambda x : x.name)
    return render_to_response('corpora.html', 
                {'available_corpora': available_corpora})

def corpus(request, corpus_name):
    if not request.user.is_authenticated():
        return redirect_to_login(request.path, login_url='/login/') 
    c = get_object_or_404(Corpus, name=corpus_name)
    sorted_topics = sorted(c.topic_set.all(), key=lambda x : x.corpus_topic_id)
    words_for_topic = [(t, t.best_k_words()) for t in sorted_topics]
    subcorpus_names = [x.name for x in c.subcorpus_set.all()]
    # Once we populate the right tables, this code should manage access.
    # u = User.objects.get_by_natural_key(request.user.username)
    # accessible = set(c.subcorpus_set.all()).intersection(set(u.subcorpus_set.all())

    return render_to_response('corpus.html', 
                              {'corpus': c, 
                               'words_for_topic': words_for_topic,
                               'subcorpus_names':subcorpus_names})

def topic(request, corpus_name, corpus_topic_id):
    if not request.user.is_authenticated():
        return redirect_to_login(request.path, login_url='/login/')
    t = get_object_or_404(Topic, corpus__name=corpus_name,
                          corpus_topic_id=corpus_topic_id)
    best_words = t.best_k_words()
    best_documents = [x.title for x in t.best_k_documents()]

    return render_to_response('topic.html', 
                              {'corpus_name': corpus_name,
                               'corpus_topic_id': corpus_topic_id,
                               'best_words': best_words,
                               'best_documents': best_documents})

def subcorpus(request, corpus_name, subcorpus_name):
    if not request.user.is_authenticated():
        return redirect_to_login(request.path, login_url='/login/')
    sc = get_object_or_404(SubCorpus, corpus__name=corpus_name,
                           name=subcorpus_name)
    best_topics = sc.best_k_topics(k=5)
    words_for_topic = [(t, t.best_k_words()) for t in best_topics]

    return render_to_response('subcorpus.html', 
                              {'corpus_name': corpus_name,
                               'subcorpus_name': subcorpus_name,
                               'words_for_topic': words_for_topic})

def document(request, corpus_name, document_title):
    if not request.user.is_authenticated():
        return redirect_to_login(request.path, login_url='/login/')
    d = get_object_or_404(Document, corpus__name=corpus_name, 
                          title=document_title)
    text = d.documentcontent.text
    return render_to_response('document.html', {'title': d.title,'text': text})

def compare_subcorpora(request, corpus_name):
    if not request.user.is_authenticated():
        return redirect_to_login(request.path, login_url='/login/')
    subcorpus_name1 = request.GET.get('subcorpus_name1')
    subcorpus_name2 = request.GET.get('subcorpus_name2')

    sc1 = get_object_or_404(SubCorpus, corpus__name=corpus_name, 
                            name=subcorpus_name1)
    sc2 = get_object_or_404(SubCorpus, corpus__name=corpus_name, 
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
    if not request.user.is_authenticated():
        return redirect_to_login(request.path, login_url='/login/')
    if request.method != 'GET' or 'q' not in request.GET:
        raise Http404
    search_term = request.GET.get('q')

    # Make sure corpus is valid.
    get_object_or_404(Corpus, name=corpus_name)
    
    pwgts = ProbWordGivenTopic.objects.all().filter(topic__corpus__name=corpus_name, 
                                                    word=search_term)
    num_results = 5
    best_pwgts = heapq.nlargest(num_results, pwgts, key=lambda x : x.prob)
    word_prob_topics = [(x.topic,
                         x.prob,
                         x.topic.best_k_words()) for x in best_pwgts]

    return render_to_response('search.html', {'corpus_name': corpus_name,
                                              'search_term': search_term,
                                              'word_prob_topics': word_prob_topics})
    
def outlog(request):
    logout(request)
    return HttpResponseRedirect('/sesvis/')
            
def sesvis(request):
    return render_to_response('index.html', 
                    context_instance=RequestContext(request))
