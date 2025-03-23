#!/usr/bin/env python3

import json
import stanza
import argparse
import logging
import sys
from typing import List, Dict

def setup_args():
    parser = argparse.ArgumentParser(description='Evaluate Stanza dependency parsing on ambiguous attachments')
    parser.add_argument('input_file', help='Input JSON file with examples')
    parser.add_argument('--live_run', action='store_true',
                       help='If set, download and run Stanza. Otherwise, just print examples')
    parser.add_argument('--output_file',
                       help='File to save detailed results (required for live run)')
    args = parser.parse_args()
    
    # Check if output_file is provided when doing a live run
    if args.live_run and not args.output_file:
        parser.error("--output_file is required when using --live_run")
    
    return args

def find_head_token(phrase_tokens: List[str], sentence_tokens: List) -> str:
    """Return the head word in the dependency parse for the phrase tokens."""
    token_ids = [t.id for t in sentence_tokens if t.text in phrase_tokens]
    heads = [t.head for t in sentence_tokens if t.id in token_ids]
    head_id = max(set(heads), key=heads.count)  # most common head
    for t in sentence_tokens:
        if t.id == head_id:
            return t.text
    return None

def evaluate_example(nlp: stanza.Pipeline, example: Dict) -> Dict:
    """Evaluate a single example and return results."""
    doc = nlp(example["sentence"])
    sentence = doc.sentences[0]

    phrase_words = example["ambiguous_phrase"].split()
    predicted_head = find_head_token(phrase_words, sentence.words)
    expected_head = example["correct_attachment"]

    return {
        "sentence": example["sentence"],
        "ambiguous_phrase": example["ambiguous_phrase"],
        "predicted_head": predicted_head,
        "expected_head": expected_head,
        "correct": predicted_head.lower() == expected_head.lower() if predicted_head else False
    }

def main():
    args = setup_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger(__name__)

    # Load input data
    logger.info(f"Loading examples from {args.input_file}")
    with open(args.input_file) as f:
        examples = json.load(f)

    if args.live_run:
        logger.info("Running in LIVE mode - will download and run Stanza")
        # Initialize Stanza
        stanza.download('en')
        nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse')
        
        results = []
        correct = 0
        total = len(examples)

        for i, example in enumerate(examples, 1):
            result = evaluate_example(nlp, example)
            results.append(result)
            
            if result["correct"]:
                correct += 1
            
            # Print progress
            logger.info(f"\nExample {i}/{total}:")
            logger.info(f"Sentence: {result['sentence']}")
            logger.info(f"→ Phrase: '{result['ambiguous_phrase']}' → predicted: '{result['predicted_head']}', expected: '{result['expected_head']}'")
        
        # Print final accuracy
        accuracy = correct / total
        logger.info(f"\nFinal Accuracy: {correct}/{total} = {accuracy:.2%}")
        
        # Save detailed results
        with open(args.output_file, 'w') as f:
            json.dump({
                "total_examples": total,
                "correct": correct,
                "accuracy": accuracy,
                "detailed_results": results
            }, f, indent=2)
            
    else:
        logger.info("Running in DRY RUN mode - will only print examples")
        for i, example in enumerate(examples, 1):
            logger.info(f"\nExample {i}:")
            logger.info(f"Sentence: {example['sentence']}")
            logger.info(f"Ambiguous phrase: {example['ambiguous_phrase']}")
            logger.info(f"Expected head: {example['correct_attachment']}")

if __name__ == "__main__":
    main()
