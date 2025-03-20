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

def get_token_by_head(sent: List[Dict], head_idx: str) -> Dict:
    """Get token by its index (accounting for different index formats)."""
    head_idx = head_idx.strip('(,)')
    if head_idx == '0':
        return {'text': 'ROOT', 'upos': 'ROOT'}
    for token in sent:
        if token['id'].strip('(,)') == head_idx:
            return token
    return {'text': 'UNKNOWN', 'upos': 'UNKNOWN'}

def analyze_head_errors(gold_sents: List[List[Dict]], pred_sents: List[List[Dict]]):
    """Analyze and print head prediction errors."""
    total_errors = 0
    error_types = {}  # Dictionary to track frequency of error types
    
    for sent_idx, (gold_sent, pred_sent) in enumerate(zip(gold_sents, pred_sents)):
        # First, check if there are any errors in this sentence
        has_errors = False
        for g, p in zip(gold_sent, pred_sent):
            if g['head'].strip('(,)') != p['head'].strip('(,)'):
                has_errors = True
                break
        
        if has_errors:
            # Print sentence text
            print(f"\nSentence {sent_idx + 1}:")
            print(' '.join(token['text'] for token in gold_sent))
            print("Errors:")
            
            # Then show each error
            for token_idx, (gold_token, pred_token) in enumerate(zip(gold_sent, pred_sent)):
                gold_head = gold_token['head'].strip('(,)')
                pred_head = pred_token['head'].strip('(,)')
                
                if gold_head != pred_head:
                    total_errors += 1
                    error_pattern = f"{gold_head}→{pred_head}"
                    error_types[error_pattern] = error_types.get(error_pattern, 0) + 1
                    
                    # Get the head words
                    gold_head_token = get_token_by_head(gold_sent, gold_head)
                    pred_head_token = get_token_by_head(gold_sent, pred_head)
                    
                    print(f"  {gold_token['text']} → {gold_head_token['text']} (gold)")
                    print(f"  {gold_token['text']} → {pred_head_token['text']} (pred)")
                    print()

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