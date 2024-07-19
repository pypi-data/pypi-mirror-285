from __future__ import annotations
import asyncclick as ac
import json
import typing as t
from xoa_driver.hlfuncs import anlt as anlt_utils
from xoa_utils.clicks import click_backend as cb
from xoa_utils.clis import (
    format_recovery,
    format_port_status,
    format_strict,
    format_log_control,
    dominant_and_recessive,
)
from xoa_driver.enums import AnLtLogControl
from xoa_utils.clicks.click_commands.group import xoa_util
from xoa_utils.clicks import click_help as h
from xoa_utils.cmds import CmdContext
from enum import Enum
from xoa_utils.clicks.click_commands.models import *


class ASCIIStyle(Enum):
    DARKRED = "\033[31m"
    DARKGREEN = "\033[32m"
    DARKYELLOW = "\033[33m"
    DARKBLUE = "\033[34m"
    DARKMAGENTA = "\033[35m"
    DARKCYAN = "\033[36m"

    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"

    DARKRED_BG = "\033[41m"
    DARKGREEN_BG = "\033[42m"
    DARKYELLOW_BG = "\033[43m"
    DARKBLUE_BG = "\033[44m"
    DARKMAGENTA_BG = "\033[45m"
    DARKCYAN_BG = "\033[46m"

    RED_BG = "\033[101m"
    GREEN_BG = "\033[102m"
    YELLOW_BG = "\033[103m"
    BLUE_BG = "\033[104m"
    MAGENTA_BG = "\033[105m"
    CYAN_BG = "\033[106m"

    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    END = "\033[0m"


@xoa_util.group(cls=cb.XenaGroup)
def anlt():
    """
    ANLT group
    """


# --------------------------
# command: autorestart
# --------------------------
@anlt.command(cls=cb.XenaCommand, name="autorestart")
@ac.option("--link-down/--no-link-down", type=ac.BOOL, help=h.HELP_ANLT_RESTART_LINK_DOWN_ON, default=False)
@ac.option("--lt-fail/--no-lt-fail", type=ac.BOOL, help=h.HELP_ANLT_RESTART_LT_FAIL_ON, default=False)
@ac.pass_context
async def autorestart(context: ac.Context, link_down: bool, lt_fail: bool) -> str:
    """
    Control AN/LT autorestart
    """
    storage: CmdContext = context.obj

    port_obj = storage.retrieve_port()
    await anlt_utils.anlt_link_recovery(port_obj, link_down, lt_fail)
    return format_recovery(storage, link_down, lt_fail)


# --------------------------
# command: status
# --------------------------
@anlt.command(cls=cb.XenaCommand, name="status")
@ac.pass_context
async def status(context: ac.Context) -> str:
    """
    Show AN/LT status
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    status_dic = await anlt_utils.anlt_status(port_obj)
    port_id = storage.retrieve_port_str()
    return format_port_status(status_dic, storage)


# --------------------------
# command: start
# --------------------------
@anlt.command(cls=cb.XenaCommand, name="start")
@ac.pass_context
async def start(context: ac.Context) -> str:
    """
    Apply and start AN/LT
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    an_enable = storage.retrieve_an_enable()
    lt_enable = storage.retrieve_lt_enable()
    an_allow_loopback = storage.retrieve_an_loopback()
    lt_preset0 = storage.retrieve_lt_preset0()
    lt_initial_modulations = storage.retrieve_lt_initial_mod()
    lt_interactive = storage.retrieve_lt_interactive()
    lt_algorithm = storage.retrieve_lt_algorithm()
    should_lt_timeout = storage.retrieve_lt_timeout()
    await anlt_utils.anlt_start(
        port_obj,
        an_enable,
        lt_enable,
        an_allow_loopback,
        lt_preset0,
        lt_initial_modulations,
        lt_interactive,
        lt_algorithm,
        should_lt_timeout,
    )
    return ""

