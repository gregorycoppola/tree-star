#!/usr/bin/env python3

import stanza
from stanza.utils.conll import CoNLL
import logging
from typing import List, Dict, Tuple
import numpy as np
import sys
import argparse
import time

logging.basicConfig(level=logging.INFO)
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
                'id': word.id,
                'text': word.text,
                'lemma': word.lemma,
                'upos': word.upos,
                'xpos': word.xpos,
                'feats': '_',
                'head': word.head,
                'deprel': word.deprel,
                'deps': '_',
                'misc': '_'
            })
    
    return conll_output

def format_token(token: Dict) -> str:
    """Format a token for display."""
    return f"{token['id']}\t{token['text']}\t{token['lemma']}\t{token['upos']}\t{token['xpos']}\t{token['feats']}\t{token['head']}\t{token['deprel']}\t{token['deps']}\t{token['misc']}"

def show_parse_diff(gold_sent: List[Dict], pred_sent: List[Dict], doc_idx: int, sent_idx: int):
    """Show differences between gold and predicted parses."""
    logger.info(f"\nDocument {doc_idx}, Sentence {sent_idx}:")
    logger.info("Gold Standard:")
    for token in gold_sent:
        logger.info(format_token(token))
    
    logger.info("\nPredicted Parse:")
    for token in pred_sent:
        logger.info(format_token(token))
    
    # Show specific differences
    logger.info("\nDifferences:")
    for gold_token, pred_token in zip(gold_sent, pred_sent):
        if gold_token['head'] != pred_token['head'] or gold_token['deprel'] != pred_token['deprel']:
            logger.info(f"Token {gold_token['id']} ({gold_token['text']}):")
            if gold_token['head'] != pred_token['head']:
                logger.info(f"  Head: {gold_token['head']} → {pred_token['head']}")
            if gold_token['deprel'] != pred_token['deprel']:
                logger.info(f"  Relation: {gold_token['deprel']} → {pred_token['deprel']}")
    logger.info("-" * 80)

def evaluate_parsing(gold_docs: Tuple[List[List[List[Dict]]], ...], 
                    pred_docs: Tuple[List[List[List[Dict]]], ...]) -> Dict[str, float]:
    """Evaluate the predicted parses against gold standard."""
    total_tokens = 0
    correct_heads = 0
    correct_deprels = 0
    correct_both = 0
    diff_count = 0
    
    for doc_idx, (gold_doc, pred_doc) in enumerate(zip(gold_docs, pred_docs)):
        for sent_idx, (gold_sent, pred_sent) in enumerate(zip(gold_doc, pred_doc)):
            has_diff = False
            for gold_token, pred_token in zip(gold_sent, pred_sent):
                total_tokens += 1
                
                # Compare head indices
                if gold_token['head'] == pred_token['head']:
                    correct_heads += 1
                else:
                    has_diff = True
                
                # Compare dependency relations
                if gold_token['deprel'] == pred_token['deprel']:
                    correct_deprels += 1
                else:
                    has_diff = True
                
                # Compare both head and relation
                if gold_token['head'] == pred_token['head'] and gold_token['deprel'] == pred_token['deprel']:
                    correct_both += 1
            
            # Show diff if there were any differences in this sentence
            if has_diff and diff_count < 10:  # Limit to first 10 diffs
                show_parse_diff(gold_sent, pred_sent, doc_idx, sent_idx)
                diff_count += 1
    
    # Calculate metrics
    uas = correct_heads / total_tokens if total_tokens > 0 else 0
    las = correct_deprels / total_tokens if total_tokens > 0 else 0
    complete = correct_both / total_tokens if total_tokens > 0 else 0
    
    return {
        'UAS': uas,
        'LAS': las,
        'Complete': complete
    }

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Parse CoNLL file using Stanza')
    parser.add_argument('input_file', help='Path to input CoNLL file')
    args = parser.parse_args()
    
    # Load data
    logger.info(f"Loading data from {args.input_file}...")
    docs = CoNLL.conll2dict(input_file=args.input_file)
    
    # Initialize Stanza pipeline
    logger.info("Initializing Stanza pipeline...")
    pipeline = setup_stanza_pipeline()
    
    # Parse all sentences
    logger.info("Starting parsing...")
    start_time = time.time()
    total_sentences = sum(len(doc) for doc in docs)
    processed_sentences = 0
    
    parsed_docs = []
    for doc_idx, doc in enumerate(docs):
        parsed_sentences = []
        for sent_idx, sentence in enumerate(doc):
            parsed = parse_with_stanza(pipeline, sentence)
            parsed_sentences.append(parsed)
            
            # Update progress
            processed_sentences += 1
            if processed_sentences % 100 == 0:
                elapsed = time.time() - start_time
                rate = processed_sentences / elapsed
                logger.info(f"Processed {processed_sentences}/{total_sentences} sentences ({rate:.2f} sentences/sec)")
        
        parsed_docs.append(parsed_sentences)
    
    # Print final statistics
    total_time = time.time() - start_time
    logger.info(f"\nParsing completed in {total_time:.2f} seconds")
    logger.info(f"Average speed: {total_sentences/total_time:.2f} sentences/second")
    
    # Evaluate results
    metrics = evaluate_parsing(docs, parsed_docs)
    logger.info("\nEvaluation Results:")
    for metric, value in metrics.items():
        logger.info(f"{metric}: {value:.4f}")

if __name__ == "__main__":
    main() 