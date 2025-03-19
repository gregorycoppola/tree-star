import stanza
from stanza.utils.conll import CoNLL
import sys

def read_conll_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as file:
        conll_str = file.read()
    sentences = CoNLL.conll2dict(input_str=conll_str)
    return sentences

def parse_sentences(nlp, sentences):
    parsed_sentences = []
    for sentence in sentences:
        print('====================================================================================================')
        print('sentence')
        print('----------------------------------------------------------------------------------------------------')
        print(sentence)
        print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++')
        print('sentence type')
        print('....................................................................................................')
        print(type(sentence))
        tokens = sentence[0]['tokens']  # CORRECT ACCESS
        words = [token['text'] for token in tokens]
        doc = nlp(' '.join(words))
        conll_sentence = CoNLL.convert_dict(doc.to_dict())
        parsed_sentences.extend(conll_sentence)
    return parsed_sentences

def compare_parses(gold_sentences, predicted_sentences):
    total, correct_heads, correct_deprels = 0, 0, 0

    for gold_sent, pred_sent in zip(gold_sentences, predicted_sentences):
        for gold_word, pred_word in zip(gold_sent, pred_sent):
            total += 1
            if gold_word['head'] == pred_word['head']:
                correct_heads += 1
                if gold_word['deprel'] == pred_word['deprel']:
                    correct_deprels += 1

    head_acc = correct_heads / total if total else 0
    label_acc = correct_deprels / total if total else 0
    return head_acc, label_acc

def main(conll_filepath):
    print(f"Reading CoNLL file from: {conll_filepath}")
    gold_sentences = read_conll_file(conll_filepath)

    print("Initializing stanza pipeline...")
    nlp = stanza.Pipeline('en', processors='tokenize,pos,lemma,depparse')

    print("Parsing sentences...")
    predicted_sentences = parse_sentences(nlp, gold_sentences)

    print("Comparing parses...")
    head_acc, label_acc = compare_parses(gold_sentences, predicted_sentences)

    print(f"Head accuracy: {head_acc:.2%}")
    print(f"Head + Label accuracy: {label_acc:.2%}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <gold_standard.conllu>")
        sys.exit(1)

    main(sys.argv[1])
