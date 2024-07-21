from typing import Optional, Tuple, Type

from pydantic import BaseModel


class TBaseModel(BaseModel):
    def totuple(self) -> Tuple:
        raise NotImplementedError()

    @staticmethod
    def fromtuple(x: Tuple):
        raise NotImplementedError()


class BaseRobotParams(TBaseModel):
    pass


class BaseRobotState(TBaseModel):
    pass


class BaseRobotInputs(TBaseModel):
    pass


class BaseRobot(BaseModel):
    params: Type[BaseRobotParams]
    inputs: Type[BaseRobotInputs]
    state: Type[BaseRobotState]


class BaseRobotModel:

    base_robot: BaseRobot

    def reset(self) -> None:
        raise NotImplementedError()

    def run(
        self,
        state: BaseRobotState,
        inputs: BaseRobotInputs,
        params: Optional[BaseRobotParams] = None,
    ) -> BaseRobotState:
        raise NotImplementedError()
