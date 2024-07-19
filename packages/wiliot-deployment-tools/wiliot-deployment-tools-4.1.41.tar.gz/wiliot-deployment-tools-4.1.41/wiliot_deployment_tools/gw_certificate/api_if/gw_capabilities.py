from dataclasses import dataclass
from typing import Literal

@dataclass
class GWCapabilities:
    tagMetadataCouplingSupported: bool = False
    downlinkSupported: bool = False
    bridgeOtaUpgradeSupported: bool = False
    fwUpgradeSupported: bool = False
    geoLocationSupport: bool = False
    
    @staticmethod
    def get_capabilities():
        return list(GWCapabilities.__dataclass_fields__.keys())
    
    def set_capability(self, capability, value:bool):
        assert capability in GWCapabilities.get_capabilities(), f'{capability} is not a valid capability'
        setattr(self, capability, value)