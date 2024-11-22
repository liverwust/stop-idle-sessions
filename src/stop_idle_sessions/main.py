"""Main logic for the stop-idle-session loop"""


from datetime import timedelta
from itertools import product
import logging
import sys
import traceback
from typing import List, Mapping, NamedTuple, Optional

from stop_idle_sessions.exception import SessionParseError
import stop_idle_sessions.getent
import stop_idle_sessions.logind
import stop_idle_sessions.ps
import stop_idle_sessions.ss
import stop_idle_sessions.tty
import stop_idle_sessions.x11


logger = logging.getLogger(__name__)


class SessionProcess(NamedTuple):
    """Representation of a Process specifically inside of a Session"""

    # Generic Process details for this SessionProcess
    process: stop_idle_sessions.ps.Process

    # Whether this process has been marked as the "Leader" of its session
    # (i.e., whether Process.pid == Session.leader_pid)
    leader: bool

    # The value of the DISPLAY environment variable for this particular
    # process, or None if none was assigned
    display: Optional[str]

    # The idletime (expressed as a timedelta) reported by the X11 Screen Saver
    # extension for this DISPLAY (or None)
    display_idle: Optional[timedelta]

    # A (possibly empty) list of backend processes that this particular
    # process has tunneled back into
    tunneled_processes: List[stop_idle_sessions.ps.Process]

    # A (possibly empty) list of Sessions that contain the tunneled_processes
    # that this particular process has connected to
    tunneled_sessions: List['Session']

    def __eq__(self, other):
        if not hasattr(other, 'process'):
            return False
        if not hasattr(other.process, 'pid'):
            return False
        return self.process.pid == other.process.pid


class Session(NamedTuple):
    """Representation of an individual Session, combining various sources"""

    # Backend logind session object for this Session
    session: stop_idle_sessions.logind.Session

    # The TTY or PTY which is assigned to this session (or None)
    tty: Optional[stop_idle_sessions.tty.TTY]

    # The symbolic username corresponding to session.uid
    username: str

    # Collection of Process objects belonging to this Session
    processes: List[SessionProcess]

    def __eq__(self, other):
        if not hasattr(other, 'session'):
            return False
        if not hasattr(other.session, 'session_id'):
            return False
        return self.session.session_id == other.session.session_id


#def check_ssh_session_tunnel(session: Session) -> bool:
#    """Check whether an SSH session is tunneled to a backend session
#
#    This would be something like `ssh -L 5901:localhost:5901 <host>`. The Rule
#    will detect a tunnel only so long as it is actually part of an active
#    connection. A user needs to be connected to the client-side (and the
#    server-side needs to have relayed that connection) in order for this to
#    trigger. Simply _specifying_ that a tunnel should exists (-L) is not
#    enough.
#    """
#
#    for session_processes in session.processes:
#        for tunnel_backend in session_processes.tunnels:
#            if isinstance(tunnel_backend, Session):
#                pass
#

# Constructing the tree involves many local variables, necessarily
# pylint: disable-next=too-many-locals, too-many-branches
def load_sessions() -> List[Session]:
    """Construct an abstract Session/Process tree from system observations"""

    try:
        logind_sessions = stop_idle_sessions.logind.get_all_sessions()
        loopback_connections = stop_idle_sessions.ss.find_loopback_connections()
    except SessionParseError as err:
        logger.error('Problem while reading session and networking table '
                     'information: %s', err.message)
        raise err

    resolved_usernames: Mapping[int, str] = {}

    # Constructing the tree involves many layers of nesting, necessarily
    # pylint: disable=too-many-nested-blocks
    sessions: List[Session] = []
    for logind_session in logind_sessions:
        try:
            if logind_session.uid not in resolved_usernames:
                username = stop_idle_sessions.getent.uid_to_username(
                        logind_session.uid
                )
                resolved_usernames[logind_session.uid] = username

            session_processes: List[SessionProcess] = []
            ps_table = stop_idle_sessions.ps.processes_in_scope_path(
                    logind_session.scope_path
            )
            for process in ps_table:
                tunneled_processes: List[stop_idle_sessions.ps.Process] = []

                # Associate Processes thru loopback to other Processes
                for loopback_connection in loopback_connections:
                    client_processes = loopback_connection.client.processes
                    server_processes = loopback_connection.server.processes
                    for client_process in client_processes:
                        for server_process in server_processes:
                            if process == client_process:
                                if not server_process in tunneled_processes:
                                    tunneled_processes.append(server_process)

                display_idle: Optional[timedelta] = None
                if process.display is not None:
                    idle_ms = stop_idle_sessions.x11.retrieve_idle_time_ms(
                            process.display,
                            process.xauthority
                    )
                    display_idle = timedelta(milliseconds=idle_ms)

                session_processes.append(SessionProcess(
                        process=process,
                        leader=(process.pid == logind_session.leader),
                        display=process.display,
                        display_idle=display_idle,
                        tunneled_processes=tunneled_processes,
                        tunneled_sessions=[]
                ))

            session_tty: Optional[stop_idle_sessions.tty.TTY] = None
            if logind_session.tty != "":
                session_tty = stop_idle_sessions.tty.TTY(
                        logind_session.tty
                )

            sessions.append(Session(
                    session=logind_session,
                    tty=session_tty,
                    username=resolved_usernames[logind_session.uid],
                    processes=session_processes
            ))

        except SessionParseError as err:
            logger.warning('Could not successfully parse information related '
                           'to session %s: %s',
                           logind_session.session_id,
                           err.message)
            traceback.print_exc(file=sys.stderr)

    # Go back and resolve backend tunneled Processes to their Sessions
    for session_a, session_b in product(sessions, sessions):
        for process_a, process_b in product(session_a.processes,
                                            session_b.processes):
            for backend_process_a in process_a.tunneled_processes:
                if backend_process_a == process_b.process:
                    process_a.tunneled_sessions.append(session_b)

    # Send the identified Sessions to the debug log
    logger.debug('Identified %d sessions to be reviewed:')
    for index, session in enumerate(sessions):
        tty_string = "notty"
        if session.tty is not None:
            tty_string = session.tty.name
        logger.debug('%d (id=%s): %s@%s with %d processes and '
                     '%d active tunnels',
                     index + 1,  # make index more human-friendly by adding 1
                     session.session.session_id,
                     session.username,
                     tty_string,
                     len(session.processes),
                     sum(map(lambda p: len(p.tunneled_processes), session.processes)))

    return sessions


def apply_time_discrepancy_rule(session: Session) -> bool:
    """Check and fix a TTY whose atime is older than its mtime

    As indicated in the README, there are multiple kinds of "user activity" on
    the command-line. The systemd-logind logic for idle timeouts checks the
    atime on the TTY/PTY. User keyboard activity updates both the mtime and
    atime. On the other hand, program output _only_ updates the mtime.

    This rule ensures that the atime is touched to match the mtime, when the
    atime is older than the mtime. In doing so, program output will ALSO re-up
    the idle timeout.
    """

    if session.tty is not None:
        if session.tty.atime < session.tty.mtime:
            session.tty.touch_times(session.tty.mtime)
            return True
    return False