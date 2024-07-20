from typing import Any

from nltk.translate.bleu_score import sentence_bleu

from pureml_evaluate.metrics.metric_base import MetricBase


class BleuScore(MetricBase):
    name = "bleu_score"
    input_type = "text"
    output_type: Any = None
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, references, predictions, **kwargs):

        blue = sentence_bleu(references=[references], hypothesis=[predictions])

        return {self.name: {"value": blue}}
