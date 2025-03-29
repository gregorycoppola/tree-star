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
python laeling/ask_chatgpt_oneshot.py \
  --input_file test_sentences.txt \
  --output_file results/full_parse/metrics.json
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
python3 labeling/ask_chatgpt_tags.py \
    --live_run \
    --output_file results/pos_tagged.conllu \
    data/input.conllu

# 2. Head Prediction (with gold POS)
python3 labeling/ask_chatgpt_arcs.py \
    --live_run \
    --output_file results/heads_predicted.conllu \
    data/input.conllu

# 3. Dependency Label Prediction (with gold heads)
python3 labeling/ask_chatgpt_rels.py \
    --live_run \
    --output_file results/labels_predicted.conllu \
    data/input.conllu
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
python measure/stanza_against_gpt.py open-data/chatgpt_generated/set2_20examples.json --live_run --output_file open-data/chatgpt_generated/set2_predictions_stanza.conllu
```

ask chatgpt api
```bash
python measure/gptapi_against_gpt.py open-data/chatgpt_generated/set2_20examples.json --live_run --output_file open-data/chatgpt_generated/set2_predictions_chatgpt.json
```


---

### 4. **Parse Critique (Error Detection)**
**Section:** 4.4  
**Goal:** Evaluate ChatGPT's ability to detect errors in Stanford parses.  
**Tasks:**
- [ ] Use same set of ambiguous sentences from above.
- [ ] For each sentence:
  - Present Stanford parse.
  - Ask ChatGPT to identify errors related to the preposition.
- [ ] Manually evaluate:
  - Binary correctness (error/no error).
  - Explanation plausibility.  
**Metrics:**
- Binary classification accuracy
- Explanation accuracy (manual)

---

### 5. **Iterative Parse Repair**
**Section:** 4.5  
**Goal:** Re-run or replicate the iterative parse repair loop with 100+ sentences.  
**Tasks:**
- [ ] Input Stanford CoNLL-U parses.
- [ ] Loop:
  1. ChatGPT critiques a parse.
  2. ChatGPT revises parse.
  3. Repeat until no changes.
- [ ] Track:
  - Number of edits
  - LAS before and after (using gold parses)
  - Accuracy of changes (manual or semi-automatic eval)  
**Metrics:**
- % sentences modified
- % arcs modified
- Change accuracy
- LAS delta

