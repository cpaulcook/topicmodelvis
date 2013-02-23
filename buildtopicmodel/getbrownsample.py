import argparse, nltk, os, subprocess

# A script to extract a sample of the Brown Corpus and run Mallet on
# it with 20 topics

parser = argparse.ArgumentParser()
parser.add_argument('mallet_bin', type=str,
                    help="Path to mallet")
args = parser.parse_args()

corpus_dir = 'brown_sample_corpus'
model_dir = 'brown_sample_model'

categories = ['news', 'romance']

# Create the output directory if it doesn't exist
if not os.path.exists(corpus_dir):
    os.mkdir(corpus_dir)

# Create the files for Mallet to topic model
for fname in nltk.corpus.brown.fileids(categories):
    outf = open(os.path.join(corpus_dir, fname + '.txt'), 'w')
    for word in nltk.corpus.brown.words(fname):
        print >> outf, word.encode('utf8')
    outf.close()

# Create a directory for the output of the topic modeler if it doesn't exist
if not os.path.exists(model_dir):
    os.mkdir(model_dir)

# Write a file containing genre information to the topic model output dir
genre_outf = open(os.path.join(model_dir, 'genres.txt'), 'w')
for c in categories:
    for fname in nltk.corpus.brown.fileids(c):
        print >> genre_outf, fname + '.txt', c
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
                    mallet_data_file, '--num-topics', '20', '--output-state',
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
