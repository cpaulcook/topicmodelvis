import argparse, nltk, os, subprocess

parser = argparse.ArgumentParser()
parser.add_argument('corpus', type=str,
                    choices=['brown', 'brown_sample', 'brown_sample2',
                             'state_of_the_union'],
                    help="Corpus to Run topic modeller on")
parser.add_argument('mallet_bin', type=str,
                    help="Path to mallet")
args = parser.parse_args()

model_dir = args.corpus + '_model'
corpus_dir = args.corpus + '_corpus'

if args.corpus == 'brown':
    nltk_corpus = nltk.corpus.brown
    num_topics = 50
    categories = nltk_corpus.categories()
    fnames = nltk_corpus.fileids()
    fnames_for_category = lambda x : nltk_corpus.fileids(x)
    encoding = 'utf8'
elif args.corpus == 'brown_sample':
    nltk_corpus = nltk.corpus.brown
    num_topics = 20
    categories = ['news', 'romance']
    fnames = nltk.corpus.brown.fileids(categories)
    fnames_for_category = lambda x : nltk_corpus.fileids(x)
    encoding = 'utf8'
elif args.corpus == 'brown_sample2':
    nltk_corpus = nltk.corpus.brown
    num_topics = 30
    categories = ['news', 'romance', 'science_fiction', 'religion']
    fnames = nltk.corpus.brown.fileids(categories)
    fnames_for_category = lambda x : nltk_corpus.fileids(x)
    encoding = 'utf8'
elif args.corpus == 'state_of_the_union':
    nltk_corpus = nltk.corpus.state_union
    num_topics = 20
    categories = set([x.split('.')[0].split('-')[1] for x in nltk_corpus.fileids()])
    fnames = nltk.corpus.state_union.fileids()
    fnames_for_category = lambda x : [f for f in fnames if x in f]
    encoding = 'latin1'

words_for_fname = lambda x : nltk_corpus.words(x)

# Create the output directory if it doesn't exist
if not os.path.exists(corpus_dir):
    os.mkdir(corpus_dir)

# Create the files for Mallet to topic model
for fname in fnames:
    if fname.endswith('.txt'):
        output_fname = fname
    else:
        output_fname = fname + '.txt'

    outf = open(os.path.join(corpus_dir, output_fname), 'w')
    for word in words_for_fname(fname):
        print >> outf, word.decode(encoding).encode('utf8'),
    outf.close()

# Create a directory for the output of the topic modeler if it doesn't exist
if not os.path.exists(model_dir):
    os.mkdir(model_dir)

# Write a file containing genre information to the topic model output dir
genre_outf = open(os.path.join(model_dir, 'genres.txt'), 'w')
for c in categories:
    for fname in fnames_for_category(c):
        if not fname.endswith('.txt'):
            fname += '.txt'
        print >> genre_outf, c, fname
genre_outf.close()

mallet_data_file = os.path.join(model_dir, 'corpus.mallet')

# Import the corpus into Mallet
mallet_import_cmd = [args.mallet_bin, 'import-dir', '--input', corpus_dir + "/", 
                 '--output', mallet_data_file, '--remove-stopwords', 
                 '--keep-sequence']
print ' '.join(mallet_import_cmd)
subprocess.call(mallet_import_cmd)

# Run Mallet
train_mallet_cmd = [args.mallet_bin, 'train-topics', '--input', 
                    mallet_data_file, '--num-topics', str(num_topics), '--output-state',
                    os.path.join(model_dir, 'state.gz'), '--output-topic-keys',
                    os.path.join(model_dir, 'topic-keys.txt'), 
                    '--topic-word-weights-file', 
                    os.path.join(model_dir, 'topic-word-weights.txt'),
                    '--word-topic-counts-file', 
                    os.path.join(model_dir, 'word-topic-counts-file.txt'),
                    '--output-doc-topics',
                    os.path.join(model_dir, 'doc-topics.txt')]
print ' '.join(train_mallet_cmd)
subprocess.call(train_mallet_cmd)
