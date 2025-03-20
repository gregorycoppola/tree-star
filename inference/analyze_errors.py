#!/usr/bin/env python3

import argparse
from typing import List, Dict, Tuple

def load_conll_file(file_path: str) -> List[List[Dict]]:
    """Load a CoNLL file and return a list of sentences, where each sentence is a list of tokens."""
    sentences = []
    current_sentence = []
    
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:  # Empty line marks sentence boundary
                if current_sentence:
                    sentences.append(current_sentence)
                    current_sentence = []
                continue
            
            # Parse CoNLL format
            fields = line.split('\t')
            if len(fields) < 8:  # Need at least up to HEAD field
                continue
                
            token = {
                'id': fields[0],
                'text': fields[1],
                'lemma': fields[2],
                'upos': fields[3],
                'xpos': fields[4],
                'feats': fields[5],
                'head': fields[6],
                'deprel': fields[7],
            }
            current_sentence.append(token)
            
    if current_sentence:  # Don't forget last sentence
        sentences.append(current_sentence)
    
    return sentences

def analyze_head_errors(gold_sents: List[List[Dict]], pred_sents: List[List[Dict]]):
    """Analyze and print head prediction errors."""
    print("Analyzing head prediction errors...")
    print("Format: Sentence #, Token #: Word (Gold head → Predicted head)")
    print("-" * 80)
    
    total_errors = 0
    error_types = {}  # Dictionary to track frequency of error types
    
    for sent_idx, (gold_sent, pred_sent) in enumerate(zip(gold_sents, pred_sents)):
        for token_idx, (gold_token, pred_token) in enumerate(zip(gold_sent, pred_sent)):
            # Clean up head values (remove tuple notation if present)
            gold_head = gold_token['head'].strip('(,)')
            pred_head = pred_token['head'].strip('(,)')
            
            if gold_head != pred_head:
                total_errors += 1
                error_pattern = f"{gold_head}→{pred_head}"
                error_types[error_pattern] = error_types.get(error_pattern, 0) + 1
                
                print(f"Sent {sent_idx + 1}, Token {token_idx + 1}: "
                      f"'{gold_token['text']}' (head: {gold_head} → {pred_head})")

    print("\nError Statistics:")
    print(f"Total head errors: {total_errors}")
    print("\nMost common error patterns (Gold→Pred):")
    for pattern, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"{pattern}: {count} times")

def main():
    parser = argparse.ArgumentParser(description='Analyze parsing errors between gold and predicted CoNLL files')
    parser.add_argument('base_output_file', help='Base path for input files (will append _gold.conllu and _pred.conllu)')
    args = parser.parse_args()
    
    # Load files
    gold_file = f"{args.base_output_file}_gold.conllu"
    pred_file = f"{args.base_output_file}_pred.conllu"
    
    print(f"Loading gold standard from {gold_file}")
    gold_sents = load_conll_file(gold_file)
    print(f"Loading predictions from {pred_file}")
    pred_sents = load_conll_file(pred_file)
    
    if len(gold_sents) != len(pred_sents):
        print(f"Warning: Different number of sentences in gold ({len(gold_sents)}) "
              f"and predicted ({len(pred_sents)}) files")
    
    analyze_head_errors(gold_sents, pred_sents)

if __name__ == "__main__":
    main() 