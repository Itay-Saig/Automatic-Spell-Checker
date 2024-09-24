# Automatic Spell Checker
![Python Version](https://img.shields.io/badge/python-3.9-blue)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Developing a context-aware spell checker that uses language modeling and error tables to efficiently correct spelling mistakes.

This project applies principles from language modeling and error analysis to build an automatic spelling correction system. It detects spelling errors, ranks potential corrections, and outputs the most contextually appropriate suggestion.

## :clipboard: Table of Contents
  * [Introduction](#bookmark_tabs-introduction)
  * [Goals and Features](#dart-goals-and-features)
  * [Data Description](#bar_chart-data-description)
  * [Pre-processing](#broom-pre-processing)
  * [Spell Checker Architecture](#hammer_and_wrench-spell-checker-architecture)
  * [Noisy Channel Model](#loud_sound-noisy-channel-model)
  * [Error Tables](#clipboard-error-tables)
  * [Language Model](#brain-language-model)
  * [Usage](#computer-usage)

## :bookmark_tabs: Introduction
This project implements a spell checker capable of handling both non-word and real-word errors. The system uses the Noisy Channel Model to incorporate both the error likelihood (at a character level) and the probability of words within a sentence context to maximize the likelihood of the corrected sentence.

## :dart: Goals and Features
The project aims to develop a robust automatic spelling correction system. It will effectively identify and rectify misspelled words using the Noisy Channel Model and employ a Language Model to assess sentence context. This system will encompass several essential features, including:
- Supports corrections for both character-level and word-level errors.
- Handles up to two character-level errors in words and one erroneous word per sentence.
- Implements confusion matrices to manage error types and common spelling mistakes.
- Generates contextually accurate suggestions.
- Addresses various types of errors, including phonetic, typographic and contextual mistakes.

## :bar_chart: Data Description
The spell checker can work with any text-based data, and it processes input sentences or documents by identifying potential errors. While this project doesn't rely on a specific dataset, it uses predefined error tables that capture common spelling mistakes and utilizes language models trained on large corpora:
- Norvig’s big.txt: A large text corpus for language modeling.
- Error Tables: Based on the paper ["A Spelling Correction Program Based on a Noisy Channel Model"](https://aclanthology.org/C90-2036.pdf) (Kernighan et al., 1990), as well as a custom set of common misspellings.

![](docs/Error_table_example.png)

## :broom: Pre-processing
The pre-processing phase includes:
- Text Normalization: Removing unnecessary characters, lowercasing and standardizing text formats.
- Tokenization: Splitting text into individual words or tokens.
- Error Analysis: Identifying potential spelling errors by comparing words against a dictionary and utilizing error tables for likely confusions.
- Context Extraction: Capturing the surrounding words of each identified error to assist in ranking correction suggestions.

## :hammer_and_wrench: Spell Checker Architecture
The spell-checking system is based on the following components:
- Error Tables: Mapping commonly misspelled characters or words.
- Language Model: An inner class within the `SpellChecker` class that ranks correction suggestions based on contextual probability.
- Correction Algorithm: A core algorithm that matches potential corrections to detected errors and ranks them by likelihood.

## :loud_sound: Noisy Channel Model
This model uses both the error type at the character level and the probability of word sequences to correct misspellings. The correction aims to maximize the likelihood of the full corrected sentence, considering prior word probabilities and likely character-level errors.

## :clipboard: Error Tables
Confusion matrices based on common misspellings are used to guide corrections, which are integrated with the language model in a context-sensitive manner. The system is designed to correct up to two character-level errors in a word.

## :brain: Language Model
The `LanguageModel` (an inner class) supports:
- N-gram modeling for both words and characters.
- Sentence generation based on learned models.
- Smoothing for unseen n-grams.
- Evaluation of sentence likelihood in context.

## :computer: Usage
To use the spell checker:
1. Clone the repository and install the dependencies listed in `requirements.txt`.
2. Run the script from `main.py`, which demonstrates how to input text and receive corrected outputs.
3. Example command:
   ```bash
   python main.py "This is an exmple of a sentence with spelling errobs."
   ```
4. The output will provide the corrected sentence:
   `"This is an example of a sentence with spelling errors."`
