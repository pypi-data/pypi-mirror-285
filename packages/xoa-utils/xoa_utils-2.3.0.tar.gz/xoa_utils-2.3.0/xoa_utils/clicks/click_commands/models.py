from pydantic import BaseModel, Field
from enum import Enum
from typing import (
    Generator,
    Dict,
    List,
    Optional,
    Any
)
import json

class EntryDiscriminatorEnum(str, Enum):
    fsm = 'fsm'
    lt = 'lt'
    aneg_bp = 'aneg_bp'
    aneg_np = 'aneg_np'
    alg_result = 'alg_result'
    log = 'log'

class LogModuleEnum(str, Enum):
    ANEG = 'ANEG'
    LT = 'LT'

class BaseLogModel(BaseModel):
    lane: int
    module: str
    time: int
    type: str
    entry: Any

class EntryModel(BaseModel):
    entry_discriminator: str
    entry_value: Any

# entry_discriminator: alg_result
class PRBSLogModel(BaseModel):
    bits: int
    errors: int
    result: str

class AlgLogModel(BaseModel):
    ber: Optional[List[str]] = None
    cmd: str
    flags: Optional[List[str]] = None
    prbs: Optional[List[PRBSLogModel]] = None
    result: Optional[str] = None

class CmdEntryValueModel(BaseModel):
    cmds: List[AlgLogModel]

class LogResultValueModel(BaseModel):
    result: CmdEntryValueModel

# entry_discriminator: log
class LogEntryValueModel(BaseModel):
    log: str

# entry_discriminator: fsm
class FSMEntryValueModel(BaseModel):
    current: str
    event: str
    new: str

# entry_discriminator: lt, entry_value.log
class LTLogEntryValueModel(BaseModel):
    log: str

# entry_discriminator: lt, entry_value.direction
class LTControlModel(BaseModel):
    C_REQ: str
    C_SEL: str
    IC_REQ: str
    PAM_MOD: str

class LTStatusModel(BaseModel):
    C_ECH: str
    C_STS: str
    IC_STS: str
    PAM_MOD: str

class LTPktFieldModel(BaseModel):
    control: LTControlModel
    done: str
    locked: str
    status: LTStatusModel

class LTPktModel(BaseModel):
    fields: LTPktFieldModel
    prev_count: str
    value: str

class LTEntryValueModel(BaseModel):
    direction: str
    pkt: LTPktModel

# entry_discriminator: aneg_bp, entry_value.log
class AnegLogEntryValueModel(BaseModel):
    log: str
    pkt: Dict[str, Any]

# entry_discriminator: aneg_bp, entry_value.direction
class AnegBpFieldModel(BaseModel):
    Ack: str
    C: str
    EN: str
    NP: str
    RF: str
    TN: str
    ability: List[str]
    fec: List[str]

class AnegBpPktModel(BaseModel):
    fields: AnegBpFieldModel
    prev_count: str
    type: str
    value: str

class AnegBpEntryValueModel(BaseModel):
    direction: str
    pkt: AnegBpPktModel

# entry_discriminator: aneg_np, entry_value.direction
class FormattedMessageModel(BaseModel):
    message: Optional[str] = None
    value: str

class UnformattedMessageModel(BaseModel):
    ability: Optional[List[str]] = None
    fec: Optional[List[str]] = None
    message: Optional[str] = None
    value: str

class AnegNpFieldModel(BaseModel):
    Ack: str
    Ack2: str
    MP: str
    NP: str
    T: str
    formatted_message: Optional[FormattedMessageModel] = None
    unformatted_message: Optional[UnformattedMessageModel] = None

class AnegNpPktModel(BaseModel):
    fields: AnegNpFieldModel
    prev_count: str
    type: str
    value: str

class AnegNpEntryValueModel(BaseModel):
    direction: str
    pkt: AnegNpPktModel



# json_data = '{"entry":{"entry_discriminator":"alg_result","entry_value":{"result":{"cmds":[{"ber":["0","0","0"],"cmd":"SET PRESET_1","flags":["DONE","LOCK"],"prbs":[{"bits":4774354720,"errors":0,"result":"1.000e+00"}],"result":"success"},{"ber":["8664789","8664789"],"cmd":"SET PRESET_2","flags":["DONE","LOCK","LOST_LOCK"],"prbs":[{"bits":1186453120,"errors":8664789,"result":"7.303e-03"}],"result":"success"},{"ber":["500000000","500000000"],"cmd":"SET PRESET_3","flags":["DONE","LOST_LOCK"],"prbs":[{"bits":1000000000,"errors":500000000,"result":"5.000e-01"}],"result":"timeout"},{"ber":["0","0","0","0"],"cmd":"SET PRESET_1","flags":["DONE","LOCK","LOST_LOCK"],"prbs":[{"bits":3598300960,"errors":0,"result":"1.000e+00"}],"result":"success"},{"cmd":"LOCAL_TRAINED"}]}}},"lane":4,"module":"LT_ALG0","time":3445187171,"type":"trace"}'
# # print(BaseLogModel.model_validate_json(json_data))
# data = BaseLogModel(**json.loads(json_data))
# print(data.lane)
# print(data.time)
# print(data.module)
# print(data.type)
# print(data.entry)
# data = EntryModel(**data.entry)
# print(data.entry_discriminator)
# print(data.entry_value)

# if data.entry_discriminator == EntryDiscriminatorEnum.alg_result.name:
#     if data.entry_value != None:
#         data = LogEntryValueModel(**data.entry_value)
#         for cmd in data.result.cmds:
#             # print(f"cmd: {cmd.cmd}, result: {cmd.result}, prbs: {cmd.prbs}, flags: {cmd.flags}")
#             if cmd.result != None:
#                 print(f"cmd: {cmd.cmd}, result: {cmd.result}, prbs: bits={cmd.prbs[0].bits:} errors={cmd.prbs[0].errors} ber={cmd.prbs[0].result}, flags: {cmd.flags}\n{'':<37}")
#             else:
#                 print(f"cmd: {cmd.cmd}")
