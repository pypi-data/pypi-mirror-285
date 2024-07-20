# Readme for metrics
[ ] Update table to make it checklist item


# Table of Contents
## Implemented but have to test 
1. [Model Metrics](#model-metrics)
2. [Data Integrity Metrics](#data-integrity-metrics)
3. [Data Drift Metrics](#data-drift-metrics)
4. [Subset Operational Metrics](#subset-operational-metrics)

## Not Implemented at all (Pending Metrics)
1. [Transformations](#pending-transformations)
2. [Data Drift Metrics](#pending-data-drift-metrics)
3. [Abnormal Inputs](#pending-abnormal-inputs)
4. [Adversarial](#pending-adversarial)
5. [Data Cleanliness](#pending-data-cleanliness)
6. [Model Metrics](#pending-model-metrics)
7. [Bias & Fairness](#pending-bias--fairness-metrics)
8. [Model Alignment](#pending-model-alignment)
9. [Factual Awareness](#pending-factual-awareness)
10. [Evasion Attack Detection](#pending-evasion-attack-detection)
11. [Data Poisoning Detection](#pending-data-poisoning-detection)
12. [Subset Performance Degradation](#pending-subset-performance-degradation)
13. [Subset Operational](#pending-subset-operational-metrics)

## Model Metrics

This section includes various metrics used to evaluate the performance of the models.

| Implemented Status | Metric Name                          | Type         | File Link       | Source           |
|--------|--------------------------------------|--------------|-----------------|------------------|
| [x]    | accuracy                             | Operational  | [./accuracy](#)| [scikit-learn](#)|
| [x]    | additive_chi2_kernel                 | Operational  | [./additive_chi2_kernel](#)| [scikit-learn](#)      |
| [x]    | adjusted_mutual_info_score           | Operational  | [./adjusted_mutual_info_score](#)| [scikit-learn](#)      |
| [x]    | adjusted_rand_score                  | Operational  | [./adjusted_rand_score](#)       | [scikit-learn](#)      |
| [x]    | auc                                  | Operational  | [./auc](#)       | [scikit-learn](#)      |
| [x]    | average_precision_score              | Operational  | [./average_precision_score](#)       | [scikit-learn](#)      |
| [x]    | balanced_accuracy_score              | Operational  | [./balanced_accuracy_score](#)       | [scikit-learn](#)      |
| [x]    | brier_score_loss                     | Operational  | [./brier_score_loss](#)       | [scikit-learn](#)      |
| [x]    | calinski_harabasz_score              | Operational  | [./calinski_harabasz_score](#)       | [scikit-learn](#)      |
| [x]    | chi2_kernel                          | Operational  | [./chi2_kernel](#)       | [scikit-learn](#)      |
| [x]    | class_likelihood_ratios              | Operational  | [./class_likelihood_ratios](#)       | [scikit-learn](#)      |
| [x]    | cohen_kappa_score                    | Operational  | [./cohen_kappa_score](#)       | [scikit-learn](#)      |
| [x]    | completeness_score                   | Operational  | [./completeness_score](#)       | [scikit-learn](#)      |
| [x]    | confusion_matrix                     | Operational  | [./confusion_matrix](#)       | [scikit-learn](#)      |
| [x]    | contingency_matrix                   | Operational  | [./contingency_matrix](#)       | [scikit-learn](#)      |
| [x]    | cosine_distances                     | Operational  | [./cosine_distances](#)       | [scikit-learn](#)      |
| [x]    | cosine_similarity                    | Operational  | [./cosine_similarity](#)       | [scikit-learn](#)      |
| [x]    | coverage_error                       | Operational  | [./coverage_error](#)       | [scikit-learn](#)      |
| [x]    | d2_absolute_error_score              | Operational  | [./d2_absolute_error_score](#)       | [scikit-learn](#)      |
| [x]    | d2_pinball_score                     | Operational  | [./d2_pinball_score](#)       | [scikit-learn](#)      |
| [x]    | d2_tweedie_score                     | Operational  | [./d2_tweedie_score](#)       | [scikit-learn](#)      |
| [x]    | davies_bouldin_score                 | Operational  | [./davies_bouldin_score](#)       | [scikit-learn](#)      |
| [x]    | dcg_score                            | Operational  | [./dcg_score](#)       | [scikit-learn](#)      |
| [x]    | det_curve                            | Operational  | [./det_curve](#)       | [scikit-learn](#)      |
| [x]    | euclidean_distances                  | Operational  | [./euclidean_distances](#)       | [scikit-learn](#)      |
| [x]    | explained_variance_score             | Operational  | [./explained_variance_score](#)       | [scikit-learn](#)      |
| [x]    | f1_score                             | Operational  | [./f1_score](#)       | [scikit-learn](#)      |
| [x]    | fbeta_score                          | Operational  | [./fbeta_score](#)       | [scikit-learn](#)      |
| [x]    | fowlkes_mallows_score                | Operational  | [./fowlkes_mallows_score](#)       | [scikit-learn](#)      |
| [x]    | hamming_loss                         | Operational  | [./hamming_loss](#)       | [scikit-learn](#)      |
| [x]    | haversine_distances                  | Operational  | [./haversine_distances](#)       | [scikit-learn](#)      |
| [x]    | hinge_loss                           | Operational  | [./hinge_loss](#)       | [scikit-learn](#)      |
| [x]    | homogeneity_completeness_v_measure   | Operational  | [./homogeneity_completeness_v_measure](#)       | [scikit-learn](#)      |
| [x]    | homogeneity_score                    | Operational  | [./homogeneity_score](#)       | [scikit-learn](#)      |
| [x]    | jaccard_score                        | Operational  | [./jaccard_score](#)       | [scikit-learn](#)      |
| [x]    | label_ranking_average_precision_score| Operational  | [./label_ranking_average_precision_score](#)       | [scikit-learn](#)      |
| [x]    | label_ranking_loss                   | Operational  | [./label_ranking_loss](#)       | [scikit-learn](#)      |
| [x]    | laplacian_kernel                     | Operational  | [./laplacian_kernel](#)       | [scikit-learn](#)      |
| [x]    | linear_kernel                        | Operational  | [./linear_kernel](#)       | [scikit-learn](#)      |
| [x]    | log_loss                             | Operational  | [./log_loss](#)       | [scikit-learn](#)      |
| [x]    | manhattan_distances                  | Operational  | [./manhattan_distances](#)       | [scikit-learn](#)      |
| [x]    | matthews_corrcoef                    | Operational  | [./matthews_corrcoef](#)       | [scikit-learn](#)      |
| [x]    | max_error                            | Operational  | [./max_error](#)       | [scikit-learn](#)      |
| [x]    | mean_absolute_error                  | Operational  | [./mean_absolute_error](#)       | [scikit-learn](#)      |
| [x]    | mean_absolute_percentage_error       | Operational  | [./mean_absolute_percentage_error](#)       | [scikit-learn](#)      |
| [x]    | mean_gamma_deviance                  | Operational  | [./mean_gamma_deviance](#)       | [scikit-learn](#)      |
| [x]    | mean_pinball_loss                    | Operational  | [./mean_pinball_loss](#)       | [scikit-learn](#)      |
| [x]    | mean_poisson_deviance                | Operational  | [./mean_poisson_deviance](#)       | [scikit-learn](#)      |
| [x]    | mean_squared_error                   | Operational  | [./mean_squared_error](#)       | [scikit-learn](#)      |
| [x]    | mean_squared_log_error               | Operational  | [./mean_squared_log_error](#)       | [scikit-learn](#)      |
| [x]    | mean_tweedie_deviance                | Operational  | [./mean_tweedie_deviance](#)       | [scikit-learn](#)      |
| [x]    | median_absolute_error                | Operational  | [./median_absolute_error](#)       | [scikit-learn](#)      |
| [x]    | multilabel_confusion_matrix          | Operational  | [./multilabel_confusion_matrix](#)       | [scikit-learn](#)      |
| [x]    | mutual_info_score                    | Operational  | [./mutual_info_score](#)       | [scikit-learn](#)      |
| [x]    | nan_euclidean_distances              | Operational  | [./nan_euclidean_distances](#)       | [scikit-learn](#)      |
| [x]    | ndcg_score                           | Operational  | [./ndcg_score](#)       | [scikit-learn](#)      |
| [x]    | normalized_mutual_info_score         | Operational  | [./normalized_mutual_info_score](#)       | [scikit-learn](#)      |
| [x]    | pair_confusion_matrix                | Operational  | [./pair_confusion_matrix](#)       | [scikit-learn](#)      |
| [x]    | paired_cosine_distances              | Operational  | [./paired_cosine_distances](#)       | [scikit-learn](#)      |
| [x]    | paired_distances                     | Operational  | [./paired_distances](#)       | [scikit-learn](#)      |
| [x]    | paired_euclidean_distances           | Operational  | [./paired_euclidean_distances](#)       | [scikit-learn](#)      |
| [x]    | paired_manhattan_distances           | Operational  | [./paired_manhattan_distances](#)       | [scikit-learn](#)      |
| [x]    | pairwise_distances                   | Operational  | [./pairwise_distances](#)       | [scikit-learn](#)      |
| [x]    | pairwise_distances_argmin            | Operational  | [./pairwise_distances_argmin](#)       | [scikit-learn](#)      |
| [x]    | pairwise_distances_argmin_min        | Operational  | [./pairwise_distances_argmin_min](#)       | [scikit-learn](#)      |
| [x]    | pairwise_distances_chunked           | Operational  | [./pairwise_distances_chunked](#)       | [scikit-learn](#)      |
| [x]    | pairwise_kernels                     | Operational  | [./pairwise_kernels](#)       | [scikit-learn](#)      |
| [x]    | polynomial_kernel                    | Operational  | [./polynomial_kernel](#)       | [scikit-learn](#)      |
| [x]    | precision                            | Operational  | [./precision](#)       | [scikit-learn](#)      |
| [x]    | precision_recall_curve               | Operational  | [./precision_recall_curve](#)       | [scikit-learn](#)      |
| [x]    | r2_score                             | Operational  | [./r2_score](#)       | [scikit-learn](#)      |
| [x]    | rand_score                           | Operational  | [./rand_score](#)       | [scikit-learn](#)      |
| [x]    | rbf_kernel                           | Operational  | [./rbf_kernel](#)       | [scikit-learn](#)      |
| [x]    | recall                               | Operational  | [./recall](#)       | [scikit-learn](#)      |
| [x]    | roc_auc                              | Operational  | [./roc_auc](#)       | [scikit-learn](#)      |
| [x]    | roc_curve                            | Operational  | [./roc_curve](#)       | [scikit-learn](#)      |
| [x]    | sigmoid_kernel                       | Operational  | [./sigmoid_kernel](#)       | [scikit-learn](#)      |
| [x]    | silhouette_samples                   | Operational  | [./silhouette_samples](#)       | [scikit-learn](#)      |
| [x]    | silhouette_score                     | Operational  | [./silhouette_score](#)       | [scikit-learn](#)      |
| [x]    | top_k_accuracy_score                 | Operational  | [./top_k_accuracy_score](#)       | [scikit-learn](#)      |
| [x]    | v_measure_score                      | Operational  | [./v_measure_score](#)       | [scikit-learn](#)      |
| [x]    | zero_one_loss                        | Operational  | [./zero_one_loss](#)       | [scikit-learn](#)      |
| [x]    | balanced_accuracy                    | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |  balanced_acc_error                  | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |selection_rate                        | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |false_positive_rate                   | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |false_positive_error                  | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |false_negative_rate                   | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |false_positive_error                  | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |true_positive_rate                    | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |true_negative_rate                    | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |demographic_parity_difference         | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |demographic_parity_ratio              | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |equalized_odds_difference             | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |equalized_odds_ratio                  | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |equalized_odds                        | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |predictive_value_parity               | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |false_positive_parity                 | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |true_positive_parity                  | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |equal_opportunity                     | Fairness     | [./fairness_for_policy](#)   | [fairlearn](#) |
| [x]    |disparate_impact                      | Fairness     | [./fairness_for_policy](#)   | [](#) |
| [ ]    | BERT Score                         |Operational (NLP) |[./nlp_metrics_model/bert_score](#)   | Robust Intelligence|
| [ ]    | METEOR Score                       |Operational (NLP) | [./nlp_metrics_model/meteor_score](#)  | Robust Intelligence|
| [ ]    | Flesch Kincaid Grade Level         |Operational (NLP) | [./nlp_metrics_model/flesch_kincaid_grade_level](#)  | Robust Intelligence|
| [ ]    | ROUGE Score                        |Operational (NLP) | [./nlp_metrics_model/rouge_score](#)  | Robust Intelligence|
| [ ]    | SBERT Score                        |Operational (NLP) | [./nlp_metrics_model/sbert_score](#)  | Robust Intelligence|
| [ ]    | BLEU Score                         |Operational (NLP) | [./nlp_metrics_model/bleu_score](#)  | Robust Intelligence|


# Subset Operational Metrics

| Status | Metric Name                                      | Type              | File Link | Source             |
|--------|--------------------------------------------------|-------------------|-----------|--------------------|
| [ ]    | Subset Precision                                 | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset BERT Score                                | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Mean-Absolute Error (MAE)                 | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset F1                                        | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Mean-Squared Error (MSE)                  | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Macro F1                                  | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset METEOR Score                              | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset False Negative Rate                       | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Recall                                    | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Accuracy                                  | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Flesch-Kincaid Grade Level                | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Mean-Absolute Percentage Error (MAPE)     | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset ROUGE Score                               | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset False Positive Rate                       | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset SBERT Score                               | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset AUC                                       | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset BLEU Score                                | Subset Operational|           | Robust Intelligence|


# Data Integrity Metrics

This section includes metrics that ensure the integrity  of the data used.

| Implementation Status   | Metric Name                     | File Link       | Source           |
|----------|---------------------------------|-----------------|------------------|
| []      | class_imbalance                 | [./class_imbalance](#)       | [Deepchecks](#)      |
| []      | column_info                     | [./column_info](#)       | [Deepchecks](#)      |
| []      | conflicting_labels              | [./conflicting_labels](#)       | [Deepchecks](#)      |
| []      | data_duplicates                 | [./data_duplicates](#)       | [Deepchecks](#)      |
| []      | feature_feature_correlation     | [./feature_feature_correlation](#)       | [Deepchecks](#)      |
| []      | feature_label_correlation       | [./feature_label_correlation](#)       | [Deepchecks](#)      |
| []      | identifier_label_correlation    | [./identifier_label_correlation](#)       | [Deepchecks](#)      |
| []      | is_single_value                 | [./is_single_value](#)       | [Deepchecks](#)      |
| []      | mixed_data_types                | [./mixed_data_types](#)       | [Deepchecks](#)      |
| []      | mixed_nulls                     | [./mixed_nulls](#)       | [Deepchecks](#)      |
| []      | outlier_sample_detection        | [./outlier_sample_detection](#)       | [Deepchecks](#)      |
| []      | percent_of_nulls                | [./percent_of_nulls](#)       | [Deepchecks](#)      |
| []      | special_character               | [./special_character](#)       | [Deepchecks](#)      |
| []      | string_length_outOfBounds       | [./string_length_outOfBounds](#)       | [Deepchecks](#)      |
| []      | string_mismatch                 | [./string_mismatch](#)       | [Deepchecks](#)      |


# Data Drift Metrics

This section includes metrics used to detect and mitigate bias in the data.
| Implementation Status   | Metric Name                     | Type         | File Link | Source           |
|----------|---------------------------------|--------------|-----------|------------------|
|[]       | chi_squared_statistic           | Data Drift   | [./chi_squared_statistic](#)            | [NannyML](#)      |
|[]       | cramers_v                       | Data Drift   | [./cramers_v](#)            | [DeepChecks](#)      |
|[]       | hellinger_distance              | Data Drift   | [./hellinger_distance](#)            | [NannyML](#)      |
|[]       | jensen_shannon_distance         | Data Drift   | [./jensen_shannon_distance](#)            | [NannyML](#)      |
|[]       | kolmogorov_smirnov              | Data Drift   | [./kolmogorov_smirnov](#)            | [NannyML](#)      |
|[]       | l_infinity_distance             | Data Drift   | [./l_infinity_distance](#)            | [NannyML](#)      |
|[]       | population_stability_index      | Data Drift   | [./population_stability_index](#)            | [DeepChecks](#)      |
|[]       | wasserstein_distance            | Data Drift   | [./wasserstein_distance](#)            | [NannyML](#)      |


## Pending Transformations
NLP Transformation Metrics

| Status | Metric Name                           | File Link | Source             |
|--------|---------------------------------------|-----------|--------------------|
| [ ]    | Out of Range Substitution             |           | Robust Intelligence|
| [ ]    | Numeric Outliers Substitution         |           | Robust Intelligence|
| [ ]    | Feature Type Change                   |           | Robust Intelligence|
| [ ]    | Empty String Substitution             |           | Robust Intelligence|
| [ ]    | Required Characters Deletion          |           | Robust Intelligence|
| [ ]    | Unseen Categorical Substitution       |           | Robust Intelligence|
| [ ]    | Null Substitution                     |           | Robust Intelligence|
| [ ]    | Capitalization Change                 |           | Robust Intelligence|
| [ ]    | Upper-Case Text                       |           | Robust Intelligence|
| [ ]    | Lower-Case Text                       |           | Robust Intelligence|
| [ ]    | Remove Special Characters             |           | Robust Intelligence|
| [ ]    | Unicode to ASCII                      |           | Robust Intelligence|
| [ ]    | Character Substitution                |           | Robust Intelligence|
| [ ]    | Character Deletion                    |           | Robust Intelligence|
| [ ]    | Character Insertion                   |           | Robust Intelligence|
| [ ]    | Character Swap                        |           | Robust Intelligence|
| [ ]    | Keyboard Augmentation                 |           | Robust Intelligence|
| [ ]    | Common Misspellings                   |           | Robust Intelligence|
| [ ]    | OCR Error Simulation                  |           | Robust Intelligence|
| [ ]    | Synonym Swap                          |           | Robust Intelligence|
| [ ]    | Contextual Word Swap                  |           | Robust Intelligence|
| [ ]    | Contextual Word Insertion             |           | Robust Intelligence|
| [ ]    | Lower-Case Entity                     |           | Robust Intelligence|
| [ ]    | Upper-Case Entity                     |           | Robust Intelligence|
| [ ]    | Ampersand                             |           | Robust Intelligence|
| [ ]    | Abbreviation Expander                 |           | Robust Intelligence|
| [ ]    | Whitespace Around Special Character   |           | Robust Intelligence|
| [ ]    | Entity Unicode to ASCII               |           | Robust Intelligence|
| [ ]    | Entity Remove Special Characters      |           | Robust Intelligence|
| [ ]    | Swap Unseen Entities                  |           | Robust Intelligence|
| [ ]    | Gaussian Blur                         |           | Robust Intelligence|
| [ ]    | Color Jitter                          |           | Robust Intelligence|
| [ ]    | Gaussian Noise                        |           | Robust Intelligence|
| [ ]    | Vertical Flip                         |           | Robust Intelligence|
| [ ]    | Horizontal Flip                       |           | Robust Intelligence|
| [ ]    | Randomize Pixels With Mask            |           | Robust Intelligence|
| [ ]    | Contrast Increase                     |           | Robust Intelligence|
| [ ]    | Contrast Decrease                     |           | Robust Intelligence|
| [ ]    | Add Rain                              |           | Robust Intelligence|
| [ ]    | Add Snow                              |           | Robust Intelligence|
| [ ]    | Generative Upper-Case Text            |           | Robust Intelligence|
| [ ]    | Generative Lower-Case Text            |           | Robust Intelligence|
| [ ]    | Generative Remove Special Characters  |           | Robust Intelligence|
| [ ]    | Generative Unicode to ASCII           |           | Robust Intelligence|
| [ ]    | Generative Character Substitution     |           | Robust Intelligence|
| [ ]    | Generative Character Deletion         |           | Robust Intelligence|
| [ ]    | Generative Character Insertion        |           | Robust Intelligence|
| [ ]    | Generative Character Swap             |           | Robust Intelligence|
| [ ]    | Generative Keyboard Augmentation      |           | Robust Intelligence|
| [ ]    | Generative Common Misspellings        |           | Robust Intelligence|
| [ ]    | Generative OCR Error Simulation       |           | Robust Intelligence|
| [ ]    | Generative Synonym Swap               |           | Robust Intelligence|
| [ ]    | Generative Contextual Word Swap       |           | Robust Intelligence|
| [ ]    | Generative Contextual Word Insertion  |           | Robust Intelligence|
| [ ]    | Generative Character Insertion (Japanese) |      | Robust Intelligence|
| [ ]    | Generative Character Deletion (Japanese) |      | Robust Intelligence|
| [ ]    | Generative Character Swap (Japanese)  |           | Robust Intelligence|


## Pending Data Drift Metrics
This section includes metrics used to detect and mitigate bias in the data.
| Status   | Metric Name                     | Type         | File Link | Source           |
|----------|---------------------------------|--------------|-----------|------------------|
|[]       | Nulls Per Feature Drift           | Data Drift   | [](#)      | [Robust Intelligence](#)      |
|[]       | Nulls Per Row Drift                       | Data Drift   | [](#)      | [Robust Intelligence](#)      |
|[]       | Embedding Drift              | Data Drift   | [](#)      | [Robust Intelligence](#)      |
|[]       | Correlation Drift (Feature-to-Feature)         | Data Drift   | [](#)      | [Robust Intelligence](#)      |
|[]       | Correlation Drift (Feature-to-Label)              | Data Drift   | [](#)      | [Robust Intelligence](#)      |
|[]       | Mutual Information Drift (Feature-to-Feature)             | Data Drift   | [](#)      | [Robust Intelligence](#)      |
|[]       | Mutual Information Drift (Feature-to-Label)      | Data Drift   | [](#)      | [Robust Intelligence](#)      |
|[]       | Histogram-based Gradient Boosting Classification Tree.            | Data Drift   | [](#)      | [Robust Intelligence](#)      |


## Pending Abnormal Inputs


| Status | Metric Name            | File Link | Source             |
|--------|------------------------|-----------|--------------------|
| []       | Numeric Outliers       |           | Robust Intelligence|
| []      | Unseen Categorical     |           | Robust Intelligence|
|  []      | Rare Categories        |           | Robust Intelligence|
|  []      | Out of Range           |           | Robust Intelligence|
|  []      | Required Characters    |           | Robust Intelligence|
|  []      | Inconsistencies        |           | Robust Intelligence|
|  []      | Capitalization         |           | Robust Intelligence|
|  []      | Empty String           |           | Robust Intelligence|
|  []      | Embedding Anomalies    |           | Robust Intelligence|
|  []      | Null Check             |           | Robust Intelligence|
|  []      | Feature Type Check     |           | Robust Intelligence|

## Pending Adversarial

| Status | Metric Name                            | File Link | Source             |
|--------|----------------------------------------|-----------|--------------------|
| [ ]    | Single-Feature Changes                 |           | Robust Intelligence|
| [ ]    | Bounded Single-Feature Changes         |           | Robust Intelligence|
| [ ]    | Multi-Feature Changes                  |           | Robust Intelligence|
| [ ]    | Bounded Multi-Feature Changes          |           | Robust Intelligence|
| [ ]    | Tabular HopSkipJump Attack             |           | Robust Intelligence|
| [ ]    | Invisible Character Attack             |           | Robust Intelligence|
| [ ]    | Deletion Control Character Attack      |           | Robust Intelligence|
| [ ]    | Intentional Homoglyph Attack           |           | Robust Intelligence|
| [ ]    | Confusable Homoglyph Attack            |           | Robust Intelligence|
| [ ]    | HotFlip Attack                         |           | Robust Intelligence|
| [ ]    | Universal Prefix Attack                |           | Robust Intelligence|
| [ ]    | Image HopSkipJump Attack               |           | Robust Intelligence|
| [ ]    | Pixel Attack                           |           | Robust Intelligence|
| [ ]    | Square Attack                          |           | Robust Intelligence|
| [ ]    | Zero-Shot Prompt Injection             |           | Robust Intelligence|
| [ ]    | Zero-Shot Prompt Injection (Japanese)  |           | Robust Intelligence|

## Pending Data Cleanliness

| Status | Metric Name                                        | File Link | Source             |
|--------|----------------------------------------------------|-----------|--------------------|
| [ ]    | Label Imbalance                                    |           | Robust Intelligence|
| [ ]    | Required Features                                  |           | Robust Intelligence|
| [ ]    | Duplicate Row                                      |           | Robust Intelligence|
| [ ]    | Mutual Information Decrease (Feature to Label)     |           | Robust Intelligence|
| [ ]    | High Mutual Information (Feature to Label)         |           | Robust Intelligence|
| [ ]    | High Feature Correlation                           |           | Robust Intelligence|


## Pending Model Metrics
|  Status | Metric Name                          | Type         | File Link       | Source           |
|--------|--------------------------------------|--------------|-----------------|------------------|
| [ ]    | Average Number of Predicted Entities|Operational |   | Robust Intelligence|
| [ ]    | Prediction Variance (Negative Labels)|Operational |   | Robust Intelligence|
| [ ]    | Average Number of Predicted Boxes|Operational |   | Robust Intelligence|
| [ ]    | Normalized Discounted Cumulative Gain (NDCG)|Operational |   | Robust Intelligence|
| [ ]    | Average Rank|Operational |   | Robust Intelligence|
| [ ]    | Prediction Variance|Operational |   | Robust Intelligence|
| [ ]    | Mean Reciprocal Rank|Operational|   | Robust Intelligence|


## Pending Bias & Fairness Metrics

| Status | Metric Name                                      | File Link | Source             |
|--------|--------------------------------------------------|-----------|--------------------|
| [ ]    | Protected Feature Drift                          |           | Robust Intelligence|
| [ ]    | Demographic Parity (AVG Pred)                    |           | Robust Intelligence|
| [ ]    | Demographic Parity (Avg Rank)                    |           | Robust Intelligence|
| [ ]    | Equalized Odds                                   |           | Robust Intelligence|
| [ ]    | Feature Independence                             |           | Robust Intelligence|
| [ ]    | Predict Protected Features                       |           | Robust Intelligence|
| [ ]    | Feature Indenpendence                            |           | Robust Intelligence|
| [ ]    | Equal Opportunity (Macro Recall)                 |           | Robust Intelligence|
| [ ]    | Intersectional Group Fairness (Pos Pred)         |           | Robust Intelligence|
| [ ]    | Intersectional Group Fairness (Avg Pred)         |           | Robust Intelligence|
| [ ]    | Intersectional Group Fairness (Avg Rank)         |           | Robust Intelligence|
| [ ]    | Discrimination by Proxy                          |           | Robust Intelligence|
| [ ]    | Subset Sensitivity (Pos Pred)                    |           | Robust Intelligence|
| [ ]    | Subset Sensitivity (Avg Pred)                    |           | Robust Intelligence|
| [ ]    | Subset Sensitivity (Avg Rank)                    |           | Robust Intelligence|
| [ ]    | Gendered Pronoun Distribution                    |           | Robust Intelligence|
| [ ]    | Fill Mask Invariance                             |           | Robust Intelligence|
| [ ]    | Replace Masculine with Feminine Pronouns         |           | Robust Intelligence|
| [ ]    | Replace Feminine with Masculine Pronouns         |           | Robust Intelligence|
| [ ]    | Replace Masculine with Feminine Names            |           | Robust Intelligence|
| [ ]    | Replace Feminine with Masculine Names            |           | Robust Intelligence|
| [ ]    | Replace Masculine with Plural Pronouns           |           | Robust Intelligence|
| [ ]    | Replace Feminine with Plural Pronouns            |           | Robust Intelligence|
| [ ]    | Swap High Income with Low-Income Countries       |           | Robust Intelligence|
| [ ]    | Swap Low Income with High-Income Countries       |           | Robust Intelligence|
| [ ]    | Swap Majority Ethnicity Names with Minority Names|           | Robust Intelligence|
| [ ]    | Swap Minority Ethnicity Names with Majority Names|           | Robust Intelligence|

## Pending  Model Alignment
|  Status | Metric Name                          | Type         | File Link       | Source           |
|--------|--------------------------------------|--------------|-----------------|------------------|
| [ ]    | Row-wise Toxic Content | |   | Robust Intelligence|


## Pending  Factual Awareness
|  Status | Metric Name                          | Type         | File Link       | Source           |
|--------|--------------------------------------|--------------|-----------------|------------------|
| [ ]    | Row-wise Factual Inconsistency | |   | Robust Intelligence|


# Pending Evasion Attack Detection

| Status | Metric Name                         | File Link | Source             |
|--------|-------------------------------------|-----------|--------------------|
| [ ]    | Stateful Black Box Evasion Detection|           | Robust Intelligence|
| [ ]    | Row-wise Data Leakage               |           | Robust Intelligence|
| [ ]    | Row-wise PII Detection              |           | Robust Intelligence|
| [ ]    | Row-wise Prompt Injection Detection |           | Robust Intelligence|
| [ ]    | Row-wise Prompt Extraction Detection|           | Robust Intelligence|


# Pending Data Poisoning Detection

| Status | Metric Name                         | File Link | Source             |
|--------|-------------------------------------|-----------|--------------------|
| [ ]    | Label Flipping Detection (Exact Match)|           | Robust Intelligence|
| [ ]    | Label Flipping Detection (Near Match)               |           | Robust Intelligence|


# Pending Subset Performance Degradation


| Status | Metric Name                                      | File Link | Source             |
|--------|--------------------------------------------------|-----------|--------------------|
| [ ]    | Subset Drift Precision                           |           | Robust Intelligence|
| [ ]    | Subset Drift Mean-Squared-Log Error (MSLE)       |           | Robust Intelligence|
| [ ]    | Subset Drift Macro Precision                     |           | Robust Intelligence|
| [ ]    | Subset Drift BERT Score                          |           | Robust Intelligence|
| [ ]    | Subset Drift Multiclass Accuracy                 |           | Robust Intelligence|
| [ ]    | Subset Drift Mean-Absolute Error (MAE)           |           | Robust Intelligence|
| [ ]    | Subset Drift Prediction Variance                 |           | Robust Intelligence|
| [ ]    | Subset Drift F1                                  |           | Robust Intelligence|
| [ ]    | Subset Drift Mean-Squared Error (MSE)            |           | Robust Intelligence|
| [ ]    | Subset Drift Average Prediction                  |           | Robust Intelligence|
| [ ]    | Subset Drift Mean Reciprocal Rank (MRR)          |           | Robust Intelligence|
| [ ]    | Subset Drift Macro F1                            |           | Robust Intelligence|
| [ ]    | Subset Drift METEOR Score                        |           | Robust Intelligence|
| [ ]    | Subset Drift False Negative Rate                 |           | Robust Intelligence|
| [ ]    | Subset Drift Prediction Variance (Positive Labels)|          | Robust Intelligence|
| [ ]    | Subset Drift Rank Correlation                    |           | Robust Intelligence|
| [ ]    | Subset Drift Recall                              |           | Robust Intelligence|
| [ ]    | Subset Drift Accuracy                            |           | Robust Intelligence|
| [ ]    | Subset Drift Average Number of Predicted Entities|           | Robust Intelligence|
| [ ]    | Subset Drift Flesch-Kincaid Grade Level          |           | Robust Intelligence|
| [ ]    | Subset Drift Multiclass AUC                      |           | Robust Intelligence|
| [ ]    | Subset Drift Mean-Absolute Percentage Error (MAPE)|          | Robust Intelligence|
| [ ]    | Subset Drift ROUGE Score                         |           | Robust Intelligence|
| [ ]    | Subset Drift False Positive Rate                 |           | Robust Intelligence|
| [ ]    | Subset Drift Average Number of Predicted Boxes   |           | Robust Intelligence|
| [ ]    | Subset Drift Root-Mean-Squared Error (RMSE)      |           | Robust Intelligence|
| [ ]    | Subset Drift Average Rank                        |           | Robust Intelligence|
| [ ]    | Subset Drift Macro Recall                        |           | Robust Intelligence|
| [ ]    | Subset Drift SBERT Score                         |           | Robust Intelligence|
| [ ]    | Subset Drift NDCG                                |           | Robust Intelligence|
| [ ]    | Subset Drift AUC                                 |           | Robust Intelligence|
| [ ]    | Subset Drift BLEU Score                          |           | Robust Intelligence|
| [ ]    | Subset Drift Prediction Variance (Negative Labels)|          | Robust Intelligence|

 
# Pending Subset Operational Metrics

| Status | Metric Name                                      | Type              | File Link | Source             |
|--------|--------------------------------------------------|-------------------|-----------|--------------------|
| [ ]    | Subset Macro Precision                           | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Multiclass Accuracy                       | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Prediction Variance                       | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Mean Reciprocal Rank (MRR)                | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Prediction Variance (Positive Labels)     | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Rank Correlation                          | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Multiclass AUC                            | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Root-Mean-Squared Error (RMSE)            | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Average Confidence                        | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Average Rank                              | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Macro Recall                              | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Positive Prediction Rate                  | Subset Operational|           | Robust Intelligence|
| [ ]    | Subset Normalized Discounted Cumulative Gain (NDCG)| Subset Operational|         | Robust Intelligence|
| [ ]    | Subset Prediction Variance (Negative Labels)     | Subset Operational|           | Robust Intelligence|
