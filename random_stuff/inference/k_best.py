import stanza
from stanza.utils.conll import CoNLL
import logging
from typing import List, Dict
import numpy as np
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def setup_stanza_pipeline(lang: str = 'en', dropout: float = 0.0) -> stanza.Pipeline:
    """Initialize the Stanza pipeline with optional dropout."""
    return stanza.Pipeline(
        lang=lang,
        processors='tokenize,pos,lemma,depparse',
        depparse_batch_size=1,
        use_gpu=False,
        tokenize_no_ssplit=True,
        depparse_pretagged=False,
        depparse_dropout=dropout
    )

def parse_with_stanza(pipeline: stanza.Pipeline, sentence: List[Dict]) -> List[Dict]:
    """Parse a single sentence using Stanza."""
    text = ' '.join([token['text'] for token in sentence])
    parsed = pipeline(text)

    conll_output = []
    for sent in parsed.sentences:
        for word in sent.words:
            conll_output.append({
                'id': (word.id,),
                'text': word.text,
                'Lemma': word.lemma,
                'upos': word.upos,
                'xpos': word.xpos,
                'Feats': '_',
                'head': (word.head,) if word.head > 0 else 0,
                'deprel': word.deprel.lower(),
                'Deps': '_',
                'Misc': '_'
            })
    return conll_output

def generate_k_best_parses(sentence: List[Dict], k: int = 5, lang: str = 'en', dropout: float = 0.1) -> List[List[Dict]]:
    """Simulate k-best parses by multiple inference runs with dropout."""
    parses = []
    for i in range(k):
        pipeline = setup_stanza_pipeline(lang=lang, dropout=dropout)
        parsed_sentence = parse_with_stanza(pipeline, sentence)
        parses.append(parsed_sentence)
        logger.info(f"Generated parse {i+1}/{k}")
    return parses

def format_token(token: Dict) -> str:
    return "\t".join([
        str(token['id'][0]),
        token['text'],
        token['Lemma'],
        token['upos'],
        token['xpos'],
        token['Feats'],
        str(token['head'][0]) if token['head'] else '0',
        token['deprel'],
        token['Deps'],
        token['Misc']
    ])

if __name__ == '__main__':
    example_sentence = [
        {'text': 'Although'}, {'text': 'the'}, {'text': 'project'}, {'text': 'was'}, {'text': 'challenging'}, 
        {'text': ','}, {'text': 'the'}, {'text': 'team'}, {'text': 'completed'}, {'text': 'it'}, 
        {'text': 'successfully'}, {'text': 'before'}, {'text': 'the'}, {'text': 'deadline'}, {'text': '.'}
    ]
    
    k_parses = generate_k_best_parses(example_sentence, k=3, dropout=0.2)

    for idx, parse in enumerate(k_parses):
        logger.info(f"\n--- Parse {idx + 1} ---")
        for token in parse:
            print(format_token(token))
