from __future__ import annotations
import asyncclick as ac
from xoa_utils.clicks import click_backend as cb
from xoa_driver.hlfuncs import anlt as anlt_utils
from xoa_driver import enums
from xoa_utils.clis import (
    format_lt_algorithm,
    format_lt_config,
    format_lt_im,
    format_lt_inc_dec,
    format_lt_no_eq,
    format_lt_encoding,
    format_lt_preset,
    format_lt_trained,
    format_txtap_get,
    format_txtap_set,
    format_lt_status,
)
from xoa_utils.clicks.click_commands.group import xoa_util
from xoa_utils.clicks import click_help as h
from xoa_utils.cmds import CmdContext


# --------------------------
# command: lt
# --------------------------
@xoa_util.group(cls=cb.XenaGroup)
def lt():
    """
    Link training group
    """


# **************************
# Type: Config
# **************************
# **************************
# sub-command: lt config
# **************************
@lt.command(cls=cb.XenaCommand, name="config")
@ac.option(
    "--mode",
    type=ac.Choice(["interactive", "auto"]),
    help=h.HELP_LT_CONFIG_MODE,
    default="auto",
)
@ac.option("--on/--off", type=ac.BOOL, help=h.HELP_LT_CONFIG_ON, default=True)
@ac.option(
    "--preset0",
    type=ac.Choice(["ieee", "existing"]),
    help=h.HELP_LT_CONFIG_PRESET0,
    default="ieee",
)
@ac.option(
    "--timeout",
    type=ac.Choice(["enable", "disable"]),
    help=h.HELP_LT_TIMEOUT_MODE,
    default="enable",
)
@ac.pass_context
async def lt_config(context: ac.Context, mode: str, on: bool, preset0: str, timeout: str) -> str:
    """
    Link training config
    """
    storage: CmdContext = context.obj
    storage.retrieve_port()
    storage.store_should_do_lt(on)
    storage.store_lt_preset0(preset0)
    storage.store_lt_interactive(True if mode == "interactive" else False)
    storage.store_should_enable_lt_timeout(True if timeout == "enable" else False)
    return format_lt_config(storage)


# **************************
# sub-command: lt im
# **************************
@lt.command(cls=cb.XenaCommand, name="im")
@ac.argument("serdes", type=ac.INT)
@ac.argument("encoding", type=ac.Choice(["nrz", "pam4", "pam4pre"]))
@ac.pass_context
async def lt_im(context: ac.Context, serdes: int, encoding: str) -> str:
    """
    LT initial modulation config

        Configure link training initial modulation for a lane.

        <SERDES>: Specifies the transceiver lane index.

        <ENCODING>: Specifies the initial modulation. Allowed values: nrz | pam4 | pam4pre
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    storage.validate_current_serdes(serdes)
    storage.store_lt_initial_mod(serdes, encoding)
    status_dic = await anlt_utils.lt_im_status(port_obj)
    return format_lt_im(status_dic, storage, serdes)


# **************************
# sub-command: lt alg
# **************************
@lt.command(cls=cb.XenaCommand, name="alg")
@ac.argument("serdes", type=ac.INT)
@ac.argument("algorithm", type=ac.Choice(["alg0", "algn1"]))
@ac.pass_context
async def lt_algorithm(context: ac.Context, serdes: int, algorithm: str) -> str:
    """
    LT algorithm config

        Configure link training algorithm for a lane

        <SERDES>: Specifies the transceiver lane index.

        <ALGORITHM>: Specifies the algorithm. Allowed values: alg0 | algn1
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    storage.validate_current_serdes(serdes)
    storage.store_lt_algorithm(serdes, algorithm)
    status_dic = await anlt_utils.lt_algorithm_status(port_obj)
    return format_lt_algorithm(status_dic, storage, serdes)


