#!/usr/bin/env python3

import openai
import logging
import sys
import argparse
import time
import json
from stanza.utils.conll import CoNLL
from typing import List, Dict

# Set your OpenAI API key
openai.api_key = "YOUR_OPENAI_API_KEY"

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)


def load_conll_file(file_path: str) -> List[List[Dict]]:
    """Load sentences from a CoNLL file."""
    doc = CoNLL.conll2dict(input_file=file_path)
    return [sentence for doc_sentences in doc for sentence in doc_sentences]


def query_chatgpt(sentence: List[Dict], focus_token: Dict) -> str:
    """Send a request to ChatGPT asking about token dependencies."""
    sentence_text = " ".join(token['text'] for token in sentence)
    prompt = (
        f"Given the sentence '{sentence_text}', "
        f"according to CoNLL guidelines, which word would '{focus_token['text']}' modify? "
        "Respond with only the word it modifies. If it's the root, reply 'root'."
    )

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    result = response.choices[0].message.content.strip()
    return result


def evaluate_sentences(sentences: List[List[Dict]]) -> List[List[Dict]]:
    """Evaluate each token using ChatGPT and calculate accuracy."""
    correct = 0
    total = 0

    for sentence in sentences:
        for token in sentence:
            gold_head_idx = token['head'][0] if isinstance(token['head'], tuple) else token['head']
            gold_head_word = sentence[gold_head_idx - 1]['text'] if gold_head_idx > 0 else 'root'

            chatgpt_prediction = query_chatgpt(sentence, token)
            token['chatgpt_head'] = chatgpt_prediction

            if chatgpt_prediction == gold_head_word:
                correct += 1
            total += 1

            logger.info(f"Token: {token['text']} | Gold: {gold_head_word} | ChatGPT: {chatgpt_prediction}")

            time.sleep(0.5)  # Basic rate limiting

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


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('input_file', help='Input CoNLL file path')
    parser.add_argument('output_file', help='Output CoNLL file path')

    args = parser.parse_args()

    sentences = load_conll_file(args.input_file)
    evaluated_sentences = evaluate_sentences(sentences)
    save_results(evaluated_sentences, args.output_file)
