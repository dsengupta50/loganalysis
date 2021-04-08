import numpy as np
import json
import os
from keras.layers.embeddings import Embedding

import logutils

# the glove vector file to load, this has <x>d.txt where d is the number of features
my_glove_file = 'glove/glove.6B.50d.txt'

def find_max_len(X):
    '''
        This method finds the maximum length of a sentence in all the input examples (NOT USED in the program as I eventually hardcoded it to a smaller number than 455 that was an outlier)
    '''
    m = X.shape[0]
    max_len = 0
    for i in range(m):
        length = len(X[i].split())
        if length > max_len:
            max_len = length

    #print("MAX LENGTH is " + str(max_len))
    return max_len

# Read the glove vectors from a pretrained glove file
def read_glove_vecs(glove_file):
    '''
        This method reads the word vector files and prepares them for the embedding matrix and transforming sentences into vectors.
    '''
    with open(glove_file, 'r') as f:
        words = set()
        word_to_vec_map = {}
        for line in f:
            line = line.strip().split()
            curr_word = line[0]
            words.add(curr_word)
            word_to_vec_map[curr_word] = np.array(line[1:], dtype=np.float64)
        
        i = 1
        words_to_index = {}
        index_to_words = {}
        for w in sorted(words):
            words_to_index[w] = i
            index_to_words[i] = w
            i = i + 1

    return words_to_index, index_to_words, word_to_vec_map

# read the embedding matrix
word_to_index, index_to_word, word_to_vec_map = read_glove_vecs(my_glove_file)

# This function returns the index of the word in the glove dictionary
def get_word_value(map, word):
    if word in map:
        return map.get(word)

    return map.get('unknown') 

'''
This function pre-processes the input text before training and prediction.
The following steps were taken
    1. Remove URLs
    2. Replace any text emoticons like :-) or :( with word equivalents
    3. Remove punctuations from the text
    4. Remove words that are not in the glove dictionary
    5. Lemmatization by replacing words to its base root word
'''
def sanitize_sentence(sentence):
    words = sentence.split()

    # remove words not in the dictionary
    words = [w for w in words if w.lower() in word_to_index]
    sentence = ' '.join(words)

    return sentence


# Converts an array of sentences (strings) into an array of indices corresponding to words in the sentences.
def sentences_to_indices(X, word_to_index, max_len):
    """
    Converts an array of sentences (strings) into an array of indices corresponding to words in the sentences.
    
    Arguments:
    X -- array of sentences (strings), of shape (m, 1)
    word_to_index -- a dictionary containing the each word mapped to its index
    max_len -- maximum number of words in a sentence. You can assume every sentence in X is no longer than this. 
    
    Returns:
    X_indices -- array of indices corresponding to words in the sentences from X, of shape (m, max_len)
    """
    
    m = X.shape[0] # number of training examples
    
    # Initialize X_indices as a numpy matrix of zeros and the correct shape
    X_indices = np.zeros([m, max_len])
    
    for i in range(m):  # loop over training examples
        
        # Convert the ith training sentence in lower case and split is into words. You should get a list of words.
        sentence_words = X[i].lower().split()
        
        j = 0
        
        # Loop over the words of sentence_words
        for w in sentence_words[:max_len-1]:
            # Set the (i,j)th entry of X_indices to the index of the correct word.
            X_indices[i, j] = get_word_value(word_to_index, w)
            #print(w + " is " + str(X_indices[i,j]))
            j = j+1
                
    return X_indices

def get_logs_from_json(filename):
    messages = []
    f = open(filename, 'r')
    json_data = json.load(f)
    for obj in json_data:
        messages.append(obj['message'])

    return np.asarray(messages)


def pretrained_embedding_layer(word_to_vec_map, word_to_index):
    """
    Creates a Keras Embedding() layer and loads in pre-trained GloVe 300-dimensional vectors.
    
    Arguments:
    word_to_vec_map -- dictionary mapping words to their GloVe vector representation.
    word_to_index -- dictionary mapping from words to their indices in the vocabulary (400,001 words)

    Returns:
    embedding_layer -- pretrained layer Keras instance
    """
    
    vocab_len = len(word_to_index) + 1                  # adding 1 to fit Keras embedding (requirement)
    emb_dim = word_to_vec_map["cucumber"].shape[0]      # define dimensionality of your GloVe word vectors (= 50)
    
    # Step 1
    # Initialize the embedding matrix as a numpy array of zeros.
    emb_matrix = np.zeros([vocab_len, emb_dim])
    
    # Step 2
    # Set each row "idx" of the embedding matrix to be 
    # the word vector representation of the idx'th word of the vocabulary
    for word, idx in word_to_index.items():
        emb_matrix[idx, :] = get_word_value(word_to_vec_map, word)

    # Step 3
    # Define Keras embedding layer with the correct input and output sizes
    # Make it non-trainable.
    embedding_layer = Embedding(vocab_len, emb_dim, trainable=False)

    # Step 4
    # Build the embedding layer, it is required before setting the weights of the embedding layer. 
    embedding_layer.build((None,))
    
    # Set the weights of the embedding layer to the embedding matrix. Your layer is now pretrained.
    embedding_layer.set_weights([emb_matrix])
    
    return embedding_layer

def get_data(folder):
    max_len = 20
    X_data = np.empty([0, max_len])
    X_all = []
    for f in os.listdir(folder):
        if f.startswith("."):
            continue

        X = get_logs_from_json(folder + "/" + f)
        X_all = np.append(X_all, X)
        X_log = sentences_to_indices(X, word_to_index, max_len)
        X_data = np.insert(X_data, X_data.shape[0], X_log, axis=0)
        #print(str(X_data.shape) + ":" + str(X_log.shape))

    #print(f + ":" + str(X_all.shape))
    #print(X_all[1])
    return X_data, X_all    

def main():
    print("Hello feature extraction")

    #print(word_to_vec_map["cucumber"])
    #print(word_to_vec_map["cucumber"].shape)
    #print(len(word_to_vec_map.keys()))

    #message = "Created a fabric task to update agents on a pool/Image. pool_id: *, image_id: null, poolOrPatternName: *, agent_name: [HAI-Agent], agent_id: [*]"
    X = get_data()
    print(type(X[0]))

# Start program
if __name__ == "__main__":
    main()
