# Performance Metrics
from typing import Any

from pureml_evaluate.metrics.model.accuracy.accuracy import Accuracy
from pureml_evaluate.metrics.model.average_precision_score.average_precision_score import (
    AveragePrecisionScore,
)
from pureml_evaluate.metrics.model.balanced_accuracy_score.balanced_accuracy_score import (
    BalancedAccuracyScore,
)
from pureml_evaluate.metrics.model.brier_score_loss.brier_score_loss import BrierScoreLoss
from pureml_evaluate.metrics.data.data_drift.chi_squared_statistic.chi_squared_statistic import (
    ChiSquaredStatistic,
)

# Data Integrity Metrics
from pureml_evaluate.metrics.data.class_imbalance.class_imbalance import ClassImbalance
from pureml_evaluate.metrics.data.data_integrity.column_info.column_info import ColumnInfoCheck
from pureml_evaluate.metrics.data.data_integrity.conflicting_labels.conflicting_labels import (
    ConflictingLabels,
)
from pureml_evaluate.metrics.model.confusion_matrix.confusion_matrix import ConfusionMatrix
from pureml_evaluate.metrics.data.data_drift.cramers_v.cramers_v import CramersV
from pureml_evaluate.metrics.data.data_integrity.data_duplicates.data_duplicates import DataDuplicatesCheck
from pureml_evaluate.metrics.model.f1_score.f1_score import F1
from pureml_evaluate.metrics.data.data_integrity.feature_feature_correlation.feature_feature_correlation import (
    FeatureFeatureCorrelation,
)
from pureml_evaluate.metrics.data.data_drift.hellinger_distance.hellinger_distance import (
    HellingerDistance,
)
from pureml_evaluate.metrics.data.data_integrity.is_single_value.is_single_value import IsSingleValue

# Data Drift Metrics
from pureml_evaluate.metrics.data.data_drift.kolmogorov_smirnov.kolmogorov_smirnov_statistic import (
    KolmogorovSmirnov,
)
from pureml_evaluate.metrics.data.data_drift.l_infinity_distance.l_infinity_distance import (
    LInfinityDistance,
)
from pureml_evaluate.metrics.model.log_loss.log_loss import LogLoss
from pureml_evaluate.metrics.data.data_integrity.mixed_nulls.mixed_nulls import MixedNulls
from pureml_evaluate.metrics.data.data_integrity.percent_of_nulls.percent_of_nulls import PercentOfNulls
from pureml_evaluate.metrics.data.data_drift.population_stability_index.population_stability_index import (
    PopulationStabilityIndex,
)
from pureml_evaluate.metrics.model.precision.precision import Precision
from pureml_evaluate.metrics.model.recall.recall import Recall
from pureml_evaluate.metrics.model.roc_auc.roc_auc import ROC_AUC
from pureml_evaluate.metrics.data.data_integrity.special_character.special_character import (
    SpecialCharacters,
)
from pureml_evaluate.metrics.data.data_integrity.string_length_outOfBounds.string_length_outOfBounds import (
    StringLengthOutOfBounds,
)
from pureml_evaluate.metrics.data.data_integrity.string_mismatch.string_mismatch import StringMismatch
from pureml_evaluate.metrics.model.top_k_accuracy_score.top_k_accuracy_score import (
    TopKAccuracyScore,
)
from pureml_evaluate.metrics.data.data_drift.wasserstein_distance.wasserstein_distance import (
    WassersteinDistance,
)

metrics_to_class_name: Any = {
    "accuracy": Accuracy(),
    "precision": Precision(),
    "recall": Recall(),
    "f1": F1(),
    "confusionmatrix": ConfusionMatrix(),
    "balancedaccuracyScore": BalancedAccuracyScore(),
    "topkaccuracyscore": TopKAccuracyScore(),
    "logloss": LogLoss(),
    "averageprecisionscore": AveragePrecisionScore(),
    "roc_auc": ROC_AUC(),
    "brierscoreloss": BrierScoreLoss(),
    "kolmogorovsmirnov": KolmogorovSmirnov(),
    "wassersteindistance": WassersteinDistance(),
    "hellingerdistance": HellingerDistance(),
    "linfinitydistance": LInfinityDistance(),
    "chisquaredstatistic": ChiSquaredStatistic(),
    "cramersv": CramersV(),
    "populationstabilityindex": PopulationStabilityIndex(),
}

data_metrics_to_class_name: Any = {
    "classimbalance": ClassImbalance(),
    "columninfocheck": ColumnInfoCheck(),
    "conflictinglabels()": ConflictingLabels(),
    "dataduplicatescheck()": DataDuplicatesCheck(),
    "featurefeaturecorrelation()": FeatureFeatureCorrelation(),
    # 'FeatureLabelCorrelation()':FeatureLabelCorrelation(),
    # 'IdentifierLabelCorrelation()': IdentifierLabelCorrelation(),
    "issinglevalue()": IsSingleValue(),
    # 'MixedDataTypes()': MixedDataTypes(),
    "mixednulls()": MixedNulls(),
    # 'OutlierSampleDetection()': OutlierSampleDetection(),
    "percentofnulls()": PercentOfNulls(),
    "specialcharacters()": SpecialCharacters(),
    "stringlengthoutofbounds()": StringLengthOutOfBounds(),
    "stringmismatch()": StringMismatch(),
}
