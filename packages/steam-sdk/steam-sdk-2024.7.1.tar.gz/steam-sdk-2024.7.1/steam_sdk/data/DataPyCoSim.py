from typing import Union, Dict

from pydantic import BaseModel, validator

from steam_sdk.data.DataModelCosim import General, sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE, PostProcessPyCoSim

class DataPyCoSim(BaseModel):
    """
    This class defines input file for PyCoSim of STEAM SDK
    """
    GeneralParameters: General = General()
    Simulations: Dict[str, Union[sim_FiQuS, sim_LEDET, sim_PSPICE, sim_XYCE]] = {}
    PostProcess: PostProcessPyCoSim = PostProcessPyCoSim()

    @validator('Simulations')
    def validate_Simulations(cls, Simulations):
        for key, value in Simulations.items():
            value.name = key
        return Simulations
