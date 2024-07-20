from typing import Any

# from rouge_score import rouge_scorer
from torchmetrics.text.rouge import ROUGEScore

from pureml_evaluate.metrics.metric_base import MetricBase


class RougeScore(MetricBase):
    name = "rouge_score"
    input_type = "text"
    output_type: Any = None
    kwargs: Any = {}

    def parse_data(self, data):
        return data

    def compute(self, references, predictions, **kwargs):

        rouge_score = ROUGEScore()
        scores = rouge_score(preds=predictions, target=references)
        fmeasure = scores["rouge1_fmeasure"]
        recall = scores["rouge1_recall"]
        precision = scores["rouge1_precision"]

        # Can be calcuated for rouge1, rouge2, rougeL, rougeLsum
        precision = precision.item()
        recall = recall.item()
        fmeasure = fmeasure.item()

        return {
            self.name: {
                "precision": {"value": precision},
                "recall": {"value": recall},
                "fmeasure": {"value": fmeasure},
            }
        }