# --------------------------
# command: stop
# --------------------------
@anlt.command(cls=cb.XenaCommand, name="stop")
@ac.pass_context
async def stop(context: ac.Context) -> str:
    """
    Stop AN/LT
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    await anlt_utils.anlt_stop(
        port_obj,
    )
    return ""

# --------------------------
# command: log
# --------------------------
@anlt.command(cls=cb.XenaCommand, name="log")
@ac.option(
    "-f", "--filename", type=ac.STRING, help=h.HELP_ANLT_LOG_FILENAME, default=""
)
@ac.option(
    "-r", "--read", is_flag=True, help=h.HELP_ANLT_READ, default=False
)
@ac.option(
    "-k",
    "--keep",
    type=ac.Choice(["all", "an", "lt"]),
    help=h.HELP_ANLT_LOG_KEEP,
    default="all",
)
@ac.option("-s", "--serdes", type=ac.STRING, help=h.HELP_ANLT_LOG_SERDES, default="")
@ac.option("-p", "--polls", type=ac.INT, help=h.HELP_ANLT_LOG_POLLS, default=10)
@ac.pass_context
async def log(ctx: ac.Context, filename: str, read: bool, keep: str, serdes: str, polls: int) -> str:
    """
    AN/LT logging
    """

    def _filter_log(log: str, keep: str, serdes: list[int]) -> list[dict]:
        all_logs = []
        for lg in log.split("\n"):
            try:
                content = json.loads(lg)
                log_serdes = content["lane"]
                module = content["module"]

                serdes_in = (serdes and log_serdes in serdes) or (not serdes)
                keep_in = any(
                    (
                        keep == "an" and "AN" in module,
                        keep == "lt" and "LT" in module,
                        keep == "all",
                    )
                )
                if serdes_in and keep_in:
                    all_logs.append(content)

            except Exception:
                pass
        return all_logs

    def _dict_get(dic: dict, *keys: str) -> t.Any:
        current = dic
        for k in keys:
            current = current.get(k, "")
            if current == "":
                break
        return current

    def _flatten(dic: dict[str, str]) -> str:
        return "".join((f"{k}: {v:<7}" for k, v in dic.items()))

    def _ascii_styler(str: str, fg_style: list[ASCIIStyle]) -> str:
        style = "".join(s.value for s in fg_style)
        return f"{style}{str}{ASCIIStyle.END.value}"

    def _direction_styler(str: str) -> str:
        # for log2 only
        if str == "tx":
            str = _ascii_styler(
                str.upper(), [ASCIIStyle.DARKBLUE_BG]
            )
        else:
            str = _ascii_styler(
                str.upper(), [ASCIIStyle.DARKGREEN_BG]
            )
        return str

    def _true_false_styler(str: str) -> str:
        # for log2 only
        if str == "true":
            str = _ascii_styler(str, [ASCIIStyle.GREEN_BG])
        else:
            str = _ascii_styler(str, [ASCIIStyle.RED_BG])
        return str
    
    def _an_page_styler(str: str) -> str:
        # for log2 only
        if str == "base page":
            str = _ascii_styler(str.title(), [ASCIIStyle.DARKBLUE_BG])
        else:
            str = _ascii_styler(str.title(), [ASCIIStyle.BLUE_BG])
        return str
    
    def _ber_styler(str: str) -> str:
        # for log2 only
        return _ascii_styler(str, [ASCIIStyle.YELLOW])
    
    def _beautify(filtered: list[dict], version: int) -> str:
        real = []
        if version <= 1:
            for i in filtered:
                b_str = ""

                log_time = _dict_get(i, "time")
                log_entry = _dict_get(i, "entry")
                log_type = _dict_get(i, "type")
                log_m = _dict_get(i, "module")
                log_log = _dict_get(i, "entry", "log")
                log_serdes = _dict_get(i, "lane")
                log_m = _dict_get(i, "module")
                log_m = _dict_get(i, "module")
                log_event = _dict_get(i, "entry", "fsm", "event")
                log_current = _dict_get(i, "entry", "fsm", "current")
                log_new = _dict_get(i, "entry", "fsm", "new")
                log_direction = _dict_get(i, "entry", "direction")
                if log_direction == "tx":
                    log_direction = _ascii_styler(
                        log_direction.upper(), [ASCIIStyle.DARKBLUE_BG]
                    )
                else:
                    log_direction = _ascii_styler(
                        log_direction.upper(), [ASCIIStyle.DARKGREEN_BG]
                    )

                log_value = _dict_get(i, "entry", "pkt", "value")
                log_ptype = _dict_get(i, "entry", "pkt", "type")
                log_pstate = _dict_get(i, "entry", "pkt", "state")
                log_np = _dict_get(i, "entry", "pkt", "fields", "NP")
                log_ack = _dict_get(i, "entry", "pkt", "fields", "Ack")
                log_rf = _dict_get(i, "entry", "pkt", "fields", "RF")
                log_tn = _dict_get(i, "entry", "pkt", "fields", "TN")
                log_en = _dict_get(i, "entry", "pkt", "fields", "EN")
                log_c = _dict_get(i, "entry", "pkt", "fields", "C")
                log_fec = _dict_get(i, "entry", "pkt", "fields", "fec")
                log_ab = _dict_get(i, "entry", "pkt", "fields", "ability")
                log_pkt_ctrl = _dict_get(i, "entry", "pkt", "fields", "control")
                log_pkt_status = _dict_get(i, "entry", "pkt", "fields", "status")
                log_pkt_locked = _dict_get(i, "entry", "pkt", "fields", "locked")
                log_mp = _dict_get(i, "entry", "pkt", "fields", "MP")
                log_ack2 = _dict_get(i, "entry", "pkt", "fields", "Ack2")
                log_t = _dict_get(i, "entry", "pkt", "fields", "T")
                log_fmt_v = _dict_get(
                    i, "entry", "pkt", "fields", "formatted message", "value"
                )
                log_fmt_msg = _dict_get(
                    i, "entry", "pkt", "fields", "formatted message", "message"
                )
                log_ufmt_v = _dict_get(
                    i, "entry", "pkt", "fields", "un-formatted message", "value"
                )
                log_ufmt_msg = _dict_get(
                    i, "entry", "pkt", "fields", "un-formatted message", "message"
                )
                log_ufmt_fec = _dict_get(
                    i, "entry", "pkt", "fields", "un-formatted message", "fec"
                )
                log_ufmt_ab = _dict_get(
                    i, "entry", "pkt", "fields", "un-formatted message", "ability"
                )
                log_errors = _dict_get(i, "entry", "pkt", "errors")

                if log_pkt_locked == "true":
                    log_pkt_locked = _ascii_styler(log_pkt_locked, [ASCIIStyle.GREEN_BG])
                else:
                    log_pkt_locked = _ascii_styler(log_pkt_locked, [ASCIIStyle.RED_BG])

                log_pkt_done = _dict_get(i, "entry", "pkt", "fields", "done")
                if log_pkt_done == "true":
                    log_pkt_done = _ascii_styler(log_pkt_done, [ASCIIStyle.GREEN_BG])
                else:
                    log_pkt_done = _ascii_styler(log_pkt_done, [ASCIIStyle.RED_BG])

                log_pkt_value = _dict_get(i, "entry", "pkt", "value")

                serdes_str = f"(S{log_serdes})," if "LT" in log_m else ","
                common = f"{log_time/1000000:.6f}, {log_m}{serdes_str}"

                if log_type == "debug":
                    b_str = f"{common:<32}{'DBG:':<5}{log_log}"
                elif log_type == "fsm":
                    b_str = (
                        f"{common:<32}{'FSM:':<5}({log_event}) {log_current} -> {log_new}"
                    )
                elif log_type == "trace" and "log" in log_entry:
                    b_str = f"{common:<32}{'MSG:':<5}{log_log}"
                elif log_type == "trace" and "direction" in log_entry and "LT" not in log_m:
                    if log_pstate == "new" or log_pstate == "":
                        if log_ptype == "base page":
                            b_str = f"{common:<32}{(log_direction + ':'):<14}{log_value}, {log_ptype}, NP:{int(log_np, 0)}, ACK:{int(log_ack, 0)}, RF:{int(log_rf, 0)}, TN:{int(log_tn, 0)}, EN:{int(log_en ,0)}, C:{int(log_c, 0)}\n{'':<37}FEC:{log_fec}\n{'':<37}ABILITY:{log_ab}"
                        else:
                            if log_fmt_v:
                                b_str = f"{common:<32}{(log_direction + ':'):<14}{log_value}, {log_ptype}, NP:{int(log_np, 0)}, ACK:{int(log_ack, 0)}, MP:{int(log_mp, 0)}, ACK2:{int(log_ack2, 0)}, T:{int(log_t ,0)}\n{'':<37}Formatted message:\n{'':<37}Value:{log_fmt_v}, Msg:{log_fmt_msg}"
                            else:
                                b_str = f"{common:<32}{(log_direction + ':'):<14}{log_value}, {log_ptype}, NP:{int(log_np, 0)}, ACK:{int(log_ack, 0)}, MP:{int(log_mp, 0)}, ACK2:{int(log_ack2, 0)}, T:{int(log_t ,0)}\n{'':<37}Unformatted message:\n{'':<37}Value:{log_ufmt_v}, Msg:{log_ufmt_msg}\n{'':<37}FEC:{log_ufmt_fec}\n{'':<37}ABILITY:{log_ufmt_ab}"
                        if log_errors:
                            b_str += "\n" + f"{'':<37}" + _ascii_styler("ERRORS:", [ASCIIStyle.RED_BG]) + f"{log_errors}"

                elif log_type == "trace" and "direction" in log_entry and "LT" in log_m:
                    if log_pstate == "new" or log_pstate == "":
                        b_str = f"{common:<32}{(log_direction + ':'):<14}{log_pkt_value}, LOCKED={log_pkt_locked}, TRAINED={log_pkt_done}\n{'':<37}{_flatten(log_pkt_ctrl)}\n{'':<37}{_flatten(log_pkt_status)}"
                        if log_errors:
                            b_str += "\n" + f"{'':<37}" + _ascii_styler("ERRORS:", [ASCIIStyle.RED_BG]) + f"{log_errors}"
                elif log_type == "xla":
                    log_xla = _ascii_styler("XLA", [ASCIIStyle.RED_BG])
                    b_str = f"{common:<32}{(log_xla + ': '):<5}{log_log}"

                if b_str:
                    real.append(b_str)
        else:
            for i in filtered:
                b_str = ""

                data = BaseLogModel(**i)
                log_time = data.time
                log_m = data.module
                log_serdes = data.lane
                log_type = data.type
                log_entry = data.entry

                serdes_str = f"(S{log_serdes})," if "LT" in log_m else ","
                common = f"{log_time/1000000:.6f}, {log_m}{serdes_str}"

                _entry_data = EntryModel(**log_entry)
                _entry_discriminator = _entry_data.entry_discriminator
                _entry_value = _entry_data.entry_value

                if _entry_discriminator == EntryDiscriminatorEnum.fsm.name:
                    data = FSMEntryValueModel(**_entry_value)
                    log_event = data.event
                    log_current = data.current
                    log_new = data.new
                    b_str = f"{common:<32}{'FSM:':<5}({log_event}) {log_current} -> {log_new}"

                elif _entry_discriminator == EntryDiscriminatorEnum.alg_result.name:
                    log_log = ""
                    if _entry_value != None:
                        data = LogResultValueModel(**_entry_value)
                        for cmd in data.result.cmds:
                            if cmd.result != None:
                                log_log += f"cmd: {cmd.cmd}, result: {cmd.result}, prbs: bits={cmd.prbs[0].bits:} errors={cmd.prbs[0].errors} ber={_ber_styler(cmd.prbs[0].result)}, flags: {cmd.flags}\n{'':<37}"
                            else:
                                log_log += f"cmd: {cmd.cmd}"
                    else:
                        log_log = ""
                    b_str = f"{common:<32}{'MSG:':<5}{log_log}"

                elif _entry_discriminator == EntryDiscriminatorEnum.aneg_bp.name:
                    if "log" in _entry_value.keys():
                        data = AnegLogEntryValueModel(**_entry_value)
                        log_log = data.log
                        b_str = f"{common:<32}{'MSG:':<5}{log_log}"
                    else:
                        data = AnegBpEntryValueModel(**_entry_value)
                        log_direction = _direction_styler(data.direction)
                        log_value = data.pkt.value
                        log_ptype = _an_page_styler(data.pkt.type)
                        log_prev_count = data.pkt.prev_count

                        log_np = data.pkt.fields.NP
                        log_ack = data.pkt.fields.Ack
                        log_rf = data.pkt.fields.RF
                        log_tn = data.pkt.fields.TN
                        log_en = data.pkt.fields.EN
                        log_c = data.pkt.fields.C
                        log_fec = data.pkt.fields.fec
                        log_ab = data.pkt.fields.ability

                        b_str = f"{common:<32}{(log_direction + ':'):<14}{log_value}, {log_ptype}\n{'':<37}NP:{int(log_np, 0)}, ACK:{int(log_ack, 0)}, RF:{int(log_rf, 0)}, TN:{int(log_tn, 0)}, EN:{int(log_en ,0)}, C:{int(log_c, 0)}\n{'':<37}FEC:    {log_fec}\n{'':<37}ABILITY:{log_ab}"

                elif _entry_discriminator == EntryDiscriminatorEnum.aneg_np.name:
                    if "log" in _entry_value.keys():
                        data = AnegLogEntryValueModel(**_entry_value)
                        log_log = data.log
                        b_str = f"{common:<32}{'MSG:':<5}{log_log}"
                    else:
                        data = AnegNpEntryValueModel(**_entry_value)
                        log_direction = _direction_styler(data.direction)
                        log_value = data.pkt.value
                        log_ptype = _an_page_styler(data.pkt.type)
                        log_prev_count = data.pkt.prev_count

                        log_np = data.pkt.fields.NP
                        log_ack = data.pkt.fields.Ack
                        log_mp = data.pkt.fields.MP
                        log_ack2 = data.pkt.fields.Ack2
                        log_t = data.pkt.fields.T
                        
                        if (data.pkt.fields.formatted_message != None):
                            log_fmt_v = data.pkt.fields.formatted_message.value
                            log_fmt_msg = data.pkt.fields.formatted_message.message

                            b_str = f"{common:<32}{(log_direction + ':'):<14}{log_value}, {log_ptype}\n{'':<37}NP:{int(log_np, 0)}, ACK:{int(log_ack, 0)}, MP:{int(log_mp, 0)}, ACK2:{int(log_ack2, 0)}, T:{int(log_t ,0)}\n{'':<37}Formatted message:\n{'':<37}Value:{log_fmt_v}, Msg:{log_fmt_msg}"

                        elif (data.pkt.fields.unformatted_message != None):
                            log_ufmt_v = data.pkt.fields.unformatted_message.value
                            log_ufmt_msg = data.pkt.fields.unformatted_message.message
                            log_ufmt_fec = data.pkt.fields.unformatted_message.fec
                            log_ufmt_ab = data.pkt.fields.unformatted_message.ability

                            b_str = f"{common:<32}{(log_direction + ':'):<14}{log_value}, {log_ptype}\n{'':<37}NP:{int(log_np, 0)}, ACK:{int(log_ack, 0)}, MP:{int(log_mp, 0)}, ACK2:{int(log_ack2, 0)}, T:{int(log_t ,0)}\n{'':<37}Unformatted message:"
                            
                            if log_ufmt_v != None:
                                b_str += f"\n{'':<37}Value:   {log_ufmt_v}"
                            if log_ufmt_msg != None:
                                b_str += f"\n{'':<37}Msg:     {log_ufmt_msg}"
                            if log_ufmt_fec != None:
                                b_str += f"\n{'':<37}FEC:     {log_ufmt_fec}"
                            if log_ufmt_ab != None:
                                b_str += f"\n{'':<37}ABILITY: {log_ufmt_ab}"

                elif _entry_discriminator == EntryDiscriminatorEnum.lt.name:
                    if "log" in _entry_value.keys():
                        data = LTLogEntryValueModel(**_entry_value)
                        log_log = data.log
                        b_str = f"{common:<32}{'MSG:':<5}{log_log}"
                    else:
                        data = LTEntryValueModel(**_entry_value)
                        log_direction = _direction_styler(data.direction)
                        log_value = data.pkt.value
                        log_prev_count = data.pkt.prev_count

                        log_pkt_locked = _true_false_styler(data.pkt.fields.locked)
                        log_pkt_done = _true_false_styler(data.pkt.fields.done)
                        log_pkt_ctrl = data.pkt.fields.control.model_dump()
                        log_pkt_status = data.pkt.fields.status.model_dump()

                        b_str = f"{common:<32}{(log_direction + ':'):<14}{log_value}, LOCKED={log_pkt_locked}, TRAINED={log_pkt_done}\n{'':<37}{_flatten(log_pkt_ctrl)}\n{'':<37}{_flatten(log_pkt_status)}"

                elif _entry_discriminator == EntryDiscriminatorEnum.log.name:
                    data = LogEntryValueModel(**_entry_value)
                    log_str = data.log
                    b_str = f"{common:<32}{'DBG:':<5} {log_str}"

                if b_str:
                    real.append(b_str)
        
        return "\n".join(real)

    async def read_log(storage: CmdContext, keep: str, serdes: list[int], version: int) -> str:
        port_obj = storage.retrieve_port()
        log_str = await anlt_utils.anlt_log(port_obj)
        filtered = _filter_log(log_str, keep, serdes)
        string = _beautify(filtered, version)
        if not read and filename and log_str:
            with open(filename, "a") as f:
                f.write(f"{log_str}\n")
        return string
    
    def load_log(filename: str, keep: str, serdes: list[int]) -> str:
        with open(filename, "r") as f:
            log_str = f.read()
            if "entry_discriminator" in log_str:
                _log_ver = 2
            else:
                _log_ver = 1
        filtered = _filter_log(log_str, keep, serdes)
        string = _beautify(filtered, _log_ver)
        return string
        

    real_serdes_list = [int(i.strip()) for i in serdes.split(",")] if serdes else []
    
    if read:
        return load_log(filename=filename, keep=keep, serdes=real_serdes_list)
        # return await log(storage=None, filename=filename, read=read, keep=keep, serdes=real_serdes_list, version=2)
    else:
        storage: CmdContext = ctx.obj
        _xs_version = storage.retrieve_tester_version()
        _interval = 1/polls
        if _xs_version[0] >= 465:
            _log_ver = 2
        else:
            _log_ver = 1
        kw = {"keep": keep, "serdes": real_serdes_list, "version": _log_ver}
        storage.set_loop_coro(coro=read_log, interval=_interval, dic=kw)
        return ""


# --------------------------
# command: strict
# --------------------------
@anlt.command(cls=cb.XenaCommand, name="strict")
@ac.option("--on/--off", type=ac.BOOL, help=h.HELP_STRICT_ON, default=True)
@ac.pass_context
async def strict(context: ac.Context, on: bool) -> str:
    """
    AN/LT strict mode

        Enable/disable ANLt strict mode. If enable, errored frames will be ignored.
    """
    storage: CmdContext = context.obj

    port_obj = storage.retrieve_port()
    await anlt_utils.anlt_strict(port_obj, on)
    return format_strict(storage, on)

# --------------------------
# command: log-ctrl
# --------------------------
@anlt.command(cls=cb.XenaCommand, name="logctrl")
@ac.option("-D", "--debug", help=h.HELP_LOG_CONTROL_DEBUG_ON, is_flag=True)
@ac.option("-d", "--no-debug", help=h.HELP_LOG_CONTROL_DEBUG_OFF, is_flag=True)

@ac.option("-A", "--an-trace", help=h.HELP_LOG_CONTROL_AN_TRACE_ON, is_flag=True)
@ac.option("-a", "--no-an-trace", help=h.HELP_LOG_CONTROL_AN_TRACE_OFF, is_flag=True)

@ac.option("-L", "--lt-trace", help=h.HELP_LOG_CONTROL_LT_TRACE_ON, is_flag=True)
@ac.option("-l", "--no-lt-trace", help=h.HELP_LOG_CONTROL_LT_TRACE_OFF, is_flag=True)

@ac.option("-G", "--alg-trace", help=h.HELP_LOG_CONTROL_ALG_TRACE_ON, is_flag=True)
@ac.option("-g", "--no-alg-trace", help=h.HELP_LOG_CONTROL_ALG_TRACE_OFF, is_flag=True)

@ac.option("-P", "--fsm-port", help=h.HELP_LOG_CONTROL_FSM_PORT_ON, is_flag=True)
@ac.option("-p", "--no-fsm-port", help=h.HELP_LOG_CONTROL_FSM_PORT_OFF, is_flag=True)

@ac.option("-N", "--fsm-an", help=h.HELP_LOG_CONTROL_FSM_AN_ON, is_flag=True)
@ac.option("-n", "--no-fsm-an", help=h.HELP_LOG_CONTROL_FSM_AN_OFF, is_flag=True)

@ac.option("-M", "--fsm-an-stimuli", help=h.HELP_LOG_CONTROL_FSM_AN_STIMULI_ON, is_flag=True)
@ac.option("-m", "--no-fsm-an-stimuli", help=h.HELP_LOG_CONTROL_FSM_AN_STIMULI_OFF, is_flag=True)

@ac.option("-T", "--fsm-lt", help=h.HELP_LOG_CONTROL_FSM_LT_ON, is_flag=True)
@ac.option("-t", "--no-fsm-lt", help=h.HELP_LOG_CONTROL_FSM_LT_OFF, is_flag=True)

@ac.option("-C", "--fsm-lt-coeff", help=h.HELP_LOG_CONTROL_FSM_LT_COEFF_ON, is_flag=True)
@ac.option("-c", "--no-fsm-lt-coeff", help=h.HELP_LOG_CONTROL_FSM_LT_COEFF_OFF, is_flag=True)

@ac.option("-S", "--fsm-lt-stimuli", help=h.HELP_LOG_CONTROL_FSM_LT_STIMULI_ON, is_flag=True)
@ac.option("-s", "--no-fsm-lt-stimuli", help=h.HELP_LOG_CONTROL_FSM_LT_STIMULI_OFF, is_flag=True)

@ac.option("-Z", "--fsm-lt-alg0", help=h.HELP_LOG_CONTROL_FSM_LT_ALG0_ON, is_flag=True)
@ac.option("-z", "--no-fsm-lt-alg0", help=h.HELP_LOG_CONTROL_FSM_LT_ALG0_OFF, is_flag=True)

@ac.option("-O", "--fsm-lt-algn1", help=h.HELP_LOG_CONTROL_FSM_LT_ALGN1_ON, is_flag=True)
@ac.option("-o", "--no-fsm-lt-algn1", help=h.HELP_LOG_CONTROL_FSM_LT_ALGN1_OFF, is_flag=True)

@ac.pass_context
async def log_ctrl(
    context: ac.Context, 
    debug: bool,
    an_trace: bool, 
    lt_trace: bool, 
    alg_trace: bool,
    fsm_port: bool,
    fsm_an: bool,
    fsm_an_stimuli: bool,
    fsm_lt: bool,
    fsm_lt_coeff: bool,
    fsm_lt_stimuli: bool,
    fsm_lt_alg0: bool,
    fsm_lt_algn1: bool,
    no_debug: bool,
    no_an_trace: bool, 
    no_lt_trace: bool, 
    no_alg_trace: bool,
    no_fsm_port: bool,
    no_fsm_an: bool,
    no_fsm_an_stimuli: bool,
    no_fsm_lt: bool,
    no_fsm_lt_coeff: bool,
    no_fsm_lt_stimuli: bool,
    no_fsm_lt_alg0: bool,
    no_fsm_lt_algn1: bool,
    ) -> str:
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    types = []

    # read from the server to get the current status
    resp = await anlt_utils.anlt_log_control_get(port_obj)
    _debug = resp["debug"]
    _an_trace = resp["an_trace"]
    _lt_trace = resp["lt_trace"]
    _alg_trace = resp["alg_trace"]
    _fsm_port = resp["fsm_port"]
    _fsm_an = resp["fsm_an"]
    _fsm_an_stimuli = resp["fsm_an_stimuli"]
    _fsm_lt = resp["fsm_lt"]
    _fsm_lt_coeff = resp["fsm_lt_coeff"]
    _fsm_lt_stimuli = resp["fsm_lt_stimuli"]
    _fsm_lt_alg0 = resp["fsm_lt_alg0"]
    _fsm_lt_algn1 = resp["fsm_lt_algn1"]

    _debug = dominant_and_recessive(_debug, debug, no_debug)
    _an_trace = dominant_and_recessive(_an_trace, an_trace, no_an_trace)
    _lt_trace = dominant_and_recessive(_lt_trace, lt_trace, no_lt_trace)
    _alg_trace = dominant_and_recessive(_alg_trace, alg_trace, no_alg_trace)
    _fsm_port = dominant_and_recessive(_fsm_port, fsm_port, no_fsm_port)
    _fsm_an = dominant_and_recessive(_fsm_an, fsm_an, no_fsm_an)
    _fsm_an_stimuli = dominant_and_recessive(_fsm_an_stimuli, fsm_an_stimuli, no_fsm_an_stimuli)
    _fsm_lt = dominant_and_recessive(_fsm_lt, fsm_lt, no_fsm_lt)
    _fsm_lt_coeff = dominant_and_recessive(_fsm_lt_coeff, fsm_lt_coeff, no_fsm_lt_coeff)
    _fsm_lt_stimuli = dominant_and_recessive(_fsm_lt_stimuli, fsm_lt_stimuli, no_fsm_lt_stimuli)
    _fsm_lt_alg0 = dominant_and_recessive(_fsm_lt_alg0, fsm_lt_alg0, no_fsm_lt_alg0)
    _fsm_lt_algn1 = dominant_and_recessive(_fsm_lt_algn1, fsm_lt_algn1, no_fsm_lt_algn1)

    if _debug:
        types.append(AnLtLogControl.LOG_TYPE_DEBUG)
    if _an_trace:
        types.append(AnLtLogControl.LOG_TYPE_AN_TRACE)
    if _lt_trace:
        types.append(AnLtLogControl.LOG_TYPE_LT_TRACE)
    if _alg_trace:
        types.append(AnLtLogControl.LOG_TYPE_ALG_TRACE)
    if _fsm_port:
        types.append(AnLtLogControl.LOG_TYPE_FSM_PORT)
    if _fsm_an:
        types.append(AnLtLogControl.LOG_TYPE_FSM_ANEG)
    if _fsm_an_stimuli:
        types.append(AnLtLogControl.LOG_TYPE_FSM_ANEG_STIMULI)
    if _fsm_lt:
        types.append(AnLtLogControl.LOG_TYPE_FSM_LT)
    if _fsm_lt_coeff:
        types.append(AnLtLogControl.LOG_TYPE_FSM_LT_COEFF)
    if _fsm_lt_stimuli:
        types.append(AnLtLogControl.LOG_TYPE_FSM_LT_STIMULI)
    if _fsm_lt_alg0:
        types.append(AnLtLogControl.LOG_TYPE_FSM_LT_ALG0)
    if _fsm_lt_algn1:
        types.append(AnLtLogControl.LOG_TYPE_FSM_LT_ALG1)

    await anlt_utils.anlt_log_control(port_obj, types)
    resp = await anlt_utils.anlt_log_control_get(port_obj)
    return format_log_control(
        storage, 
        resp["debug"], 
        resp["an_trace"], 
        resp["lt_trace"], 
        resp["alg_trace"],
        resp["fsm_port"],
        resp["fsm_an"],
        resp["fsm_an_stimuli"],
        resp["fsm_lt"],
        resp["fsm_lt_coeff"],
        resp["fsm_lt_stimuli"],
        resp["fsm_lt_alg0"],
        resp["fsm_lt_algn1"]
        )