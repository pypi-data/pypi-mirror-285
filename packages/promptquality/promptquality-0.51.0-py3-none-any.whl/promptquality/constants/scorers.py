from enum import Enum
from typing import List


class Scorers(str, Enum):
    completeness_luna = "completeness_nli"
    completeness_plus = "completeness_gpt"
    context_adherence_luna = "adherence_nli"
    context_adherence_plus = "groundedness"
    context_relevance = "context_relevance"
    correctness = "factuality"
    chunk_attribution_utilization_luna = "chunk_attribution_utilization_nli"
    chunk_attribution_utilization_plus = "chunk_attribution_utilization_gpt"
    pii = "pii"
    prompt_injection = "prompt_injection"
    prompt_perplexity = "prompt_perplexity"
    sexist = "sexist"
    tone = "tone"
    toxicity = "toxicity"

    # Deprecated scorers.
    completeness_gpt = "completeness_gpt"
    context_adherence_gpt = "groundedness"
    chunk_attribution_utilization_gpt = "chunk_attribution_utilization_gpt"

    @staticmethod
    def deprecated_scorer_names() -> List["Scorers"]:
        return [
            Scorers.completeness_gpt,
            Scorers.context_adherence_gpt,
            Scorers.chunk_attribution_utilization_gpt,
        ]
