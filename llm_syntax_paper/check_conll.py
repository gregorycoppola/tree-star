#!/usr/bin/env python3

from stanza.utils.conll import CoNLL
import argparse

def format_sentence(sentence):
    """Format a sentence (list of token dicts) as a string."""
    return ' '.join(token['text'] for token in sentence)

def main():
    parser = argparse.ArgumentParser(description="Print and validate each sentence in a CoNLL file.")
    parser.add_argument("conll_file", help="Path to the CoNLL file")
    args = parser.parse_args()

    try:
        docs = CoNLL.conll2dict(input_file=args.conll_file)
    except Exception as e:
        print(f"❌ Failed to parse file '{args.conll_file}': {e}")
        return

    total_sentences = 0

    print(f"\n✅ Successfully loaded '{args.conll_file}'\n")

    for doc_idx, doc in enumerate(docs):
        for sent_idx, sentence in enumerate(doc):
            total_sentences += 1
            print(f"Sentence {doc_idx},{sent_idx} {total_sentences}: {format_sentence(sentence)}")

    print(f"\n📝 Total sentences: {total_sentences}")

if __name__ == "__main__":
    main()
