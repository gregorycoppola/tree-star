#!/usr/bin/env python3

import openai
import logging
import sys
import os
import argparse
import time
import json
from stanza.utils.conll import CoNLL
from typing import List, Dict

def setup_args():
    parser = argparse.ArgumentParser(description='Query OpenAI API with prompts')
    parser.add_argument('--live_run', action='store_true', 
                       help='If set, actually send requests to OpenAI. Otherwise, just print prompts')
    parser.add_argument('--output_file', 
                       help='File to save responses (required for live run)')
    parser.add_argument('input_file', help='Input CoNLL file path')
    args = parser.parse_args()
    
    # Check if output_file is provided when doing a live run
    if args.live_run and not args.output_file:
        parser.error("--output_file is required when using --live_run")
    
    return args

def send_to_openai(prompt: str, client: openai.OpenAI, live_run: bool) -> str:
    """Send prompt to OpenAI API or simulate it."""
    if live_run:
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            return None
    else:
        # Just print what would be sent
        print("\n=== PROMPT THAT WOULD BE SENT ===")
        print(prompt)
        print("=== END PROMPT ===\n")
        return None

def load_conll_file(file_path: str) -> List[List[Dict]]:
    """Load sentences from a CoNLL file."""
    doc = CoNLL.conll2dict(input_file=file_path)
    return [sentence for doc_sentences in doc for sentence in doc_sentences]


def query_chatgpt(sentence: List[Dict], focus_token: Dict, client: openai.OpenAI, live_run: bool) -> str:
    """Send a request to ChatGPT asking about token dependencies without explicit indexing."""
    sentence_text = " ".join(token['text'] for token in sentence)
    prompt = (
        f"Given the sentence '{sentence_text}', "
        f"according to CoNLL guidelines, which word does '{focus_token['text']}' modify? "
        "Respond with only the word it modifies. If it's the root, reply 'root'."
    )
    return send_to_openai(prompt, client, live_run)



def evaluate_sentences(sentences: List[List[Dict]], client: openai.OpenAI, live_run: bool) -> List[List[Dict]]:
    """Evaluate each token using ChatGPT and calculate accuracy."""
    correct = 0
    total = 0

    for sentence in sentences:
        for token in sentence:
            gold_head_idx = token['head'][0] if isinstance(token['head'], tuple) else token['head']
            gold_head_word = sentence[gold_head_idx - 1]['text'] if gold_head_idx > 0 else 'root'

            chatgpt_prediction = query_chatgpt(sentence, token, client, live_run)
            token['chatgpt_head'] = chatgpt_prediction if chatgpt_prediction else "None"

            if live_run and chatgpt_prediction:
                if chatgpt_prediction == gold_head_word:
                    correct += 1
                total += 1

                logger.info(f"Token: {token['text']} | Gold: {gold_head_word} | ChatGPT: {chatgpt_prediction}")

                time.sleep(0.5)  # Rate limit

    if live_run and total > 0:
        accuracy = correct / total * 100
        logger.info(f"Accuracy: {accuracy:.2f}%")

    return sentences


def save_results(sentences: List[List[Dict]], output_path: str):
    """Save sentences to a CoNLL-formatted file, including ChatGPT predictions."""
    with open(output_path, 'w') as f:
        for sentence in sentences:
            for token in sentence:
                conll_line = [
                    str(token['id'][0]), token['text'], token.get('Lemma', '_'), token.get('upos', '_'),
                    token.get('xpos', '_'), '_',
                    str(token['head'][0]) if isinstance(token['head'], tuple) else str(token['head']),
                    token.get('deprel', '_'), '_', f"ChatGPTHead={token['chatgpt_head']}"
                ]
                f.write('\t'.join(conll_line) + '\n')
            f.write('\n')


def main():
    global logger
    args = setup_args()

    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s',
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    logger = logging.getLogger(__name__)

    client = None
    if args.live_run:
        api_key = os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("Error: Please set the OPENAI_API_KEY environment variable")
            sys.exit(1)
        client = openai.OpenAI(api_key=api_key)

    if args.live_run:
        logger.info(f"Running in LIVE mode - will send requests to OpenAI and save to {args.output_file}")
    else:
        logger.info("Running in DRY RUN mode - will only print prompts")

    sentences = load_conll_file(args.input_file)
    evaluated_sentences = evaluate_sentences(sentences, client, args.live_run)

    if args.live_run:
        save_results(evaluated_sentences, args.output_file)



if __name__ == "__main__":
    main()
