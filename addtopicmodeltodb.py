import argparse, gzip, os, sesvis, time
from topicmodelvis import settings
from django.core.management import setup_environ
setup_environ(settings)
from sesvis.models import *
from django.db import transaction

parser = argparse.ArgumentParser()
parser.add_argument('corpus_name', type=str,
                    help="Name of corpus")
parser.add_argument('corpus_description', type=str,
                    help="Description of corpus")
parser.add_argument('corpus_dir', type=str,
                    help="Path to directory of corpus text files")
parser.add_argument('model_dir', type=str,
                    help="Path to directory of topic model for corpus")
args = parser.parse_args()

def get_model_fname(fname):
    return os.path.join(args.model_dir, fname)

def is_prob_dist(l):
    return 0.99 < sum(l) < 1.01 and all([0 < x < 1 for x in l])

def create_corpus():
    print "Creating corpus"
    c = Corpus(name=args.corpus_name, description=args.corpus_description)
    c.save()
    return c

def create_subcorpora(c, doc_to_genre):
    print "Creating sub-corpora"

    sub_corpora = {}
    for g in set(doc_to_genre.values()):
        # ***** There's not really much to describe about a genre...
        # remove this field? *****
        s = SubCorpus(name=g, corpus=c, description=g)
        s.save()
        sub_corpora[g] = s
    return sub_corpora

# This decorator and transaction.commit() make bulk inserts more
# efficient
@transaction.commit_manually
def create_topics(c):
    print "Creating topics"
    topics = {}
    for line in open(get_model_fname('topic-keys.txt')):
        topic_id = int(line.split()[0])
        my_topic = Topic(corpus=c, corpus_topic_id=topic_id)
        my_topic.save()
        topics[topic_id] = my_topic
    transaction.commit()
    return topics

# This decorator and transaction.commit() make bulk inserts more
# efficient
@transaction.commit_manually
def create_prob_word_given_topics(c,topics):
    # This function loads all the word--topic weights into
    # memory. With large corpora this might become a problem...

    print "Creating probabilities for word given topic"

    prob_word_given_topic = {}

    for t in topics:
        prob_word_given_topic[t] = {}

    # Get the weights
    for line in open(get_model_fname('topic-word-weights.txt')):
        t,word,weight = line.split()
        t = int(t)
        weight = float(weight)
        prob_word_given_topic[t][word] = weight

    # Normalise
    for t in prob_word_given_topic:
        sum_t_weights = sum(prob_word_given_topic[t].values())
        for w in prob_word_given_topic[t]:
            prob_word_given_topic[t][w] = \
                prob_word_given_topic[t][w] / sum_t_weights

    # Make sure we have probability distributions 
    for t in prob_word_given_topic:
        assert is_prob_dist(prob_word_given_topic[t].values())

    for t in prob_word_given_topic:
        for w in prob_word_given_topic[t]:
            prob = prob_word_given_topic[t][w]
            pwgt = ProbWordGivenTopic(topic=topics[t], word=w, prob=prob)
            pwgt.save()
        print "Topic:", t
        transaction.commit()

@transaction.commit_manually
def create_documents(c):
    print "Creating documents"

    documents = {}
    for f in [x for x in os.listdir(args.corpus_dir) if x.endswith('txt')]:
        d = Document(title=f, corpus=c)
        d.save()
        documents[f] = d
    transaction.commit()
    return documents

def create_document_contents(documents):
    print "Creating document contents"

    for f in [x for x in os.listdir(args.corpus_dir) if x.endswith('txt')]:
        content = open(os.path.join(args.corpus_dir, f)).read()
        dc = DocumentContent(document=documents[f], text=content)
        dc.save()

@transaction.commit_manually
def create_prob_topic_given_documents(topics, documents):
    print "Creating prob topic given documents"
    for line in open(get_model_fname('doc-topics.txt')):
        # doc-topics.txt starts with a comment line
        if line.startswith('#'):
            continue
        line = line.split()
        doc = os.path.basename(line[1])
        ts = [int(x) for x in line[2::2]]
        ps = [float(x) for x in line[3::2]]

        assert len(ts) == len(ps)
        assert is_prob_dist(ps)

        for t,p in zip(ts, ps):
            ptgd = ProbTopicGivenDoc(topic=topics[t], document=documents[doc], prob=p)
            ptgd.save()
    transaction.commit()

@transaction.commit_manually
def create_subcorpus_contents(sub_corpora, documents, doc_to_genre):
    print "Creating sub-corpus contents"
    for d in doc_to_genre:
        scc = SubCorpusContent(subcorpus=sub_corpora[doc_to_genre[d]],
                               document=documents[d])
        scc.save()
    transaction.commit()

@transaction.commit_manually
def create_token_level_topic_allocation(topics, documents):
    print "Create token-level topic allocations"
    line_counter = 0
    for line in gzip.open(get_model_fname('state.gz')):
        if line.startswith('#'):
            continue
        line_counter += 1
        line = line.split()
        doc = os.path.basename(line[1])
        token_id = int(line[2])
        word = line[4]
        topic = int(line[5])
    
        tlta = TokenLevelTopicAllocation(topic=topics[topic],
                                         document=documents[doc], 
                                         token_id=token_id, word=word)
        tlta.save()
        if line_counter % 1000 == 0:
            print line_counter
            transaction.commit()
    transaction.commit()

if __name__ == '__main__':
    start_time = time.time()

    c = create_corpus()

    # Load the genre information
    doc_to_genre = dict([x.split() for x in open(get_model_fname('genres.txt'))])

    sub_corpora = create_subcorpora(c, doc_to_genre)
    topics = create_topics(c)
    create_prob_word_given_topics(c,topics)
    documents = create_documents(c)
    create_document_contents(documents)
    create_prob_topic_given_documents(topics, documents)
    create_subcorpus_contents(sub_corpora, documents, doc_to_genre)
    create_token_level_topic_allocation(topics, documents)

    print "Time elapsed:", time.time() - start_time
