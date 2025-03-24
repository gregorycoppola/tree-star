#!/usr/bin/env python3

import json
import stanza
import argparse
import logging
import sys
from typing import List, Dict, Optional

def setup_args():
    parser = argparse.ArgumentParser(description='Evaluate Stanza dependency parsing on ambiguous attachments')
    parser.add_argument('input_file', help='Input JSON file with examples')
    parser.add_argument('--live_run', action='store_true',
                        help='If set, download and run Stanza. Otherwise, just print examples')
    parser.add_argument('--output_file',
                        help='File to save CoNLL-U output (required for live run)')
    args = parser.parse_args()

    if args.live_run and not args.output_file:
        parser.error("--output_file is required when using --live_run")

    return args

def analyze_phrase_attachment(phrase: str, sentence_tokens: List) -> Dict[str, Optional[str]]:
    """
    Analyze a phrase to find:
    - the head word *within* the phrase
    - the word the phrase is *attached to* (outside the phrase)
    """
    phrase_words = set(phrase.lower().split())
    phrase_tokens = [t for t in sentence_tokens if t.text.lower() in phrase_words]
    phrase_token_ids = {t.id for t in phrase_tokens}

    if not phrase_tokens:
        return {"phrase_head": None, "attachment_head": None}

    # Phrase head = token whose head is outside the phrase
    phrase_head_token = None
    for t in phrase_tokens:
        if t.head not in phrase_token_ids:
            phrase_head_token = t
            break

    # External attachment
    attachment_token = (
        next((t for t in sentence_tokens if t.id == phrase_head_token.head), None)
        if phrase_head_token else None
    )
    print(f"[DEBUG] Phrase: '{phrase}' → head: '{phrase_head_token.text if phrase_head_token else None}', attachment: '{attachment_token.text if attachment_token else None}'")


    return {
        "phrase_head": phrase_head_token.text if phrase_head_token else None,
        "attachment_head": attachment_token.text if attachment_token else None
    }

def evaluate_example(nlp: stanza.Pipeline, example: Dict) -> Dict:
    doc = nlp(example["sentence"])
    sentence = doc.sentences[0]

    analysis = analyze_phrase_attachment(example["ambiguous_phrase"], sentence.words)
    predicted_head = analysis["attachment_head"]
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

    logger.info(f"Loading examples from {args.input_file}")
    with open(args.input_file) as f:
        examples = json.load(f)

    if args.live_run:
        logger.info("Running in LIVE mode - will download and run Stanza")
        stanza.download('en')
        nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse')

        correct = 0
        total = len(examples)

        with open(args.output_file, 'w') as f:
            for i, example in enumerate(examples, 1):
                result = evaluate_example(nlp, example)
                if result["correct"]:
                    correct += 1

                logger.info(f"\nExample {i}/{total}:")
                logger.info(f"Sentence: {result['sentence']}")
                logger.info(f"→ Phrase: '{result['ambiguous_phrase']}' → predicted: '{result['predicted_head']}', expected: '{result['expected_head']}'")

                doc = nlp(example["sentence"])
                for sentence in doc.sentences:
                    f.write(f"# text = {example['sentence']}\n")
                    f.write(f"# predicted_head = {result['predicted_head']}, expected_head = {result['expected_head']}\n")
                    for word in sentence.words:
                        f.write(f"{word.id}\t{word.text}\t{word.lemma}\t{word.upos}\t{word.xpos}\t_\t{word.head}\t{word.deprel}\t_\t_\n")
                    f.write("\n")

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