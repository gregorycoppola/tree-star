#!/usr/bin/env python3

import stanza
from stanza.utils.conll import CoNLL
import logging
from typing import List, Dict, Tuple
import numpy as np
import sys
import argparse
import time

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',  # Simplified format
    handlers=[
        logging.StreamHandler(sys.stdout)  # Force output to stdout
    ]
)
logger = logging.getLogger(__name__)

def load_conll_file(file_path: str) -> Tuple[List[List[List[Dict]]], ...]:
    """Load a CoNLL file and return it as a tuple of documents."""
    return CoNLL.conll2dict(input_file=file_path)

def setup_stanza_pipeline(lang: str = 'en') -> stanza.Pipeline:
    """Initialize the Stanza pipeline with dependency parsing enabled."""
    return stanza.Pipeline(lang=lang, processors='tokenize,pos,lemma,depparse')

def parse_with_stanza(pipeline: stanza.Pipeline, sentence: List[Dict]) -> List[Dict]:
    """Parse a single sentence using Stanza."""
    # Convert the sentence to text
    text = ' '.join([token['text'] for token in sentence])
    
    # Parse with Stanza
    parsed = pipeline(text)
    
    # Convert Stanza output to CoNLL format
    conll_output = []
    for sent in parsed.sentences:
        for word in sent.words:
            conll_output.append({
                'id': (word.id,),  # Convert to tuple to match input format
                'text': word.text,
                'Lemma': word.lemma,  # Match capitalization in input
                'upos': word.upos,
                'xpos': word.xpos,
                'Feats': '_',
                'head': (word.head,) if word.head > 0 else 0,
                'deprel': word.deprel.lower(),
                'Deps': '_',
                'Misc': '_'
            })
    
    return conll_output

def format_token(token: Dict) -> str:
    """Format a token for display."""
    # Handle different field names in CoNLL format with fallbacks
    feats = token.get('feats', token.get('Feats', '_'))
    deps = token.get('deps', token.get('Deps', '_'))
    misc = token.get('misc', token.get('Misc', '_'))
    head = token.get('head', token.get('Head', 0))
    lemma = token.get('lemma', token.get('Lemma', '_'))
    text = token.get('text', token.get('Text', '_'))
    upos = token.get('upos', token.get('UPOS', '_'))
    xpos = token.get('xpos', token.get('XPOS', '_'))
    deprel = token.get('deprel', token.get('Deprel', '_'))
    
    # Convert head to same format for display
    head_str = f"({head[0]},)" if isinstance(head, tuple) else str(head)
    
    return (f"{token['id']}\t{text}\t{lemma}\t{upos}\t"
            f"{xpos}\t{feats}\t{head_str}\t{deprel}\t"
            f"{deps}\t{misc}")

def show_parse_diff(gold_sent: List[Dict], pred_sent: List[Dict], doc_idx: int, sent_idx: int):
    """Show differences between gold and predicted parses."""
    print(f"\nDocument {doc_idx}, Sentence {sent_idx}:")
    print("Gold Standard:")
    for token in gold_sent:
        print(format_token(token))
    
    print("\nPredicted Parse:")
    for token in pred_sent:
        print(format_token(token))
    
    # Show specific differences
    print("\nDifferences:")
    for gold_token, pred_token in zip(gold_sent, pred_sent):
        # Get head values with fallbacks
        gold_head = gold_token.get('head', gold_token.get('Head', 0))
        pred_head = pred_token.get('head', pred_token.get('Head', 0))
        
        # Get deprel values with fallbacks
        gold_deprel = gold_token.get('deprel', gold_token.get('Deprel', '')).lower()
        pred_deprel = pred_token.get('deprel', pred_token.get('Deprel', '')).lower()
        
        # Convert head values for comparison
        gold_head_val = gold_head[0] if isinstance(gold_head, tuple) else gold_head
        pred_head_val = pred_head[0] if isinstance(pred_head, tuple) else pred_head
        
        if gold_head_val != pred_head_val or gold_deprel != pred_deprel:
            print(f"Token {gold_token['id']} ({gold_token['text']}):")
            if gold_head_val != pred_head_val:
                print(f"  Head: {gold_head} → {pred_head}")
            if gold_deprel != pred_deprel:
                print(f"  Relation: {gold_deprel} → {pred_deprel}")
    print("-" * 80)

