import stanza

# Download and set up the English model
stanza.download('en')
nlp = stanza.Pipeline('en')

# Input sentence
sentence = "She loves him"

# Process the sentence
doc = nlp(sentence)

# Print dependency relations
print("Word\tLemma\tPOS\tHead\tRelation")
for sentence in doc.sentences:
    for word in sentence.words:
        print(f"{word.text}\t{word.lemma}\t{word.upos}\t{sentence.words[word.head - 1].text if word.head > 0 else 'ROOT'}\t{word.deprel}")

