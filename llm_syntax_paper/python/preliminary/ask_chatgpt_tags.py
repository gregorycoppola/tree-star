#!/usr/bin/env python3
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
    
    if args.live_run and not args.output_file:
        parser.error("--output_file is required when using --live_run")
    
    return args

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
            logger.error(f"Error calling OpenAI API: {e}")
            return None
    else:
        print("\n=== PROMPT THAT WOULD BE SENT ===")
        print(prompt)
        print("=== END PROMPT ===\n")
        return None

def load_conll_file(file_path: str) -> List[List[Dict]]:
    doc = CoNLL.conll2dict(input_file=file_path)
    return [sentence for doc_sentences in doc for sentence in doc_sentences]

def query_chatgpt_pos(sentence: List[Dict], focus_token: Dict, client: openai.OpenAI, live_run: bool) -> str:
    sentence_text = " ".join(token['text'] for token in sentence)
    prompt = (
        f"In the sentence '{sentence_text}', what is the part of speech of the word '{focus_token['text']}' "
        "according to the Universal POS tags used in the CoNLL guidelines? "
        "Respond with the UPOS tag only (e.g., NOUN, VERB, ADJ, etc)."
    )
    return send_to_openai(prompt, client, live_run)

def evaluate_sentences(sentences: List[List[Dict]], client: openai.OpenAI, live_run: bool) -> List[List[Dict]]:
    correct = 0
    total = 0

    for sentence in sentences:
        for token in sentence:
            gold_upos = token.get('upos', '_')
            chatgpt_prediction = query_chatgpt_pos(sentence, token, client, live_run)
            token['chatgpt_upos'] = chatgpt_prediction if chatgpt_prediction else "None"

            if live_run and chatgpt_prediction:
                if chatgpt_prediction.upper() == gold_upos.upper():
                    correct += 1
                total += 1

                logger.info(f"Token: {token['text']} | Gold UPOS: {gold_upos} | ChatGPT: {chatgpt_prediction}")

                time.sleep(0.5)

    if live_run:
        if total > 0:
            accuracy = correct / total * 100
            logger.info(f"POS Tagging Accuracy: {accuracy:.2f}%")
        else:
            logger.info("No tokens evaluated, total is 0.")

    return sentences

def save_results(sentences: List[List[Dict]], output_path: str):
    with open(output_path, 'w') as f:
        for sentence in sentences:
            for token in sentence:
                token_id = token['id'][0] if isinstance(token['id'], tuple) else token['id']
                head_id = token['head'][0] if isinstance(token['head'], tuple) else token['head']
                conll_line = [
                    str(token_id), token['text'], token.get('Lemma', '_'), token.get('upos', '_'),
                    token.get('xpos', '_'), '_', str(head_id),
                    token.get('deprel', '_'), '_', f"ChatGPTUPOS={token['chatgpt_upos']}"
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
