from typing import Any

from bert_score import score

from pureml_evaluate.metrics.metric_base import MetricBase


class BertScore(MetricBase):
    name = "bert_score"
    input_type = "text"
    # output_type = 'score'
    output_type: Any = None
    kwargs = {}

    def parse_data(self, data):
        return data

    def compute(self, references, predictions, **kwargs):

        prediction, recall, f1 = score(
            cands=[references], refs=[predictions], lang="en", verbose=True
        )  # Can add model_type='xlnet-base-cased' as an argument

        # To convert tensors to int
        prediction = prediction.item()
        recall = recall.item()
        f1 = f1.item()

        result = {
            "prediction": {"value": prediction},
            "recall": {"value": recall},
            "f1": {"value": f1},
        }

        return {self.name: result}
