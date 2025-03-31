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
python python/preliminary/ask_chatgpt_oneshot.py --gold_file data/input/preliminary/examples25.conllu --live_run --output_file data/output/preliminary/examples25.conllu.ask_chatgpt_oneshot.py.conllu
```

#### 📈 Figure 1: Zero-Shot Full Parsing Performance

**Description:**  
Accuracy of ChatGPT in a zero-shot setting on full dependency parses. Metrics include Part-of-Speech tagging (POS), Unlabeled Attachment Score (UAS), and Labeled Attachment Score (LAS).

| Metric | Accuracy (%) |
|--------|---------------|
| POS    | 94.04         |
| UAS    | 50.00         |
| LAS    | 46.56         |
| total  tokens | 436    |
| avg tokens    | 22     |

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
python python/preliminary/ask_chatgpt_tags.py data/input/preliminary/examples25.conllu --live_run --output_file preliminary/examples25.conllu.ask_chatgpt_tags

# 2. Head Prediction (with gold POS)
python python/preliminary/ask_chatgpt_arcs.py data/input/preliminary/examples25.conllu --live_run --output_file data/output/preliminary/examples25.conllu.ask_chatgpt_arcs.py.conllu

# 3. Dependency Label Prediction (with gold heads)
python python/preliminary/ask_chatgpt_rels.py data/input/preliminary/examples25.conllu --live_run --output_file data/output/preliminary/examples25.conllu.ask_chatgpt_rels.py.conllu
```

#### 📈 Figure 2: Decomposed Parsing Subtasks Performance

**Description:**  
Accuracy of ChatGPT when syntactic analysis is broken into individual tasks: POS tagging, head prediction (with gold POS), and dependency label prediction (with gold heads).

| Subtask                    | Accuracy (%) | Total Tokens | Correct Tags |
|---------------------------|--------------|--------------|--------------|
| POS Tagging               | 91.09        | 202          | 184          |
| Head Prediction (gold POS)| 34.91        | 527          | 184          |
| Dependency Labeling       | 52.18        | 527          | 275          |

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

```bash
# ask stanza parser
python python/systematic_pp/stanza_against_gpt.py data/input/systematic_pp/chatgpt_generated_20.json --live_run --output_file data/output/systematic_pp/chatgpt_generated_20.stanza.conllu

python python/systematic_pp/stanza_against_gpt.py data/input/systematic_pp/chatgpt_generated_20.heldout1.json --live_run --output_file data/output/systematic_pp/chatgpt_generated_20.heldout1.stanza.conllu

# ask chatgpt api
python python/systematic_pp/gptapi_against_gpt.py data/input/systematic_pp/chatgpt_generated_20.json --live_run --output_base data/output/systematic_pp/chatgpt_generated_20.gptapi.json
```

#### 📈 Figure 3: PP Attachment Accuracy — ChatGPT vs. Stanford Parser

**Description:**  
Accuracy of prepositional phrase attachment for ambiguous constructions. Results reflect evaluation on a set of ~100 examples, with statistical significance calculated via binomial test.

| System           | Accuracy (%) | 95% CI           | Significance |
|------------------|--------------|------------------|--------------|
| ChatGPT (zero-shot) | 95.00         | [_.__, _.__]     | _           |
| Stanford Parser     | 50.00        | [_.__, _.__]     | _           |

---

### 4. **Parse Critique (Error Detection)**  
**Section:** 4.4  
**Goal:** Evaluate ChatGPT's ability to detect errors in Stanford dependency parses.  

We conduct two complementary experiments:

#### 4.4.1 **General Parse Critique**  
**Goal:** Assess whether ChatGPT can detect *any* error in a given dependency parse, without being guided to a specific construction.

```bash
python python/reranker/gptapi_as_reranker.py data/input/systematic_pp/chatgpt_generated_20.json --output_file data/output/reranker/chatgpt_generated_20.reranker.json
```

eval:

```bash
python eval/evluate_chatgpt_as_reranker.py data/output/reranker/chatgpt_generated_20.reranker.json
```

#### 📈 Figure 4: General Parse Critique — ChatGPT as Error Detector

**Description:**  
ChatGPT's performance when asked to critique full parses without specific hints. Manual evaluation measures binary correctness and plausibility of explanations.

| Metric                                    | Accuracy (%) |
|-------------------------------------------|--------------|
| ChatGPT on Correct Parser Outputs         | 100.00       |
| ChatGPT on Incorrect Parser Outputs       | 0.00        |
| Overall ChatGPT Accuracy                  | 50.00        |
| Total Examples Evaluated                  | 20           |

#### 4.4.2 **Targeted Attachment Critique**  
**Goal:** Evaluate ChatGPT's ability to detect *specific* errors in PP-attachment decisions.

```bash
python python/reranker/gptapi_with_hint.py data/input/systematic_pp/chatgpt_generated_20.json --output_file data/output/reranker/chatgpt_generated_20.hint.json
```

#### 📈 Figure 5: Targeted Attachment Critique — Focused Evaluation of PP Errors

**Description:**  
ChatGPT's accuracy when asked to evaluate a specific ambiguous prepositional phrase (e.g., "with the telescope"). Shows improvement over general critique task.

| Metric                                    | Accuracy (%) |
|-------------------------------------------|--------------|
| ChatGPT on Correct Parser Outputs         | 100.00       |
| ChatGPT on Incorrect Parser Outputs       | 10.00        |
| Overall ChatGPT Accuracy                  | 55.00        |
| Total Examples Evaluated                  | 20           |

