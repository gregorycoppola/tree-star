#!/usr/bin/env python3

import json
import stanza
import argparse
import logging
import sys
from openai import OpenAI


def setup_args():
    parser = argparse.ArgumentParser(description='Check if ChatGPT finds errors in Stanza parses')
    parser.add_argument('input_file', help='Input JSON file with sentence examples (list of {"sentence": ...})')
    parser.add_argument('--output_file', help='If set, will call OpenAI and write results to this file')
    return parser.parse_args()


def stanza_to_conllu(sentence, text):
    conllu_lines = [f"# text = {text}"]
    for word in sentence.words:
        conllu_lines.append(
            f"{word.id}\t{word.text}\t{word.lemma}\t{word.upos}\t{word.xpos}\t_\t{word.head}\t{word.deprel}\t_\t_"
        )
    return "\n".join(conllu_lines)


def build_prompt(conllu: str) -> str:
    return (
        "Here is a dependency parse of a sentence in CoNLL-U format.\n"
        "Do you see any errors in this parse?\n\n"
        "1. If no errors, respond only with \"no\".\n"
        "2. If yes, explain the most important or most obvious error in the sentence.\n\n"
        f"{conllu}"
    )


def get_chatgpt_judgment(client: OpenAI, prompt: str) -> str:
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

    use_live_api = args.output_file is not None
    client = OpenAI() if use_live_api else None
    results = []

    for i, example in enumerate(examples, 1):
        sentence_text = example["sentence"]
        doc = nlp(sentence_text)
        sentence = doc.sentences[0]
        conllu = stanza_to_conllu(sentence, sentence_text)
        prompt = build_prompt(conllu)

        if use_live_api:
            chatgpt_response = get_chatgpt_judgment(client, prompt)
        else:
            logger.info(f"\nExample {i} (DRY RUN)")
            logger.info(f"Sentence: {sentence_text}")
            logger.info("\n----- Prompt to ChatGPT -----\n")
            logger.info(prompt)
            logger.info("\n-----------------------------\n")
            chatgpt_response = "no"

        logger.info(f"ChatGPT response: {chatgpt_response}")
        logger.info("-" * 50)

        results.append({
            "index": i,
            "sentence": sentence_text,
            "conllu": conllu,
            "chatgpt_response": chatgpt_response
        })

    if use_live_api:
        with open(args.output_file, 'w') as f:
            for r in results:
                json.dump(r, f)
                f.write('\n')


if __name__ == "__main__":
    main()
