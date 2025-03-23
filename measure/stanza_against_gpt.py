import json
import stanza

# Initialize the English pipeline
stanza.download('en')  # only the first time
nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse')

def find_head_token(phrase_tokens, sentence_tokens):
    # Return the head word in the dependency parse for the phrase tokens
    token_ids = [t.id for t in sentence_tokens if t.text in phrase_tokens]
    heads = [t.head for t in sentence_tokens if t.id in token_ids]
    head_id = max(set(heads), key=heads.count)  # most common head
    for t in sentence_tokens:
        if t.id == head_id:
            return t.text
    return None

def evaluate(filepath):
    with open(filepath) as f:
        examples = json.load(f)

    total = len(examples)
    correct = 0

    for item in examples:
        doc = nlp(item["sentence"])
        sentence = doc.sentences[0]

        phrase_words = item["ambiguous_phrase"].split()
        predicted_head = find_head_token(phrase_words, sentence.words)
        expected_head = item["correct_attachment"]

        print(f"Sentence: {item['sentence']}")
        print(f"→ Phrase: '{item['ambiguous_phrase']}' → predicted head: '{predicted_head}', expected: '{expected_head}'\n")

        if predicted_head.lower() == expected_head.lower():
            correct += 1

    print(f"\nAccuracy: {correct}/{total} = {correct/total:.2%}")

evaluate("data.json")