def evaluate_sentence(gold_sent: List[Dict], pred_sent: List[Dict], doc_idx: int, sent_idx: int) -> Dict[str, float]:
    """Evaluate a single sentence parse against gold standard."""
    sent_correct_heads = 0
    sent_correct_deprels = 0
    sent_correct_both = 0
    sent_tokens = 0
    
    for gold_token, pred_token in zip(gold_sent, pred_sent):
        sent_tokens += 1
        
        # Get head values, handling both cases and formats
        gold_head = gold_token.get('head', gold_token.get('Head', 0))
        pred_head = pred_token.get('head', pred_token.get('Head', 0))
        
        # Get deprel values, handling both cases
        gold_deprel = gold_token.get('deprel', gold_token.get('Deprel', '')).lower()
        pred_deprel = pred_token.get('deprel', pred_token.get('Deprel', '')).lower()
        
        # Convert to integers for comparison
        gold_head_val = gold_head[0] if isinstance(gold_head, tuple) else gold_head
        pred_head_val = pred_head[0] if isinstance(pred_head, tuple) else pred_head
        
        # Compare head indices
        if gold_head_val == pred_head_val:
            sent_correct_heads += 1
        else:
            print(f"Found head difference in doc {doc_idx}, sent {sent_idx}, token {gold_token['id']}")
        
        # Compare dependency relations
        if gold_deprel == pred_deprel:
            sent_correct_deprels += 1
        else:
            print(f"Found deprel difference in doc {doc_idx}, sent {sent_idx}, token {gold_token['id']}")
        
        # Compare both head and relation
        if gold_head_val == pred_head_val and gold_deprel == pred_deprel:
            sent_correct_both += 1
    
    # Print per-sentence metrics
    print(f"Doc {doc_idx}, Sent {sent_idx}: heads={sent_correct_heads}/{sent_tokens} "
          f"deprels={sent_correct_deprels}/{sent_tokens} "
          f"both={sent_correct_both}/{sent_tokens}")
    
    # Show diff if there were any differences
    if sent_correct_heads < sent_tokens or sent_correct_deprels < sent_tokens:
        show_parse_diff(gold_sent, pred_sent, doc_idx, sent_idx)
    
    return {
        'tokens': sent_tokens,
        'correct_heads': sent_correct_heads,
        'correct_deprels': sent_correct_deprels,
        'correct_both': sent_correct_both
    }

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Parse CoNLL file using Stanza')
    parser.add_argument('input_file', help='Path to input CoNLL file')
    parser.add_argument('base_output_file', help='Base path for output files (will append _gold.conllu and _pred.conllu)')
    args = parser.parse_args()
    
    # Open output files
    gold_file = open(f"{args.base_output_file}_gold.conllu", 'w')
    pred_file = open(f"{args.base_output_file}_pred.conllu", 'w')
    
    # Parameters
    max_diffs_to_find = 100
    diff_count = 0
    
    try:
        # Load data
        print(f"Loading data from {args.input_file}...")
        docs = CoNLL.conll2dict(input_file=args.input_file)
        
        # Initialize Stanza pipeline
        print("Initializing Stanza pipeline...")
        pipeline = setup_stanza_pipeline()
        
        # Parse and evaluate sentences
        print("Starting parsing...")
        start_time = time.time()
        total_sentences = sum(len(doc) for doc in docs)
        processed_sentences = 0
        
        # Track overall metrics
        total_tokens = 0
        total_correct_heads = 0
        total_correct_deprels = 0
        total_correct_both = 0
        
        for doc_idx, doc in enumerate(docs):
            for sent_idx, sentence in enumerate(doc):
                # Parse sentence
                parsed = parse_with_stanza(pipeline, sentence)
                
                # Check for differences in heads
                has_head_diff = False
                for gold_token, pred_token in zip(sentence, parsed):
                    gold_head = gold_token.get('head', gold_token.get('Head', 0))
                    pred_head = pred_token.get('head', pred_token.get('Head', 0))
                    gold_head_val = gold_head[0] if isinstance(gold_head, tuple) else gold_head
                    pred_head_val = pred_head[0] if isinstance(pred_head, tuple) else pred_head
                    
                    if gold_head_val != pred_head_val:
                        has_head_diff = True
                        break
                
                # If there's a difference and we haven't hit our limit, save to files
                if has_head_diff and diff_count < max_diffs_to_find:
                    # Write gold sentence
                    for token in sentence:
                        gold_file.write(format_token(token) + '\n')
                    gold_file.write('\n')
                    
                    # Write predicted sentence
                    for token in parsed:
                        pred_file.write(format_token(token) + '\n')
                    pred_file.write('\n')
                    
                    diff_count += 1
                    if diff_count >= max_diffs_to_find:
                        print(f"\nFound {max_diffs_to_find} differences, stopping...")
                        return
                
                # Evaluate and update metrics
                metrics = evaluate_sentence(sentence, parsed, doc_idx, sent_idx)
                
                # Update overall metrics
                total_tokens += metrics['tokens']
                total_correct_heads += metrics['correct_heads']
                total_correct_deprels += metrics['correct_deprels']
                total_correct_both += metrics['correct_both']
                
                # Update progress
                processed_sentences += 1
                if processed_sentences % 100 == 0:
                    elapsed = time.time() - start_time
                    rate = processed_sentences / elapsed
                    print(f"Processed {processed_sentences}/{total_sentences} sentences ({rate:.2f} sentences/sec)")
        
        # Print final statistics
        total_time = time.time() - start_time
        print(f"\nParsing completed in {total_time:.2f} seconds")
        print(f"Average speed: {total_sentences/total_time:.2f} sentences/second")
        
        # Print overall metrics
        uas = total_correct_heads / total_tokens if total_tokens > 0 else 0
        las = total_correct_deprels / total_tokens if total_tokens > 0 else 0
        complete = total_correct_both / total_tokens if total_tokens > 0 else 0
        
        print("\nFinal Results:")
        print(f"UAS: {uas:.4f}")
        print(f"LAS: {las:.4f}")
        print(f"Complete: {complete:.4f}")
        print(f"\nWrote {diff_count} differing sentences to {args.base_output_file}_gold.conllu and {args.base_output_file}_pred.conllu")
    
    finally:
        # Close files
        gold_file.close()
        pred_file.close()

if __name__ == "__main__":
    main() 