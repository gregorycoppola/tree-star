#!/usr/bin/env python3

import stanza
from stanza.utils.conll import CoNLL
import logging
from typing import List, Dict, Tuple
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_conll_file(file_path: str) -> List[Dict]:
    """Load a CoNLL file and return it as a list of documents."""
    return CoNLL.conll2dict(input_file=file_path)

def setup_stanza_pipeline(lang: str = 'en') -> stanza.Pipeline:
    """Initialize the Stanza pipeline with dependency parsing enabled."""
    return stanza.Pipeline(lang=lang, processors='tokenize,pos,lemma,depparse')

def parse_with_stanza(pipeline: stanza.Pipeline, doc: Dict) -> Dict:
    """Parse a single document using Stanza."""
    # Convert the document to text
    text = ' '.join([token['text'] for token in doc['tokens']])
    
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
    # Example usage
    gold_file = "path/to/gold.conll"
    output_file = "path/to/output.conll"
    
    # Load gold standard data
    logger.info("Loading gold standard data...")
    gold_docs = load_conll_file(gold_file)
    
    # Initialize Stanza pipeline
    logger.info("Initializing Stanza pipeline...")
    pipeline = setup_stanza_pipeline()
    
    # Parse documents
    logger.info("Parsing documents...")
    pred_docs = []
    for doc in gold_docs:
        pred_doc = parse_with_stanza(pipeline, doc)
        pred_docs.append(pred_doc)
    
    # Save predictions
    logger.info("Saving predictions...")
    CoNLL.dict2conll(pred_docs, output_file)
    
    # Evaluate
    logger.info("Evaluating results...")
    metrics = evaluate_parsing(gold_docs, pred_docs)
    
    # Print results
    logger.info("Evaluation Results:")
    for metric, value in metrics.items():
        logger.info(f"{metric}: {value:.4f}")

if __name__ == "__main__":
    main() 