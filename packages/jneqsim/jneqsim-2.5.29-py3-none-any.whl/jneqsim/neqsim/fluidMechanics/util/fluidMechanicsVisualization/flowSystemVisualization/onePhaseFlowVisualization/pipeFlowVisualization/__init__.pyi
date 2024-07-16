
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import jneqsim.neqsim.fluidMechanics.util.fluidMechanicsVisualization.flowSystemVisualization.onePhaseFlowVisualization
import typing



class PipeFlowVisualization(jneqsim.neqsim.fluidMechanics.util.fluidMechanicsVisualization.flowSystemVisualization.onePhaseFlowVisualization.OnePhaseFlowVisualization):
    bulkComposition: typing.MutableSequence[typing.MutableSequence[typing.MutableSequence[float]]] = ...
    @typing.overload
    def __init__(self): ...
    @typing.overload
    def __init__(self, int: int, int2: int): ...
    def calcPoints(self, string: typing.Union[java.lang.String, str]) -> None: ...
    def displayResult(self, string: typing.Union[java.lang.String, str]) -> None: ...
    def setPoints(self) -> None: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.fluidMechanics.util.fluidMechanicsVisualization.flowSystemVisualization.onePhaseFlowVisualization.pipeFlowVisualization")``.

    PipeFlowVisualization: typing.Type[PipeFlowVisualization]
