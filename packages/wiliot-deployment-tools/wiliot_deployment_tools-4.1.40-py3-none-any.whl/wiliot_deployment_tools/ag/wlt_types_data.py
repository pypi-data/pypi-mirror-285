from typing import Literal
from wiliot_deployment_tools.ag.wlt_types import WltPkt
from wiliot_deployment_tools.ag.ut_defines import *
from wiliot_deployment_tools.ag.wlt_types_ag import *

DATA_DEFAULT_GROUP_ID = 0x020000

class GenericPacket():
    def __init__(self, payload=0, pkt_id=0):
        self.payload = payload
        self.pkt_id = pkt_id

    def __eq__(self, other):
        if isinstance(other, GenericV7):
            return (
                self.payload == other.payload and
                self.pkt_id == other.pkt_id
            )
        return False

    def dump(self):
        string = bitstruct.pack("u160u32", self.payload, self.pkt_id)
        return string.hex().upper()

    def set(self, string):
        d = bitstruct.unpack("u160u32", binascii.unhexlify(string))
        self.payload = d[0]
        self.pkt_id = d[1]


class DataPacket(WltPkt):
    def __init__(self, group_id=None, service_uuid:Literal["tag", "bridge"]='bridge', *args, **kwargs):
        if service_uuid == 'bridge':
            uuid_msb=HDR_DEFAULT_BRG_UUID_MSB
            uuid_lsb=HDR_DEFAULT_BRG_UUID_LSB
        else:
            uuid_msb=HDR_DEFAULT_TAG_UUID_MSB
            uuid_lsb=HDR_DEFAULT_TAG_UUID_LSB
        if group_id is None:
            group_id = DATA_DEFAULT_GROUP_ID
        else:
            group_id = group_id
        super().__init__(hdr=Hdr(uuid_msb=uuid_msb, uuid_lsb=uuid_lsb, group_id=group_id), 
                         data_hdr=DataHdr(uuid_msb=uuid_msb, uuid_lsb=uuid_lsb, 
                                          group_id_minor=((group_id & 0xFFFF00) >> 8), group_id_major=(group_id & 0x0000FF)),
                         generic=GenericPacket(), *args, **kwargs)
        

    def set(self, string):
        if not string.startswith("1E16"):
            string = "1E16" + string
        self.hdr.set(string[0:14])
        if self.hdr.group_id == DATA_DEFAULT_GROUP_ID:
            self.generic = GenericPacket()
            self.generic.set(string[14:62])
        else:
            super().set(string)
            
    def dump(self):
        return super().dump()
    
    def __repr__(self) -> str:
        return self.dump()