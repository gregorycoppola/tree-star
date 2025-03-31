# Prompts Used in Experiments

## 1. Stanza Parser
No prompt used - direct parsing via the Stanford Stanza library.

## 2. Prepositional Phrase Attachment
```text
In the sentence: "She served the guest with the silver tray."
What word does the phrase "with the silver tray" attach to syntactically?
Return only the head word.
```

## 3. ChatGPT as Reranker (No Hints)
```text
Here is a dependency parse of a sentence in CoNLL-U format.
Do you see any errors in this parse?

1. If no errors, respond only with "no".
2. If yes, explain the most important or most obvious error in the sentence.

# text = The boy saw the man with the telescope.
1	The	the	DET	DT	_	2	det	_	_
2	boy	boy	NOUN	NN	_	3	nsubj	_	_
3	saw	see	VERB	VBD	_	0	root	_	_
4	the	the	DET	DT	_	5	det	_	_
5	man	man	NOUN	NN	_	3	obj	_	_
6	with	with	ADP	IN	_	8	case	_	_
7	the	the	DET	DT	_	8	det	_	_
8	telescope	telescope	NOUN	NN	_	3	obl	_	_
9	.	.	PUNCT	.	_	3	punct	_	_
```

## 4. ChatGPT as Reranker (With Hints)
```text

```
