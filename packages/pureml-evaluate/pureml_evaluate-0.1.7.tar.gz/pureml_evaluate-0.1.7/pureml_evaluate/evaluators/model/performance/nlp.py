from pureml_evaluate.metrics.nlp_metrics_model.bert_score.bert_score import BertScore
from pureml_evaluate.metrics.nlp_metrics_model.bleu_score.bleu_score import BleuScore
from pureml_evaluate.metrics.nlp_metrics_model.flesch_kincaid_grade_level.flesch_kincaid_grade_level import (
    FleschKincaidGradeLevel,
)
from pureml_evaluate.metrics.nlp_metrics_model.meteor_score.meteor_score import (
    MeteorScore,
)
from pureml_evaluate.metrics.nlp_metrics_model.rouge_score.rouge_score import RougeScore
from pureml_evaluate.metrics.nlp_metrics_model.sbert_score.sbert_score import SbertScore


class NLP:
    def __init__(self):
        self.task_type = "nlp"
        self.evaluation_type = "performance"

        self.kwargs = None
        self.evaluator = None
        self.metrics = [
            BertScore(),
            MeteorScore(),
            RougeScore(),
            FleschKincaidGradeLevel(),
            SbertScore(),
            BleuScore(),
        ]

        self.scores = {}

    def compute(self):

        for m in self.metrics:
            # Adding  prediction scores to kwargs. It will be utilized my metrics needing it(roc_auc).
            try:
                self.kwargs["prediction_scores"] = self.prediction_scores

                score = m.compute(
                    references=self.references,
                    predictions=self.predictions,
                    **self.kwargs
                )

                self.scores.update(score)

            except Exception as e:
                print("Unable to compute", m)
                print(e)

        return self.scores
