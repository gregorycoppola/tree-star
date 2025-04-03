#!/usr/bin/env python3

import openai
import logging
import sys
import os
import argparse
import time
from stanza.utils.conll import CoNLL
from typing import List, Dict

def setup_args():
    parser = argparse.ArgumentParser(description='Query OpenAI API for main verbs')
    parser.add_argument('--live_run', action='store_true', 
                        help='Actually send requests to OpenAI')
    parser.add_argument('input_file', help='Input CoNLL file path')
    return parser.parse_args()

def send_to_openai(prompt: str, client: openai.OpenAI, live_run: bool) -> str:
    if live_run:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return None
    else:
        print("\n=== PROMPT ===")
        print(prompt)
        print("=== END PROMPT ===\n")
        return None

def load_conll_file(file_path: str) -> List[List[Dict]]:
    doc = CoNLL.conll2dict(input_file=file_path)
    # return [sentence for doc_sentences in doc for sentence in doc_sentences]
    return doc[0]
def identify_main_verbs(sentence: List[Dict], client: openai.OpenAI, live_run: bool):
    sentence_text = " ".join(token['text'] for token in sentence)
    prompt = (
        f"In the sentence: '{sentence_text}', identify the main verb or verbs. "
        "Only list the main verbs, nothing else."
    )
    response = send_to_openai(prompt, client, live_run)
    if live_run and response:
        print("\n=== PROMPT ===")
        print(prompt)
        print("=== RESPONSE ===")
        print(response)
        print("=== END ===\n")

def main():
    global logger
    args = setup_args()

    logging.basicConfig(level=logging.INFO, format='%(message)s', handlers=[logging.StreamHandler(sys.stdout)])
    logger = logging.getLogger(__name__)

    client = None
    if args.live_run:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("Error: OPENAI_API_KEY not set")
            sys.exit(1)
        client = openai.OpenAI(api_key=api_key)

    sentences = load_conll_file(args.input_file)
    for sentence in sentences:
        identify_main_verbs(sentence, client, args.live_run)
        time.sleep(0.5)

if __name__ == "__main__":
    main()
