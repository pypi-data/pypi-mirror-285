from typing import List, Tuple


class BaseCost:

    def __init__(self, model) -> None:
        pass

    def cost(
        self,
        input_sequence: List[Tuple],
        current_state_tuple: Tuple,
        desired_state_sequence: List[Tuple],
    ) -> float:
        raise NotImplementedError()
