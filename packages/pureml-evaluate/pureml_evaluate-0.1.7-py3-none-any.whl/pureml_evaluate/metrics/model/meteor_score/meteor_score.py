import os
from typing import Any

import nltk
from nltk.translate.meteor_score import meteor_score

from pureml_evaluate.metrics.metric_base import MetricBase

data_path = os.path.join(
    os.path.dirname(__file__),
    "PureML/packages/pureml_evaluate/pureml_evaluate/metrics/nlp_metrics_model/nltk_data",
)

nltk.data.path.append(data_path)
tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()


class MeteorScore(MetricBase):
    name = "meteor_score"
    input_type = "text"
    # output_type = 'score'
    output_type: Any = None
    kwargs = {}

    def parse_data(self, data):
        return data

    def compute(self, references, predictions, **kwargs):

        # tokenized_references = nltk.word_tokenize(references)
        # Supports only for single prediction
        tokenized_references = tokenizer.tokenize(references)
        result = meteor_score(
            references=[tokenized_references], hypothesis=[predictions]
        )

        return {self.name: result}
