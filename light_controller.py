from dataclasses import dataclass
from espmega.espmegar3 import ESPMega

@dataclass
def LightEntity:
    controller: ESPMega
    pwm_channel: int