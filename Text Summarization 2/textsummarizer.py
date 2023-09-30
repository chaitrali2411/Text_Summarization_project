#Importing required libraries
import nltk
from nltk.corpus import stopwords
from nltk.cluster.util import cosine_distance
from nltk.tokenize import sent_tokenize
import numpy as np
import networkx as nx
import re
import string

#fucntion to remove "[i]" from the text
def remove_index_from_paragraph(paragraph):
    pattern = r"\[\d+\]"
    updated_paragraph = re.sub(pattern, "", paragraph)
    return updated_paragraph

#Function to split text into sentences by fullstop(.)

#Read the text and tokenize into sentences
def read_article(text): 
    sentences =[]
    text = remove_index_from_paragraph(text)
    sentences = sent_tokenize(text)
    for sentence in sentences:
        sentence.replace("[^a-zA-Z0-9]"," ")
    return sentences

import re

'''def read_article(text):
    sentences = sent_tokenize(text)
    for i in range(len(sentences)):
        # Remove content like [0], [1], etc.
        sentences[i] = re.sub(r'\[[0-9]+\]', '', sentences[i])
        sentences[i] = re.sub(r'\s+', ' ', sentences[i])
        sentences[i] = sentences[i].strip()
    return sentences'''

    

# Create vectors and calculate cosine similarity b/w two sentences
def sentence_similarity(sent1,sent2,stopwords=None):
    if stopwords is None:
        stopwords = []
    
    sent1 = [w.lower() for w in sent1]
    sent2 = [w.lower() for w in sent2]
    
    all_words = list(set(sent1 + sent2))
    
    vector1 = [0] * len(all_words)
    vector2 = [0] * len(all_words)
    
    #build the vector for the first sentence
    for w in sent1:
        if not w in stopwords:
            vector1[all_words.index(w)]+=1
    
    #build the vector for the second sentence
    for w in sent2:
        if not w in stopwords:
            vector2[all_words.index(w)]+=1
            
    return 1-cosine_distance(vector1,vector2)

# Create similarity matrix among all sentences
def build_similarity_matrix(sentences,stop_words):
    #create an empty similarity matrix
    similarity_matrix = np.zeros((len(sentences),len(sentences)))
    
    for idx1 in range(len(sentences)):
        for idx2 in range(len(sentences)):
            if idx1!=idx2:
                similarity_matrix[idx1][idx2] = sentence_similarity(sentences[idx1],sentences[idx2],stop_words)
                
    return similarity_matrix


# Generate and return text summary
import random

def generate_summary(text, top_n):
    nltk.download('stopwords')
    nltk.download('punkt')
    
    stop_words = stopwords.words('english')
    summarize_text = []
    
    # Step 1: read text and tokenize
    sentences = read_article(text)
    
    # Step 2: generate similarity matrix across sentences
    sentence_similarity_matrix = build_similarity_matrix(sentences, stop_words)
    
    # Step 3: Rank sentences in similarity matrix
    sentence_similarity_graph = nx.from_numpy_array(sentence_similarity_matrix)
    scores = nx.pagerank(sentence_similarity_graph)
    
    # Step 4: sort the rank and place top sentences
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    
    # Step 5: randomly select n sentences from the top-ranked sentences
    random.shuffle(ranked_sentences)
    selected_sentences = ranked_sentences[:top_n]
    
    # Step 6: get the selected sentences in their original order
    selected_sentences = sorted(selected_sentences, key=lambda x: sentences.index(x[1]))
    
    # Step 7: output the summarized version
    for _, sentence in selected_sentences:
        summarize_text.append(sentence)
    
    return " ".join(summarize_text), len(sentences)


def summarize_text(text):
  # Extractive Model
  sentence_list = nltk.sent_tokenize(text)
  stopwords = nltk.corpus.stopwords.words('english')

  word_frequencies = {}
  for word in nltk.word_tokenize(text):
    if word not in stopwords:
        if word not in word_frequencies.keys():
            word_frequencies[word] = 1
        else:
            word_frequencies[word] += 1

  maximum_frequncy = max(word_frequencies.values())

  for word in word_frequencies.keys():
        word_frequencies[word] = (word_frequencies[word]/maximum_frequncy)

  #Sentence Scoring
  sentence_scores = {}
  for sent in sentence_list:
      for word in nltk.word_tokenize(sent.lower()):
        if word in word_frequencies.keys():
            if len(sent.split(' ')) < 30:
                if sent not in sentence_scores.keys():
                    sentence_scores[sent] = word_frequencies[word]
                else:
                    sentence_scores[sent] += word_frequencies[word]

  #Abstractive Model
  summarization_sentences = []
  sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
  for sentence in sorted_sentences:
    summarization_sentences.append(sentence[0])
  summarization1 = ' '.join(summarization_sentences[:3])
  summarization = summarization1.translate(str.maketrans('', '', string.punctuation))

  print(summarization)

  return summarization



