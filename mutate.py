import spacy
import json
import requests
import random
import functools

nlp = spacy.load("en_core_web_sm")
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

    new_text = []

    for token in document:
        print(token, token.pos_, token.dep_)
        if token.pos_ == "ADJ":
            synonym = _getSynonym(token)
            new_text.append(str(synonym))
        else:
            new_text.append(str(token))

    return " ".join(new_text)



def mutateMessage(text):
    
    assert isinstance(text, str)

    document = nlp(text)

    response = _changeAdjective(document)

    return response


if __name__ == "__main__":
    mutateMessage("I am doing good")