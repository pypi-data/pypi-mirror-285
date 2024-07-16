from enum import Enum


class DefaultMetric(Enum):
    # Unary metrics (output only)
    TOXICITY = "toxicity"
    SENTIMENT = "sentiment"

    # Binary metrics - output vs. groundtruth
    BLEU = "bleu"
    ROUGE = "rouge1"
    SIMILARITY = "similarity"
    EXACT_MATCH = "exact_match"

    # Binary metrics - output vs. input
    RELEVANCE = "relevance"

    # Ternary metrics - output vs. groundtruth & input
    FAITHFULNESS = "faithfulness"
    QA = "qa"
    HUMAN_VS_AI = "human_vs_ai"


DEFAULT_METRICS_WITH_DESCRIPTIONS: dict[str, str] = {
    DefaultMetric.TOXICITY.value: "Give a value of 1.0 (toxic) or 0.0 (non-toxic) for output text.",
    DefaultMetric.SENTIMENT.value: "Give a value between 0.0 (not happy) to 1.0 (happy) for output text.",
    DefaultMetric.BLEU.value: "Give the BLUE score between output vs. ground truth.",
    DefaultMetric.ROUGE.value: "Give the ROUGE-1 score between output vs. ground truth.",
    DefaultMetric.SIMILARITY.value: "Give a value score between 0.0 (not similar) to 1.0 (exact match) between output vs. ground truth.",
    DefaultMetric.EXACT_MATCH.value: "Give a value of 1.0 (exact match) or 0.0 (not an exact match) between output and ground truth.",
    DefaultMetric.RELEVANCE.value: "Give a value of 1.0 (relevant) or 0.0 (not relevant) between output text and input prompt.",
    # "Given a sequence of outputs, "
    DefaultMetric.FAITHFULNESS.value: "Give a value between 0.0 (not faithful) to 1.0 (faithful) between output text, input prompt and ground truth. See https://blog.lastmileai.dev/harder-better-faster-stronger-llm-hallucination-detection-for-real-world-rag-part-i-949248f0ad94 for details.",
    DefaultMetric.QA.value: "Give a value of 1.0 (correct) or 0.0 (incorrect) between output text, input prompt and ground truth.",
    DefaultMetric.HUMAN_VS_AI.value: "Give a value of 1.0 (matches human response) or 0.0 (does not match human response) between output text, input prompt and human-labelled ground truth.",
}
