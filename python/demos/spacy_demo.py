import stanza
import spacy
from spacy.tokens import Doc, Token
from spacy import displacy

# Ensure stanza and spaCy are installed
stanza.download('en')
nlp_stanza = stanza.Pipeline('en')  # Stanza pipeline
nlp_spacy = spacy.blank("en")  # Create a blank spaCy model

# Define a helper function to convert Stanza Doc to spaCy Doc
def stanza_to_spacy(stanza_doc, nlp_spacy):
    words = [word.text for sentence in stanza_doc.sentences for word in sentence.words]
    heads = [word.head - 1 if word.head > 0 else word.id - 1 for sentence in stanza_doc.sentences for word in sentence.words]  # Convert Stanza's 1-based indexing to 0-based indexing
    deps = [word.deprel for sentence in stanza_doc.sentences for word in sentence.words]

    doc = Doc(nlp_spacy.vocab, words=words)
    for i, token in enumerate(doc):
        token.dep_ = deps[i]  # Dependency relation
        token.head = doc[heads[i]] if heads[i] != i else token  # Set the head token
    return doc

# Process sentence with Stanza
# sentence = "She loves him"
# sentence = "he loves her"
sentence = "he loves her and she loves him"
stanza_doc = nlp_stanza(sentence)

# Convert Stanza output to a spaCy Doc
spacy_doc = stanza_to_spacy(stanza_doc, nlp_spacy)

# Serve visualization on port 5005
displacy.serve(spacy_doc, style="dep", port=5005)
