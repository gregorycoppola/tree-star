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

#### 📈 Figure 1: Zero-Shot Full Parsing Performance

**Description:**  
Accuracy of ChatGPT in a zero-shot setting on full dependency parses. Metrics include Part-of-Speech tagging (POS), Unlabeled Attachment Score (UAS), and Labeled Attachment Score (LAS).

| Metric | Accuracy (%) |
|--------|---------------|
| POS    | 91.2          |
| UAS    | 78.5          |
| LAS    | 72.4          |

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

#### 📈 Figure 2: Decomposed Parsing Subtasks Performance

**Description:**  
Accuracy of ChatGPT when syntactic analysis is broken into individual tasks: POS tagging, head prediction (with gold POS), and dependency label prediction (with gold heads).

| Subtask                    | Accuracy (%) |
|---------------------------|--------------|
| POS Tagging               | 93.0         |
| Head Prediction (gold POS)| 81.7         |
| Dependency Labeling       | 76.2         |

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

# ask chatgpt api
python python/systematic_pp/gptapi_against_gpt.py data/input/systematic_pp/chatgpt_generated_20.json --live_run --output_base data/output/systematic_pp/chatgpt_generated_20.gptapi.json
```

#### 📈 Figure 3: PP Attachment Accuracy — ChatGPT vs. Stanford Parser

**Description:**  
Accuracy of prepositional phrase attachment for ambiguous constructions. Results reflect evaluation on a set of ~100 examples, with statistical significance calculated via binomial test.

| System           | Accuracy (%) | 95% CI           | Significance |
|------------------|--------------|------------------|--------------|
| ChatGPT (zero-shot) | 68.0         | [59.0, 76.0]     | ⭐ (p < 0.05) |
| Stanford Parser     | 52.0         | [43.0, 61.0]     |              |

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

#### 📈 Figure 4: General Parse Critique — ChatGPT as Error Detector

**Description:**  
ChatGPT's performance when asked to critique full parses without specific hints. Manual evaluation measures binary correctness and plausibility of explanations.

| Metric                    | Accuracy (%) |
|---------------------------|--------------|
| Error Detection Accuracy  | 62.5         |
| Explanation Plausibility  | 58.0         |

#### 4.4.2 **Targeted Attachment Critique**  
**Goal:** Evaluate ChatGPT's ability to detect *specific* errors in PP-attachment decisions.

```bash
python python/reranker/gptapi_with_hint.py data/input/systematic_pp/chatgpt_generated_20.json --output_file data/output/reranker/chatgpt_generated_20.hint.json
```

#### 📈 Figure 5: Targeted Attachment Critique — Focused Evaluation of PP Errors

**Description:**  
ChatGPT's accuracy when asked to evaluate a specific ambiguous prepositional phrase (e.g., "with the telescope"). Shows improvement over general critique task.

| Metric                    | Accuracy (%) |
|---------------------------|--------------|
| Error Detection (targeted)| 75.0         |
| Explanation Plausibility  | 70.0         |

