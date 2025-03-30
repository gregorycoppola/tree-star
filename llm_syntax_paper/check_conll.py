#!/usr/bin/env python3

from stanza.utils.conll import CoNLL
import argparse

def main():
    parser = argparse.ArgumentParser(description="Check if a CoNLL file is well-formed and count the number of examples.")
    parser.add_argument("conll_file", help="Path to the CoNLL-U file")
    args = parser.parse_args()

    try:
        # Load the CoNLL file using Stanza (throws if malformed)
        docs = CoNLL.conll2dict(input_file=args.conll_file)

        total_sentences = sum(len(doc) for doc in docs)

        print(f"✅ File '{args.conll_file}' is well-formed.")
        print(f"📝 Total sentences: {total_sentences}")

    except Exception as e:
        print(f"❌ File '{args.conll_file}' is not well-formed!")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()

