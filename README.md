# Tree-Star: The Bayes-Star Treebank

*First-Order Logical Forms for All Natural Language* and an associated *Semantic Parser*

Greg Coppola, PhD.

[coppola.ai](http://coppola.ai), [vibes.university](http://vibes.university)

March 11, 2025

## Abstract

We announce a new project called "**Tree-Star: The Bayes-Star Treebank**".

* The **goal** of this project is to provide:
    * A framework for analyzing:
        * *All* (in principle) human "**natural language sentences**".
        * Into "**first-order logic**" representations.
        * Using "**labeled dependency parses**" as an "intermediate" layer of "**syntactic analysis**".
    * An associated "**syntactic parser**" and "**semantic parser**" that uses machine learning to produce such analyses automatically.
    * A "**treebank**" of natural language that is "annotated" with all applicable "**semantic**" and "**syntactic**" parsing layers.

This project can be found online at:

* https://github.com/gregorycoppola/tree-star

## The Need for Syntactic Analysis in 2025

- Traditional syntactic analysis (Chomsky, Montague) involved layers of tree-structured "syntactic" and "semantic" analysis.
- Large language models:
    - Have been the basis for the modern "boom" in attention and investment on the field of natural language processing.
    - "Large language models" do not use any traditional "hierarchical" or "latent" layers.
    - Powerful, but also limited.
- The limits of "large language models":
    - In our work last year "***The Quantified Boolean Bayesian Network: Theory and Experiments with a Logical Graphical Model***" we reviewed some of the limitations of basic LLM's:
        - They can't reason.
        - They can't plan.
        - They can't answer "probability queries".
    - We believe that these problems can be addressed with a "logical graphical model" (aka. "logical bayesian network", "logical markov model").
        - However, in order to realize this, it is necessary to first be able to express any sentence from natural language in first-order logic.
    - This, in turn, we believe necessitates being able to give a syntactic and semantic analysis of sentences in an arbitrary natural language sentence.

## The Three Interfaces

We identify "three" key interfaces that our model maps between.

- Surface form:
    - The level of "tokens".
    - Does not involve any "latent variables":
        - I.e., this layer is "fully observed".
    - The "layer" that humans interpret directly.
- Labeled dependency parse:
    - Contains "latent annotations" of a "labeled dependency tree" in which the "hidden variables" are:
        1. For each word, an "index" of another word in the document, called an "unlabeled dependency".
        2. For each "unlabeled dependency", there is one "label", taken from a finite (and in practice usually quite small) set of "discrete labels".
- First-order logic:
    - Historically well-proven as the basis for mathematics.
    - Forms the basis of much post-LLM work in "reasoning".
    - The use of "logic" is implicit in "agents".

This specific "three layer approach" we propose is an instance of "***dependency categorial grammar***".

## Methods

- English-first:
    - We will begin the process in English (or "0 to 1") first.
    - And then extending English to other languages (or "1 to N") can be done after.
    - We believe that the extension from a complete treatment of English to other languages can be done "largely automatically", due to the ability for LLM's to annotate examples as well.
- Conversion of previously labeled data:
    - We will leverage existing (expensively produced) "labeled syntactic corpora", e.g., CoNLL:
        - These represent years of study by talented and expensive researchers, as well as data labeling expense.
    - We can leverage LLM's to produce additional "layers" of annotation.
- Labeling of new unlabeled data:
    - We can leverage access to state-of-the-art LLM's via API's to label new data that has never been labeled at all.
- Community iteration:
    - We are open to receiving feedback from the community!
- Timeline:
    - We will run the project until we feel a decent "first pass" has been made.

## Future Impact

- Future applications with potentially large impact include:
    - Integrate this into a "logical markov network" to represent "human knowledge".
    - Create a system of "logical information retrieval" based on theorem-proving.
    - Create systems that can answer "probability queries" for arbitrary sentences in human language.

## Bibliography

We will present a "living" full bibliography in the repo.