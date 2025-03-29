#!/usr/bin/env python3

import json
import stanza
import argparse
import logging
import sys
from pathlib import Path
from openai import OpenAI
from typing import List, Dict, Optional


def setup_args():
    parser = argparse.ArgumentParser(description='Run Stanza + ChatGPT to evaluate parses for attachment errors')
    parser.add_argument('input_file', help='Input JSON file with sentence examples')
    parser.add_argument('--live_run', action='store_true', help='If set, calls OpenAI API')
    parser.add_argument('--output_file', required=True, help='Path to save output JSONL results')
    return parser.parse_args()


def stanza_to_conllu(sentence, text):
    conllu_lines = [f"# text = {text}"]
    for word in sentence.words:
        conllu_lines.append(
            f"{word.id}\t{word.text}\t{word.lemma}\t{word.upos}\t{word.xpos}\t_\t{word.head}\t{word.deprel}\t_\t_"
        )
    return "\n".join(conllu_lines)


def analyze_attachment(sentence_tokens, phrase: str, full_sentence: str) -> Dict[str, Optional[str]]:
    phrase = phrase.strip()
    phrase_start = full_sentence.lower().find(phrase.lower())
    phrase_end = phrase_start + len(phrase)

    phrase_tokens = [
        t for t in sentence_tokens
        if t.start_char is not None and t.end_char is not None
        and t.start_char >= phrase_start and t.end_char <= phrase_end
    ]

    phrase_token_ids = {t.id for t in phrase_tokens}
    if not phrase_tokens:
        return {"phrase_head": None, "attachment_head": None}

    phrase_head_token = None
    for t in phrase_tokens:
        if t.head not in phrase_token_ids:
            phrase_head_token = t
            break

    attachment_token = (
        next((t for t in sentence_tokens if t.id == phrase_head_token.head), None)
        if phrase_head_token else None
    )

    return {
        "phrase_head": phrase_head_token.text if phrase_head_token else None,
        "attachment_head": attachment_token.text if attachment_token else None
    }


def get_chatgpt_judgment(client: OpenAI, conllu: str) -> str:
    prompt = (
        "Here is a dependency parse of a sentence in CoNLL-U format.\n"
        "Do you see any errors in this parse?\n\n"
        "1. If no errors, respond only with \"no\".\n"
        "2. If yes, explain the most important or most obvious error in the sentence.\n\n"
        f"{conllu}"
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a linguist helping to analyze syntactic dependency parses."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return "error"


def main():
    args = setup_args()

    logging.basicConfig(level=logging.INFO, format='%(message)s', handlers=[logging.StreamHandler(sys.stdout)])
    logger = logging.getLogger(__name__)

    with open(args.input_file) as f:
        examples = json.load(f)

    stanza.download('en')
    nlp = stanza.Pipeline(lang='en', processors='tokenize,pos,lemma,depparse')

    if args.live_run:
        client = OpenAI()

    results = []

    for i, example in enumerate(examples, 1):
        doc = nlp(example["sentence"])
        sentence = doc.sentences[0]
        conllu = stanza_to_conllu(sentence, example["sentence"])

        analysis = analyze_attachment(sentence.words, example["ambiguous_phrase"], example["sentence"])
        predicted = analysis["attachment_head"]
        expected = example["correct_attachment"]
        correct = predicted and predicted.lower() == expected.lower()

        chatgpt_response = get_chatgpt_judgment(client, conllu) if args.live_run else "no"

        results.append({
            "index": i,
            "sentence": example["sentence"],
            "ambiguous_phrase": example["ambiguous_phrase"],
            "expected_head": expected,
            "predicted_head": predicted,
            "correct": correct,
            "chatgpt_response": chatgpt_response
        })

        logger.info(f"\nExample {i}")
        logger.info(f"Sentence: {example['sentence']}")
        logger.info(f"→ Predicted: {predicted}, Expected: {expected} → Correct: {correct}")
        logger.info(f"ChatGPT response: {chatgpt_response}")

    with open(args.output_file, 'w') as f:
        for r in results:
            json.dump(r, f)
            f.write('\n')


if __name__ == "__main__":
    main()
