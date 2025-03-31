# 🧪 Experiment Plan: LLM's as Syntactic Annotation Labelers for Logical IR


### 1. **Zero-Shot Full Parsing Evaluation**
**Section:** 4.1  
**Goal:** Reproduce the zero-shot dependency parsing results.  
**Inputs:**
- A test set of English sentences (e.g., 100 from Universal Dependencies).
- Instruction-style prompt with no examples.  
**Output:**
- POS tags, head indices, and dependency labels from ChatGPT (in one go).
- Metrics: UAS, LAS, POS accuracy.


```bash
python python/preliminary/ask_chatgpt_oneshot.py data/input/sanity/examples1.conllu --live_run --output_file data/output/sanity/examples1.conllu.ask_chatgpt_oneshot
```

---

### 2. **Decomposed Subtasks Evaluation**
**Section:** 4.1  
**Goal:** Re-run POS tagging, head prediction, and dependency label prediction as separate tasks.  
**Inputs:**
- Same sentences as above, with gold-standard annotations for supervision.
- Prompt model separately for:
  - POS tagging
  - Head prediction (with gold POS)
  - Dependency label prediction (with gold head)  
**Output:**
- Accuracy for each subtask.

```bash
# 1. POS Tagging
python python/preliminary/ask_chatgpt_tags.py data/input/sanity/examples1.conllu --live_run --output_file data/output/sanity/examples1.conllu.ask_chatgpt_tags

# 2. Head Prediction (with gold POS)
python python/preliminary/ask_chatgpt_arcs.py data/input/sanity/examples1.conllu --live_run --output_file data/output/sanity/examples1.conllu.ask_chatgpt_arcs

# 3. Dependency Label Prediction (with gold heads)
python python/preliminary/ask_chatgpt_rels.py data/input/sanity/examples1.conllu --live_run --output_file data/output/sanity/examples1.conllu.ask_chatgpt_rels
```

---

### 3. **Full PP Attachment Evaluation**
**Section:** 4.3  
**Goal:** Scale the PP attachment evaluation to more than 20 sentences.  
**Tasks:**
- [ ] Generate a larger dataset (~100–200 ambiguous PP sentences).
- [ ] Annotate each with gold-standard attachment (noun vs. verb).
- [ ] Evaluate:
  - ChatGPT API (zero-shot prompting)
  - Stanford Parser  
**Metrics:**
- Accuracy (correct head prediction).
- Statistical significance (binomial test, confidence intervals).

ask stanza parser
```bash
python python/systematic_pp/stanza_against_gpt.py data/input/systematic_pp/chatgpt_generated_20.json --live_run --output_file data/output/systematic_pp/chatgpt_generated_20.stanza.conllu
```

ask chatgpt api
```bash
python measure/gptapi_against_gpt.py open-data/chatgpt_generated/set2_20examples.json --live_run --output_file open-data/chatgpt_generated/set2_predictions_chatgpt.json
```


---

Absolutely — here’s the fully unified and flowing section for **Section 4.4: Parse Critique**, integrating both the general and targeted experiments, using your original formatting and tone:

---

### 4. **Parse Critique (Error Detection)**  
**Section:** 4.4  
**Goal:** Evaluate ChatGPT's ability to detect errors in Stanford dependency parses.  

We conduct two complementary experiments:

---

#### 4.4.1 **General Parse Critique**  
**Goal:** Assess whether ChatGPT can detect *any* error in a given dependency parse, without being guided to a specific construction.

**Tasks:**
- [ ] Use same set of ambiguous sentences from above.
- [ ] For each sentence:
  - Parse using Stanford Stanza (CoNLL-U).
  - Present the full parse.
  - Ask ChatGPT:  
    *“Here is a dependency parse of the sentence ‘[sentence]’. Do you see any problems with this parse?”*
- [ ] Manually evaluate:
  - Binary correctness (error/no error).
  - Explanation plausibility.

**Metrics:**
- Binary classification accuracy
- Explanation accuracy (manual)

```bash
python measure/gptapi_as_reranker.py open-data/chatgpt_generated/set2_20examples.json --output_file open-data/chatgpt_generated/set2_20examples.getapi_as_reranker_2.json
```

**Note:** ChatGPT tends to default to "no error" responses in this setting, even when parses are incorrect.

---

#### 4.4.2 **Targeted Attachment Critique**  
**Goal:** Evaluate ChatGPT’s ability to detect *specific* errors in PP-attachment decisions.

**Tasks:**
- [ ] Use same set of ambiguous sentences from above.
- [ ] For each sentence:
  - Parse using Stanford Stanza (CoNLL-U).
  - Identify the ambiguous prepositional phrase (e.g., “with the telescope”).
  - Ask ChatGPT:  
    *“Do you see any problem with the attachment of the phrase ‘[XYZ]’ in this parse?”*
- [ ] Manually evaluate:
  - Binary correctness (error/no error).
  - Explanation plausibility.

**Metrics:**
- Targeted classification accuracy
- Explanation accuracy (manual)

```bash
python measure/gptapi_against_gpt.py open-data/chatgpt_generated/set2_20examples.json --live_run --output_base open-data/chatgpt_generated/set2_predictions_chatgpt.json.2
```

