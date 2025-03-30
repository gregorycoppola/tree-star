#!/usr/bin/env python3

import openai
import argparse
import os
import logging
import sys
import time
from stanza.utils.conll import CoNLL

def setup_args():
    parser = argparse.ArgumentParser(description='Send sentences to ChatGPT for zero-shot dependency parsing.')
    parser.add_argument('--live_run', action='store_true', help='Actually send requests to OpenAI')
    parser.add_argument('--output_file', help='Where to save the CoNLL-U outputs')
    parser.add_argument('input_file', help='Input .conllu file')
    args = parser.parse_args()

    if args.live_run and not args.output_file:
        parser.error("--output_file is required in live mode")
    return args

def load_conll_sentences(path):
    docs = CoNLL.conll2dict(input_file=path)
    return [s for doc in docs for s in doc]

def format_as_text(sentence):
    return " ".join(tok["text"] for tok in sentence)

def send_to_chatgpt(prompt, client, live):
    if not live:
        print("\n=== PROMPT ===\n", prompt, "\n=== END PROMPT ===\n")
        return None
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logging.error(f"OpenAI API error: {e}")
        return None

def query_chatgpt_parse(sentence, client, live):
    text = format_as_text(sentence)
    prompt = (
        "You are a syntactic parser. Please output the correct dependency parse of the following sentence in CoNLL-U format.\n\n"
        f"Sentence: {text}"
    )
    return send_to_chatgpt(prompt, client, live)

def main():
    args = setup_args()
    logging.basicConfig(level=logging.INFO)

    client = None
    if args.live_run:
        api_key = os.environ.get("OPENAI_API_KEY")
        if not api_key:
            logging.error("Please set the OPENAI_API_KEY environment variable.")
            sys.exit(1)
        client = openai.OpenAI(api_key=api_key)

    sentences = load_conll_sentences(args.input_file)
    logging.info(f"Loaded {len(sentences)} sentences.")

    results = []
    for i, sentence in enumerate(sentences):
        logging.info(f"→ Sentence {i+1}: {format_as_text(sentence)}")
        response = query_chatgpt_parse(sentence, client, args.live_run)
        if response:
            results.append(response)
            logging.info("✅ Got response.")
            time.sleep(1.0)  # Rate limit safety
        else:
            results.append("# FAILED TO PARSE\n")

    if args.live_run:
        with open(args.output_file, "w") as f:
            for block in results:
                f.write(block.strip() + "\n\n")
        logging.info(f"Saved results to {args.output_file}")

if __name__ == "__main__":
    main()
