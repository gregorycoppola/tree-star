#!/usr/bin/env python3

import stanza
from stanza.utils.conll import CoNLL
import logging
from typing import List, Dict, Tuple
import numpy as np
import sys
import argparse
import inspect

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def print_type_info(obj, name="object", indent=0):
    """Print detailed type information about an object."""
    prefix = "  " * indent
    print(f"{prefix}{name}:")
    print(f"{prefix}  type: {type(obj)}")
    
    if isinstance(obj, dict):
        print(f"{prefix}  keys: {list(obj.keys())}")
        for k, v in obj.items():
            print_type_info(v, f"  {k}", indent + 1)
    elif isinstance(obj, list):
        print(f"{prefix}  length: {len(obj)}")
        if obj:
            print(f"{prefix}  first item type: {type(obj[0])}")
            print_type_info(obj[0], "  first item", indent + 1)
    elif hasattr(obj, '__dict__'):
        print(f"{prefix}  attributes: {dir(obj)}")
        for attr in dir(obj):
            if not attr.startswith('_'):
                try:
                    value = getattr(obj, attr)
                    print_type_info(value, f"  {attr}", indent + 1)
                except:
                    pass

def load_conll_file(file_path: str) -> List[Dict]:
    """Load a CoNLL file and return it as a list of documents."""
    return CoNLL.conll2dict(input_file=file_path)

def setup_stanza_pipeline(lang: str = 'en') -> stanza.Pipeline:
    """Initialize the Stanza pipeline with dependency parsing enabled."""
    return stanza.Pipeline(lang=lang, processors='tokenize,pos,lemma,depparse')

def parse_with_stanza(pipeline: stanza.Pipeline, doc: Dict) -> Dict:
    """Parse a single document using Stanza."""
    # Convert the document to text - CoNLL format uses 'form' for the text field
    text = ' '.join([token['form'] for token in doc['tokens']])
    
    # Parse with Stanza
    parsed = pipeline(text)
    
    # Convert Stanza output to CoNLL format
    conll_output = []
    for sent in parsed.sentences:
        for word in sent.words:
            conll_output.append({
                'id': word.id,
                'form': word.text,  # Changed from 'text' to 'form' to match CoNLL format
                'lemma': word.lemma,
                'upos': word.upos,
                'xpos': word.xpos,
                'feats': '_',
                'head': word.head,
                'deprel': word.deprel,
                'deps': '_',
                'misc': '_'
            })
    
    return {'tokens': conll_output}

def evaluate_parsing(gold_docs: List[Dict], pred_docs: List[Dict]) -> Dict[str, float]:
    """Evaluate the predicted parses against gold standard."""
    total_tokens = 0
    correct_heads = 0
    correct_deprels = 0
    correct_both = 0
    
    for gold_doc, pred_doc in zip(gold_docs, pred_docs):
        for gold_token, pred_token in zip(gold_doc['tokens'], pred_doc['tokens']):
            total_tokens += 1
            
            # Compare head indices
            if gold_token['head'] == pred_token['head']:
                correct_heads += 1
            
            # Compare dependency relations
            if gold_token['deprel'] == pred_token['deprel']:
                correct_deprels += 1
            
            # Compare both head and relation
            if gold_token['head'] == pred_token['head'] and gold_token['deprel'] == pred_token['deprel']:
                correct_both += 1
    
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
    parser = argparse.ArgumentParser(description='Print type information about CoNLL parsing')
    parser.add_argument('input_file', help='Path to input CoNLL file')
    args = parser.parse_args()
    
    # Load data
    logger.info(f"Loading data from {args.input_file}...")
    docs = CoNLL.conll2dict(input_file=args.input_file)
    
    # Print information about the loaded document
    print("\n=== CoNLL Document Structure ===")
    print_type_info(docs, "docs")
    
    if docs and len(docs) > 0:
        print("\n=== First Document Structure ===")
        print_type_info(docs[0], "first_doc")
        
        if docs[0] and len(docs[0]) > 0:
            print("\n=== First Sentence Structure ===")
            print_type_info(docs[0][0], "first_sentence")
            
            if docs[0][0] and len(docs[0][0]) > 0:
                print("\n=== First Token Structure ===")
                print_type_info(docs[0][0][0], "first_token")
    
    # Initialize Stanza pipeline
    logger.info("\nInitializing Stanza pipeline...")
    pipeline = setup_stanza_pipeline()
    
    # Parse a sample sentence
    if docs and len(docs) > 0 and len(docs[0]) > 0:
        # Get the first sentence's tokens
        first_sentence = docs[0][0]
        sample_text = ' '.join([token['text'] for token in first_sentence])
        parsed = pipeline(sample_text)
        
        print("\n=== Stanza Sentence Structure ===")
        print_type_info(parsed, "parsed")
        
        if parsed.sentences:
            print("\n=== First Stanza Sentence Structure ===")
            print_type_info(parsed.sentences[0], "first_sentence")
            
            if parsed.sentences[0].words:
                print("\n=== First Stanza Word Structure ===")
                print_type_info(parsed.sentences[0].words[0], "first_word")

if __name__ == "__main__":
    main() 