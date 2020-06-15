"""
For training a language model fitting for conversation, we will use OpenSubtitles dataset.
Rationale is, that the subtitles from the movies, should contain a natural feeling conversation.
This dataset was also used Vinyla et al.
As the model needs to be relatively fast, we will be using a trigram model for simplicity

References:
Vinyals, Oriol, and Quoc Le. "A neural conversational model." arXiv preprint arXiv:1506.05869 (2015).
J. Tiedemann, 2012, Parallel Data, Tools and Interfaces in OPUS. In Proceedings of the 8th International Conference on Language Resources and Evaluation (LREC 2012)
"""
import spacy
import pickle

from os import path as op
from tqdm import tqdm

datadir = op.join(op.dirname(__file__), "..", "Opensubtitles-en-da")
datafile = "OpenSubtitles.da-en.en"

nlp = spacy.load("en_core_web_sm", disable=["tagger", "parser", "ner", "textcat"])

trigram_counts = {}

with open(op.join(datadir, datafile), "r") as opensubtitles:
    for line in tqdm(opensubtitles, total=11021827):
        line = line.replace("\"", "")
        line = line.replace(" - ", " ")
        line = line.replace("\n", "")
        line = line.lower()
        
        tokens = ["<s>", "<s>"]
        tokens.extend([str(token) for token in nlp(line)])
        tokens.extend(["</s>", "</s>"])

        for i in range(2, len(tokens), 1):
            w_1, w_2, w_3 = (tokens[i-2], tokens[i-1], tokens[i])
            
            key = (w_1, w_2)
            
            if key not in trigram_counts:
                trigram_counts[key] = {}
            if w_3 not in trigram_counts[key]:
                trigram_counts[key][w_3] = 0

            trigram_counts[key][w_3] += 1
        
for key in trigram_counts:
    trigram = trigram_counts[key]
    total = float(sum(trigram.values()))
    # Convert to probabilities
    for w_3 in trigram:
        trigram[w_3] /= total

trigram_model = trigram_counts

with open("trigram_model.pickle", "wb") as model_file:
    pickle.dump(trigram_model, model_file)