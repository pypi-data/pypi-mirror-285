HELP_CONNECT_PORT_LIST = "Specifies the ports on the specified device host, \
default to null. Specify a port using the format slot/port, no spaces between. \
e.g. --port_list 0/0,0/1,0/2,0/3. If used,the context will switch to the first \
port in the list after the connection is established.\n"

HELP_CONNECT_RESET = "Removes all port configurations of the ports in --ports after \
reservation, default to --no-reset."

HELP_CONNECT_FORCE = "Breaks port locks established by another user, aka. \
force reservation, default to --force."


HELP_CONNECT_PWD = "The login password of the tester, default to xena. \
e.g. --password xena"


HELP_CONNECT_TCP_PORT = "The TCP port number on the chassis for the client to \
establish a session, default to 22606."

HELP_CONNECT = """
    Connect to a tester for the current session.

        DEVICE TEXT: Specifies the chassis address for connection. You can specify the IP addresses in IPv4 format, or a host name. e.g. 10.10.10.10, demo.xenanetworks.com\n
        USERNAME TEXT: Specifies the name of the user, e.g. xoa or automation

    """

HELP_PORT_RESET = "Removes all port configurations in --port_list after \
reservation, default to --reset"

HELP_PORT_FORCE = "Breaks port locks established by another user, aka. force \
reservation, default to --force"

HELP_EXIT_RELEASE = "Determines whether the ports should be released before exiting, default to --release"

HELP_PORTS_ALL = "Show all ports of the tester, default to --no-all"

HELP_ANLT_RESTART_LINK_DOWN_ON = "Should port enables AN+LT auto-restart when a link down condition is detected, default to --no-link-down."

HELP_ANLT_RESTART_LT_FAIL_ON = "Should port initiates the AN+LT restart process repeatedly when LT experiences failure until LT succeeds, default to --no-lt-fail."

HELP_AN_CONFIG_ON = "Enable or disable auto-negotiation on the working port, \
default to --on."

HELP_AN_CONFIG_LOOPBACK = "Should loopback be allowed in auto-negotiation, \
default to --no-loopback."

HELP_LT_CONFIG_MODE = "The mode for Link Training on the working port, default to --mode auto."

HELP_LT_TIMEOUT_MODE = "The timeout mode for Link Training (auto) on the working port, default to --timeout enable."

HELP_LT_CONFIG_ON = "Enable or disable Link Training on the working port, default to --on."

HELP_LT_CONFIG_PRESET0 = "Should the Out-of-Sync use IEEE values (--preset0 ieee) or existing tap values (--preset0 existing), default to --preset0 ieee."

HELP_ANLT_LOG_FILENAME = "Filename of the log."

HELP_ANLT_LOG_KEEP = "Specifies what types of log entries to keep, default to keep all.\
Allow values: all | an | lt \
all: keep both AN and LT\
an:  keep AN only\
lt:  keep lt only"

HELP_ANLT_LOG_SERDES = "Specifies which serdes of LT logs to keep. If you don't know how many\
serdes the port has, use 'anlt log', default to all serdes."

HELP_ANLT_LOG_POLLS = "Polls per second, default to 10."

HELP_ANLT_READ = "Load and read log file."

HELP_STRICT_ON = "Should enable ANLT strict mode, default to --on."

HELP_LOG_CONTROL_DEBUG_ON = "Debug log ON"
HELP_LOG_CONTROL_DEBUG_OFF = "Debug log OFF"

HELP_LOG_CONTROL_AN_TRACE_ON = "Autoneg trace ON"
HELP_LOG_CONTROL_AN_TRACE_OFF = "Autoneg trace OFF"

HELP_LOG_CONTROL_LT_TRACE_ON = "Link Training trace ON"
HELP_LOG_CONTROL_LT_TRACE_OFF = "Link Training trace OFF"

HELP_LOG_CONTROL_ALG_TRACE_ON = "Link Training algorithm trace ON"
HELP_LOG_CONTROL_ALG_TRACE_OFF = "Link Training algorithm trace OFF"

HELP_LOG_CONTROL_FSM_PORT_ON = "Port FSM trace ON"
HELP_LOG_CONTROL_FSM_PORT_OFF = "Port FSM trace OFF"

HELP_LOG_CONTROL_FSM_AN_ON = "Autoneg FSM trace ON"
HELP_LOG_CONTROL_FSM_AN_OFF = "Autoneg FSM trace OFF"

HELP_LOG_CONTROL_FSM_AN_STIMULI_ON = "Autoneg stimuli FSM trace ON"
HELP_LOG_CONTROL_FSM_AN_STIMULI_OFF = "Autoneg stimuli FSM trace OFF"

HELP_LOG_CONTROL_FSM_LT_ON = "Link Training FSM trace ON"
HELP_LOG_CONTROL_FSM_LT_OFF = "Link Training FSM trace OFF"

HELP_LOG_CONTROL_FSM_LT_COEFF_ON = "Link Training coefficient FSM trace ON"
HELP_LOG_CONTROL_FSM_LT_COEFF_OFF = "Link Training coefficient FSM trace OFF"

HELP_LOG_CONTROL_FSM_LT_STIMULI_ON = "Link Training stimuli FSM trace ON"
HELP_LOG_CONTROL_FSM_LT_STIMULI_OFF = "Link Training stimuli FSM trace OFF"

HELP_LOG_CONTROL_FSM_LT_ALG0_ON = "Link Training algorithm0 FSM trace ON"
HELP_LOG_CONTROL_FSM_LT_ALG0_OFF = "Link Training algorithm0 FSM trace OFF"

HELP_LOG_CONTROL_FSM_LT_ALGN1_ON = "Link Training algorithmN1 FSM trace ON"
HELP_LOG_CONTROL_FSM_LT_ALGN1_OFF = "Link Training algorithmN1 FSM trace OFF"