# **************************
# Type: Control
# **************************
# **************************
# sub-command: lt inc
# **************************
@lt.command(cls=cb.XenaCommand, name="inc")
@ac.argument("serdes", type=ac.INT)
@ac.argument("emphasis", type=ac.Choice(["pre3", "pre2", "pre", "main", "post"]))
@ac.pass_context
async def lt_inc(context: ac.Context, serdes: int, emphasis: str) -> str:
    """
    Request increment coeff

        Request remote port to increment (+) an emphasis by 1 on a lane

        <SERDES>: Specifies the transceiver lane index.

        <EMPHASIS>: The emphasis (coefficient) of the link partner. Allowed values: pre3 | pre2 | pre | main | post
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    storage.validate_current_serdes(serdes)
    resp = await anlt_utils.lt_coeff_inc(
        port_obj, serdes, enums.LinkTrainCoeffs[emphasis.upper()]
    )
    return format_lt_inc_dec(storage, serdes, emphasis, True, resp.name)


# **************************
# sub-command: lt dec
# **************************
@lt.command(cls=cb.XenaCommand, name="dec")
@ac.argument("serdes", type=ac.INT)
@ac.argument("emphasis", type=ac.Choice(["pre3", "pre2", "pre", "main", "post"]))
@ac.pass_context
async def lt_dec(context: ac.Context, serdes: int, emphasis: str) -> str:
    """
    Request decrement coeff

        Request remote port to decrement (-) an emphasis by 1 on a lane

        <SERDES>: Specifies the transceiver lane index.

        <EMPHASIS>: The emphasis (coefficient) of the link partner. Allowed values: pre3 | pre2 | pre | main | post
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    storage.validate_current_serdes(serdes)
    resp = await anlt_utils.lt_coeff_dec(
        port_obj, serdes, enums.LinkTrainCoeffs[emphasis.upper()]
    )
    return format_lt_inc_dec(storage, serdes, emphasis, False, resp.name)


# **************************
# Type: Control
# **************************
# **************************
# sub-command: lt no-eq
# **************************
@lt.command(cls=cb.XenaCommand, name="no-eq")
@ac.argument("serdes", type=ac.INT)
@ac.argument("emphasis", type=ac.Choice(["pre3", "pre2", "pre", "main", "post"]))
@ac.pass_context
async def lt_no_eq(context: ac.Context, serdes: int, emphasis: str) -> str:
    """
    Request equalizing to off

        Request remote port serdes to turn off equalizing on a lane

        <SERDES>: Specifies the transceiver lane index.

        <EMPHASIS>: The emphasis (coefficient) of the link partner. Allowed values: pre3 | pre2 | pre | main | post
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    storage.validate_current_serdes(serdes)
    resp = await anlt_utils.lt_coeff_no_eq(
        port_obj, serdes, enums.LinkTrainCoeffs[emphasis.upper()]
    )
    return format_lt_no_eq(storage, serdes, emphasis, resp.name)


# **************************
# sub-command: lt encoding
# **************************
@lt.command(cls=cb.XenaCommand, name="encoding")
@ac.argument("serdes", type=ac.INT)
@ac.argument("encoding", type=ac.Choice(["nrz", "pam4", "pam4pre"]))
@ac.pass_context
async def lt_encoding(context: ac.Context, serdes: int, encoding: str) -> str:
    """
    Request an encoding

        Request remote port to use a modulation encoding on a lane

        <SERDES>: Specifies the transceiver lane index.

        <ENCODING>: Specifies the encoding. Allowed values: nrz | pam4 | pam4pre
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    storage.validate_current_serdes(serdes)
    e = enums.LinkTrainEncoding[
        {"pam4pre": "PAM4_WITH_PRECODING"}.get(encoding, encoding).upper()
    ]
    resp = await anlt_utils.lt_encoding(port_obj, serdes, e)
    return format_lt_encoding(storage, serdes, encoding, resp.name)


