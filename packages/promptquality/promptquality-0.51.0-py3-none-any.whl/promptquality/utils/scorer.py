from typing import List, Optional, Tuple, Union
from warnings import warn

from promptquality.constants.scorers import Scorers
from promptquality.registered_scorers import list_registered_scorers
from promptquality.types.custom_scorer import CustomScorer
from promptquality.types.registered_scorers import RegisteredScorer


def bifurcate_scorers(
    scorers: Optional[List[Union[Scorers, CustomScorer, RegisteredScorer, str]]] = None
) -> Tuple[List[Scorers], List[CustomScorer], List[RegisteredScorer]]:
    if scorers is None:
        return [], [], []
    galileo_scorers: List[Scorers] = []
    custom_scorers: List[CustomScorer] = []
    registered_scorers: List[RegisteredScorer] = []
    possibly_registered_scorers = []
    for scorer in scorers:
        if isinstance(scorer, Scorers):
            if scorer in Scorers.deprecated_scorer_names():
                warn(
                    (
                        f"{scorer.name} is a deprecated name. and will be removed on July 15, 2024. "
                        "Please use the scorer name ending in _plus rather than _gpt"
                    )
                )
            galileo_scorers.append(scorer)
        elif isinstance(scorer, CustomScorer):
            custom_scorers.append(scorer)
        elif isinstance(scorer, RegisteredScorer):
            registered_scorers.append(scorer)
        elif isinstance(scorer, str):
            possibly_registered_scorers.append(scorer)
        else:
            raise ValueError(f"Unknown scorer type: {type(scorer)}.")
    if possibly_registered_scorers:
        existing_registered_scorers = list_registered_scorers()
        existing_registered_scorers_map = {scorer.name: scorer for scorer in existing_registered_scorers}
        for scorer in possibly_registered_scorers:
            if scorer in existing_registered_scorers_map:
                registered_scorers.append(existing_registered_scorers_map[scorer])
            else:
                warn(f"Scorer {scorer} is not a Galileo-provided, custom or registered  scorer, skipping.")
    return galileo_scorers, custom_scorers, registered_scorers
