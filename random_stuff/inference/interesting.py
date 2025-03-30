#!/usr/bin/env python3

from stanza.utils.conll import CoNLL
import argparse
from typing import List, Dict, Tuple

def load_conll_file(file_path: str) -> Tuple[List[List[List[Dict]]], ...]:
    """Load a CoNLL file and return it as a tuple of documents."""
    return CoNLL.conll2dict(input_file=file_path)

def format_sentence(sentence: List[Dict]) -> str:
    """Format a sentence for display."""
    return ' '.join(token['text'] for token in sentence)

def save_sentence(sentence: List[Dict], output_file):
    """Save a sentence in CoNLL format."""
    for token in sentence:
        # Format each token as a CoNLL line
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
    output_file.write('\n')  # Empty line between sentences

def main():
    parser = argparse.ArgumentParser(description='Interactively filter interesting sentences from a CoNLL file')
    parser.add_argument('input_file', help='Path to input CoNLL file')
    parser.add_argument('output_file', help='Path to output CoNLL file')
    args = parser.parse_args()
    
    # Load input file
    print(f"Loading {args.input_file}...")
    docs = load_conll_file(args.input_file)
    
    # Open output file
    with open(args.output_file, 'w') as out_f:
        total_sentences = 0
        saved_sentences = 0
        
        # Process each sentence
        for doc_idx, doc in enumerate(docs):
            for sent_idx, sentence in enumerate(doc):
                total_sentences += 1
                
                # Clear screen for better readability (print newlines)
                print("\n" * 2)
                
                # Show sentence
                print(f"Sentence {total_sentences}:")
                print(format_sentence(sentence))
                print()
                
                # Ask user
                while True:
                    response = input("Is this interesting? (y/n): ").lower().strip()
                    if response in ['y', 'n']:
                        break
                    print("Please answer 'y' or 'n'")
                
                # Save if interesting
                if response == 'y':
                    save_sentence(sentence, out_f)
                    saved_sentences += 1
                    print("Saved!")
                else:
                    print("Skipped!")
                
                # Show progress
                print(f"\nProgress: {total_sentences} sentences processed, {saved_sentences} saved")
                
                # Optional: allow early exit
                if total_sentences % 10 == 0:  # Ask every 10 sentences
                    while True:
                        cont = input("\nContinue? (y/n): ").lower().strip()
                        if cont in ['y', 'n']:
                            break
                        print("Please answer 'y' or 'n'")
                    if cont == 'n':
                        print("\nStopping early!")
                        break
            
            if cont == 'n':  # Break outer loop too
                break
        
        print(f"\nDone! Processed {total_sentences} sentences, saved {saved_sentences} interesting ones.")
        print(f"Interesting sentences saved to: {args.output_file}")

if __name__ == "__main__":
    main() 