# **************************
# sub-command: lt preset
# **************************
@lt.command(cls=cb.XenaCommand, name="preset")
@ac.argument("serdes", type=ac.INT)
@ac.argument("preset", type=ac.IntRange(1, 5))
@ac.pass_context
async def lt_preset(context: ac.Context, serdes: int, preset: int) -> str:
    """
    Request a preset

        Request remote port to use preset on a lane

        <SERDES>: Specifies the transceiver lane index.

        <PRESET>: Specifies the preset index. Allowed values: 1 | 2 | 3 | 4 | 5
    """
    preset = max(preset - 1, 0)
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    storage.validate_current_serdes(serdes)
    resp = await anlt_utils.lt_preset(port_obj, serdes, enums.LinkTrainPresets(preset))
    return format_lt_preset(storage, serdes, preset, resp.name)


# **************************
# sub-command: lt trained
# **************************
@lt.command(cls=cb.XenaCommand, name="trained")
@ac.argument("serdes", type=ac.INT)
@ac.pass_context
async def lt_trained(context: ac.Context, serdes: int) -> str:
    """
    Announce trained

        Announce trained to remote port on a lane.

        <SERDES>: Specifies the transceiver lane index.
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    storage.validate_current_serdes(serdes)
    resp = await anlt_utils.lt_trained(port_obj, serdes)
    return format_lt_trained(storage, serdes, resp.name)


# **************************
# sub-command: lt txtapget
# **************************
@lt.command(cls=cb.XenaCommand, name="txtapget")
@ac.argument("serdes", type=ac.INT)
@ac.pass_context
async def lt_txtapget(context: ac.Context, serdes: int) -> str:
    """
    Read tap values

        Read TX tap values of the port

        <SERDES>: Specifies the transceiver lane index.
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    storage.validate_current_serdes(serdes)
    dic = await anlt_utils.txtap_get(port_obj, serdes)
    return format_txtap_get(serdes, dic)


# **************************
# sub-command: lt txtapset
# **************************
@lt.command(cls=cb.XenaCommand, name="txtapset")
@ac.argument("serdes", type=ac.INT)
@ac.argument("pre3", type=ac.INT)
@ac.argument("pre2", type=ac.INT)
@ac.argument("pre", type=ac.INT)
@ac.argument("main", type=ac.INT)
@ac.argument("post", type=ac.INT)
@ac.pass_context
async def lt_txtapset(
    context: ac.Context,
    serdes: int,
    pre3: int,
    pre2: int,
    pre: int,
    main: int,
    post: int,
) -> str:
    """
    Write tap values

        Write TX tap values of the port

        <SERDES>: Specifies the transceiver lane index.

        <PRE3>: Specifies c(-3) value of the tap.

        <PRE2>: Specifies c(-2) value of the tap.

        <PRE> : Specifies c(-1) value of the tap.

        <MAIN>: Specifies c(0) value of the tap.

        <POST>: Specifies c(1) value of the tap.
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    storage.validate_current_serdes(serdes)
    await anlt_utils.txtap_set(port_obj, serdes, pre3, pre2, pre, main, post)
    return format_txtap_set(serdes, pre3, pre2, pre, main, post)


# **************************
# sub-command: lt status
# **************************
@lt.command(cls=cb.XenaCommand, name="status")
@ac.argument("serdes", type=ac.INT)
@ac.pass_context
async def lt_status(context: ac.Context, serdes: int) -> str:
    """
    LT status

        Show LT status of a specified lane

        <SERDES>: Specifies the transceiver lane index.
    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    storage.validate_current_serdes(serdes)
    dic = await anlt_utils.lt_status(port_obj, serdes)
    return format_lt_status(dic)


# ******************************
# sub-command: lt txtap-autotune
# ******************************
@lt.command(cls=cb.XenaCommand, name="txtap-autotune")
@ac.argument("serdes", type=ac.INT)
@ac.pass_context
async def lt_txtap_autotune(
    context: ac.Context,
    serdes: int,
) -> str:
    """
    Autotune tap values

        Autotune TX tap values of a specified lane

        <SERDES>: Specifies the transceiver lane index.

    """
    storage: CmdContext = context.obj
    port_obj = storage.retrieve_port()
    storage.validate_current_serdes(serdes)
    await anlt_utils.txtap_autotune(port_obj, serdes)
    dic = await anlt_utils.txtap_get(port_obj, serdes)
    return format_txtap_get(serdes, dic)