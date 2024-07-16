
import sys
if sys.version_info >= (3, 8):
    from typing import Protocol
else:
    from typing_extensions import Protocol

import java.lang
import jneqsim.neqsim.processSimulation.processEquipment
import jneqsim.neqsim.processSimulation.processSystem
import jneqsim.neqsim.thermo.system
import typing



class Report:
    @typing.overload
    def __init__(self, processEquipmentBaseClass: jneqsim.neqsim.processSimulation.processEquipment.ProcessEquipmentBaseClass): ...
    @typing.overload
    def __init__(self, processModule: jneqsim.neqsim.processSimulation.processSystem.ProcessModule): ...
    @typing.overload
    def __init__(self, processModuleBaseClass: jneqsim.neqsim.processSimulation.processSystem.ProcessModuleBaseClass): ...
    @typing.overload
    def __init__(self, processSystem: jneqsim.neqsim.processSimulation.processSystem.ProcessSystem): ...
    @typing.overload
    def __init__(self, systemInterface: jneqsim.neqsim.thermo.system.SystemInterface): ...
    def generateJsonReport(self) -> java.lang.String: ...


class __module_protocol__(Protocol):
    # A module protocol which reflects the result of ``jp.JPackage("jneqsim.neqsim.processSimulation.util.report")``.

    Report: typing.Type[Report]
