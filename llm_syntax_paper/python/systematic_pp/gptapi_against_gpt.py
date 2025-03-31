#!/usr/bin/env python3

from openai import OpenAI
import json
import argparse
import logging
import sys
import os
from pathlib import Path
from typing import List, Dict

def setup_args():
    parser = argparse.ArgumentParser(description='Evaluate GPT API dependency parsing on ambiguous attachments')
    parser.add_argument('input_file', help='Input JSON file with examples')
    parser.add_argument('--live_run', action='store_true',
                       help='If set, actually query OpenAI API. Otherwise, just print examples')
    parser.add_argument('--output_base', 
                       help='Base directory for output files (required for live run)')
    args = parser.parse_args()
    
    # Check if output_base is provided when doing a live run
    if args.live_run and not args.output_base:
        parser.error("--output_base is required when using --live_run")
    
    return args

def get_output_path(input_file: str, output_base: str) -> Path:
    """Generate output path based on input filename and output directory."""
    input_path = Path(input_file)
    output_dir = Path(output_base)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Use input filename but with .jsonl extension
    output_filename = input_path.stem + '.jsonl'
    return output_dir / output_filename

def get_llm_attachment_head(client: OpenAI, sentence: str, phrase: str) -> str:
    """Query GPT to find the syntactic head that a phrase attaches to."""
    prompt = (
        f"In the sentence: \"{sentence}\"\n"
        f"What word does the phrase \"{phrase}\" attach to syntactically?\n"
        f"Return only the head word."
    )

    print(prompt)

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a linguist helping analyze syntactic attachments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        answer = response.choices[0].message.content.strip()
        return answer.split()[0].lower()
    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")
        return None

def evaluate_example(client: OpenAI, example: Dict) -> Dict:
    """Evaluate a single example using GPT."""
    predicted_head = get_llm_attachment_head(client, example["sentence"], example["ambiguous_phrase"])
    expected_head = example["correct_attachment"].lower()

    return {
        "sentence": example["sentence"],
        "ambiguous_phrase": example["ambiguous_phrase"],
        "predicted_head": predicted_head,
        "expected_head": expected_head,
        "correct": predicted_head == expected_head if predicted_head else False
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
        logger.info("Running in LIVE mode - will query OpenAI API")
        # Initialize OpenAI client (assumes OPENAI_API_KEY is set in environment)
        client = OpenAI()
        
        # Get output path
        output_file = get_output_path(args.input_file, args.output_base)
        logger.info(f"Will save results to {output_file}")
        
        correct = 0
        total = len(examples)

        # Process examples and save results
        with open(output_file, 'w') as f:
            for i, example in enumerate(examples, 1):
                # Get prediction and evaluate
                result = evaluate_example(client, example)
                if result["correct"]:
                    correct += 1
                
                # Print progress
                logger.info(f"\nExample {i}/{total}:")
                logger.info(f"Sentence: {result['sentence']}")
                logger.info(f"→ Phrase: '{result['ambiguous_phrase']}' → predicted: '{result['predicted_head']}', expected: '{result['expected_head']}'")
                
                # Write result
                json.dump(result, f)
                f.write('\n')
        
        # Print final accuracy
        accuracy = correct / total
        logger.info(f"\nFinal Accuracy: {correct}/{total} = {accuracy:.2%}")
            
    else:
        logger.info("Running in DRY RUN mode - will only print examples")
        for i, example in enumerate(examples, 1):
            logger.info(f"\nExample {i}:")
            logger.info(f"Sentence: {example['sentence']}")
            logger.info(f"Ambiguous phrase: {example['ambiguous_phrase']}")
            logger.info(f"Expected head: {example['correct_attachment']}")

if __name__ == "__main__":
    main()
