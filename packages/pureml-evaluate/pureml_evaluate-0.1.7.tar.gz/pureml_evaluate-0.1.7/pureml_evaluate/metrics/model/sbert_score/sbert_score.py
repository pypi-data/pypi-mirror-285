from typing import Any

from sentence_transformers import SentenceTransformer, util

from pureml_evaluate.metrics.metric_base import MetricBase


class SbertScore(MetricBase):
    name = "sbert_score"
    input_type = "text"
    output_type: Any = None
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, references, predictions, **kwargs):

        model = SentenceTransformer("all-MiniLM-L6-v2")
        reference_embeddings = model.encode(references)
        prediction_embeddings = model.encode(predictions)

        score = util.cos_sim(reference_embeddings, prediction_embeddings)
        score = score.item()

        return {self.name: {"value": score}}
