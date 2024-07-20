import os
from typing import Any

import nltk
from nltk.tokenize import word_tokenize

from pureml_evaluate.metrics.metric_base import MetricBase

data_path = os.path.join(
    os.path.dirname(__file__),
    "PureML/packages/pureml_evaluate/pureml_evaluate/metrics/nlp_metrics_model/nltk_data",
)

nltk.data.path.append(data_path)
tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()


class FleschKincaidGradeLevel(MetricBase):
    name = "flesch_kincaid_grade_level"
    input_type = "text"
    output_type: Any = None
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def flesch_kincaid(self, text):
        words = word_tokenize(text)
        sentences = tokenizer.tokenize(text)

        word_count = len(words)
        sentence_count = len(sentences)
        syllable_count = 0

        for word in words:
            syllable_count += self.count_syllables(word)

        return (
            0.39 * (word_count / sentence_count)
            + 11.8 * (syllable_count / word_count)
            - 15.59
        )

    def count_syllables(self, word):
        word = word.lower()
        return len([c for c in word if c in "aeiouy"])

    def compute(self, references, predictions, **kwargs):

        combined_text = references + " " + predictions

        if references:
            result = self.flesch_kincaid(combined_text)
        else:
            result = self.flesch_kincaid(predictions)

        return {self.name: {"value": result}}
