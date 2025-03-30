#!/usr/bin/env python3

from stanza.utils.conll import CoNLL
import argparse
from typing import List, Dict

def load_conll_file(file_path: str):
    """Load a CoNLL file and return a list of documents."""
    return CoNLL.conll2dict(input_file=file_path)

def format_sentence(sentence: List[Dict]) -> str:
    """Format a sentence as plain text."""
    return ' '.join(token['text'] for token in sentence)

def save_sentence(sentence: List[Dict], output_file):
    """Save a sentence in CoNLL-U format."""
    for token in sentence:
        fields = [
            str(token['id']).strip('(),'),
            token['text'],
            token.get('lemma', token.get('Lemma', '_')),
            token.get('upos', token.get('UPOS', '_')),
            token.get('xpos', token.get('XPOS', '_')),
            token.get('feats', token.get('Feats', '_')),
            str(token['head']).strip('(),'),
            token.get('deprel', token.get('Deprel', '_')),
            token.get('deps', token.get('Deps', '_')),
            token.get('misc', token.get('Misc', '_'))
        ]
        output_file.write('\t'.join(fields) + '\n')
    output_file.write('\n')

def is_valid_sentence(sentence: List[Dict]) -> bool:
    """Check that all required fields are present in all tokens."""
    required_fields = ['id', 'text', 'head', 'deprel']
    return all(isinstance(tok, dict) and all(f in tok for f in required_fields) for tok in sentence)

def main():
    parser = argparse.ArgumentParser(description='Interactively select sentences from a CoNLL file.')
    parser.add_argument("input_file", help="Path to input .conllu file")
    parser.add_argument("output_file", help="Path to output .conllu file")
    parser.add_argument("num_examples", type=int, help="Number of interesting examples to collect")
    args = parser.parse_args()

    docs = load_conll_file(args.input_file)
    total_sentences = 0
    saved_sentences = 0

    with open(args.output_file, 'w') as out_f:
        for doc in docs:
            for sentence in doc:
                total_sentences += 1
                
                if not is_valid_sentence(sentence):
                    print(f"⚠️ Skipping malformed sentence {total_sentences}")
                    continue
                    
                print("\n" * 2)
                print(f"Sentence {total_sentences}:")
                print(format_sentence(sentence))
                print()


                while True:
                    response = input("Is this interesting? (y/n): ").strip().lower()
                    if response in ['y', 'n']:
                        break
                    print("Please answer 'y' or 'n'.")

                if response == 'y':
                    save_sentence(sentence, out_f)
                    saved_sentences += 1
                    print(f"✅ Saved ({saved_sentences}/{args.num_examples})")
                else:
                    print("⏩ Skipped.")

                if saved_sentences >= args.num_examples:
                    print(f"\n🎉 Done! Collected {saved_sentences} examples.")
                    return

        print(f"\n⚠️ Reached end of file. Only saved {saved_sentences} examples.")

if __name__ == "__main__":
    main()

