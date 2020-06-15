import spacy
import json
import requests
import random
import functools
import pickle

nlp = spacy.load("en_core_web_sm")

try:
    with open("trigram_model.pickle", "rb") as language_model_file:
        language_model = pickle.load(language_model_file)
except FileNotFoundError:
    language_model = {}


with open("secrets.json", "r") as secrets:
    api_key = json.load(secrets)["TheSaurusAPI"]

pos_lookup = {"VERB": "verb", "ADJ": "adjective", "NOUN": "noun"}

class SynonymNotFound(Exception):
    pass


@functools.lru_cache(maxsize=512)
def _getSynonyms(token):

    resp = requests.get("https://words.bighugelabs.com/api/2/{}/{}/json".format(api_key, str(token)))

    return json.loads(resp.text)


def _getSynonym(token):

    try:
        pos = pos_lookup[token.pos_]
    except KeyError:
        raise SynonymNotFound()

    try:
        synonyms = _getSynonyms(token)
        pos_synonym = synonyms[pos]["syn"]
        synonym = random.choice(pos_synonym)
        return synonym
    except KeyError:
        raise SynonymNotFound()


def _changeRoot(document):

    new_text = []

    for token in document:
        if token.dep_ == "ROOT":
            synonym = _getSynonym(token)
            new_text.append(str(synonym))
        else:
            new_text.append(str(token))
    
    return " ".join(new_text)


def _changeAdjective(document):
    """
    Changes the adjectives to synonyms from the input document.
    """

    new_text = ["<s>", "<s>"]

    for token in document:
        if token.pos_ == "ADJ":

            try:
                synonyms = _getSynonyms(token)
                
                thesaurus_pos = pos_lookup["ADJ"]
                adj_synonyms = synonyms[thesaurus_pos]["syn"]

                w_1 = new_text[-2].lower()
                w_2 = new_text[-1].lower()

                lm = language_model[(w_1, w_2)]

                synonym_probas = [lm.get(w_3.lower(), 0.000001) for w_3 in adj_synonyms]

                total = sum(synonym_probas)

                synonym_probas = [proba/total for proba in synonym_probas]

                chosen_adj = random.choices(adj_synonyms, weights=synonym_probas)[0]

                new_text.append(chosen_adj)

            # Be general, so we don't get runtime problems
            except Exception:
                new_text.append(str(token))

        else:
            new_text.append(str(token))

    # Drop the <s> tokens from the start
    return " ".join(new_text[2:])



def mutateMessage(text):
    
    assert isinstance(text, str)

    document = nlp(text)

    response = _changeAdjective(document)

    return response


if __name__ == "__main__":
    mutateMessage("I am doing good")