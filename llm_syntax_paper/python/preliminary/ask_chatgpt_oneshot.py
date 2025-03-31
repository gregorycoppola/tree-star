#!/usr/bin/env python3

import openai
import argparse
import os
import logging
import sys
import time
from stanza.utils.conll import CoNLL
from collections import Counter

def setup_args():
    parser = argparse.ArgumentParser(description='Send sentences to ChatGPT for zero-shot dependency parsing.')
    parser.add_argument('--live_run', action='store_true', help='Actually send requests to OpenAI')
    parser.add_argument('--output_file', help='Where to save the CoNLL-U outputs')
    parser.add_argument('gold_file', help='Gold standard .conllu file (used for both input and evaluation)')
    parser.add_argument('--eval', action='store_true', help='Evaluate the predictions against the gold file')
    args = parser.parse_args()

    if args.live_run and not args.output_file:
        parser.error("--output_file is required in live mode")
    return args

def load_conll_sentences(path):
    docs = CoNLL.conll2dict(input_file=path)
    return docs[0]

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

def evaluate_conllu(gold_sentences, pred_blocks):
    """Evaluate predicted parses against gold standard."""
    correct_heads = 0
    correct_labels = 0
    correct_pos = 0
    total = 0

    for gold, pred_block in zip(gold_sentences, pred_blocks):
        if pred_block.startswith("# FAILED"):
            continue

        pred_lines = [line for line in pred_block.strip().splitlines() if not line.startswith("#")]
        gold_tokens = [tok for tok in gold if '-' not in str(tok['id']) and '.' not in str(tok['id'])]
        
        if len(gold_tokens) != len(pred_lines):
            logging.warning("⚠️  Length mismatch, skipping sentence.")
            continue

        for gold_tok, pred_line in zip(gold_tokens, pred_lines):
            parts = pred_line.split('\t')
            if len(parts) != 10:
                continue
            _, _, _, upos, _, _, head, deprel, _, _ = parts
            
            # Convert head to match gold format (handle both string and tuple formats)
            gold_head = str(gold_tok["head"]).strip('(),')
            
            # Compare heads
            if head == gold_head:
                correct_heads += 1
                # Only check label if head is correct
                if deprel.lower() == gold_tok["deprel"].lower():
                    correct_labels += 1
            
            # Compare POS tags
            if upos.upper() == gold_tok["upos"].upper():
                correct_pos += 1
            
            total += 1

    # Calculate metrics
    uas = correct_heads / total * 100 if total else 0
    las = correct_labels / total * 100 if total else 0
    pos_acc = correct_pos / total * 100 if total else 0

    # Print results
    print(f"\n📊 Evaluation Results:")
    print(f"Total tokens: {total}")
    print(f"POS Accuracy: {pos_acc:.2f}%")
    print(f"UAS: {uas:.2f}%")
    print(f"LAS: {las:.2f}%")

    return {
        "pos_accuracy": pos_acc,
        "uas": uas,
        "las": las,
        "total_tokens": total
    }

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

    sentences = load_conll_sentences(args.gold_file)
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

    if args.eval:
        metrics = evaluate_conllu(sentences, results)

if __name__ == "__main__":
    main()
