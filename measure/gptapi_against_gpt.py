#!/usr/bin/env python3

import json
import argparse
import logging
import sys
import openai
import os
from typing import Dict

def setup_args():
    parser = argparse.ArgumentParser(description='Evaluate LLM attachment decisions on ambiguous phrases')
    parser.add_argument('input_file', help='Input JSON file with examples')
    parser.add_argument('--live_run', action='store_true',
                       help='If set, actually query OpenAI API. Otherwise, just print examples')
    parser.add_argument('--output_file',
                       help='File to save results (required for live run)')
    args = parser.parse_args()
    
    # Check if output_file is provided when doing a live run
    if args.live_run and not args.output_file:
        parser.error("--output_file is required when using --live_run")
    
    return args

def make_prompt(sentence: str, phrase: str) -> str:
    return (
        f"In the sentence: \"{sentence}\"\n"
        f"What word does the phrase \"{phrase}\" attach to syntactically?\n"
        f"Return only the head word."
    )

def get_llm_attachment_head(sentence: str, phrase: str) -> str:
    prompt = make_prompt(sentence, phrase)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a linguist helping analyze syntactic attachments."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        answer = response["choices"][0]["message"]["content"].strip()
        # Normalize answer: grab the first word, lowercase
        return answer.split()[0].lower()
    except Exception as e:
        logging.error(f"Error calling OpenAI API: {e}")
        return None

def evaluate_example(example: Dict) -> Dict:
    predicted_head = get_llm_attachment_head(example["sentence"], example["ambiguous_phrase"])
    expected_head = example["correct_attachment"].lower()

    return {
        "sentence": example["sentence"],
        "ambiguous_phrase": example["ambiguous_phrase"],
        "predicted_head": predicted_head,
        "expected_head": expected_head,
        "correct": predicted_head == expected_head
    }

def main():
    args = setup_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger(__name__)

    # Initialize OpenAI client if doing a live run
    client = None
    if args.live_run:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            print("Error: Please set the OPENAI_API_KEY environment variable")
            sys.exit(1)
        client = openai.OpenAI(api_key=api_key)

    logger.info(f"Loading examples from {args.input_file}")
    with open(args.input_file) as f:
        examples = json.load(f)

    results = []
    correct = 0

    for i, example in enumerate(examples, 1):
        result = evaluate_example(example)
        results.append(result)
        if result["correct"]:
            correct += 1

        logger.info(f"\nExample {i}:")
        logger.info(f"Sentence: {result['sentence']}")
        logger.info(f"→ Phrase: '{result['ambiguous_phrase']}' → predicted: '{result['predicted_head']}', expected: '{result['expected_head']}'")

    accuracy = correct / len(examples)
    logger.info(f"\nFinal Accuracy: {correct}/{len(examples)} = {accuracy:.2%}")

    if args.output_file:
        with open(args.output_file, 'w') as f:
            json.dump(results, f, indent=2)
        logger.info(f"Saved results to {args.output_file}")

if __name__ == "__main__":
    main()
