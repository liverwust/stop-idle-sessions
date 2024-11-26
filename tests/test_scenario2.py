"""Scenario 2 for unit-testing of stop-idle-sessions

In Scenario 2, there are several sessions:

  * Session 5 is an active SSH session running a text editor and generating
    keystrokes. It should be left alone.
  * Session 7 is an idle SSH session which should be terminated. However, it
    is running vncserver and so it should be the case that only the Session
    Leader is terminated, not other processes.
  * Session 13 was created by Visual Studio Code. It doesn't have an assigned
    TTY/PTY and should be left alone.
  * Session 14 is an idle SSH session but which is currently connected to the
    VNC session in the backend. However, the VNC session itself is idle.
    Session 14's Session Leader should be terminated (but the VNC server left
    alone). By happenstance, terminating the Session Leader for session 14
    will terminate all remaining processes in Session 14 (which happen to be
    direct children of the Session Leader) and so this one will go away
    entirely.
  * Session 16 has a long-running Ansible connection under a dedicated service
    account name. Because of the username, it should be left alone.
  * Session c1 is a GDM login screen. Although loginctl indicates this as idle
    for a long time, it should be left alone.
"""


from ipaddress import ip_address, IPv4Address, IPv6Address
from textwrap import dedent
from typing import Any, List, Mapping, Set, Tuple, Union
from unittest.mock import Mock

import stop_idle_sessions.main
import stop_idle_sessions.ps
import stop_idle_sessions.ss

from . import test_logind, test_main, test_ps, test_ss


class Scenario2LogindTestCase(test_logind.LogindTestCase):
    """Scenario2 unit testing for the logind module

    See the docstring for the test_scenario2 module for an overall description
    of Scenario 2 (various sessions on a largely idle system).

    This was generated by the following shell pipeline:
        loginctl | tail -n +2 | head -n -2 | awk '{print $1}' |
        xargs -L1 loginctl show-session
    """

    def _mock_gio_results_spec(self) -> Mapping[str, Mapping[str, str]]:
        """Input data to populate the mock Gio object (logind API)"""
        return {
            "13": {
                    "Id": "13",
                    "User": "1000",
                    "TTY": "",
                    "Scope": "session-13.scope",
                    "Leader": "19012",
                    "Type": "tty"
            },
            "14": {
                    "Id": "14",
                    "User": "1000",
                    "TTY": "pts/3",
                    "Scope": "session-14.scope",
                    "Leader": "20982",
                    "Type": "tty"
            },
            "16": {
                    "Id": "16",
                    "User": "1001",
                    "TTY": "pts/2",
                    "Scope": "session-16.scope",
                    "Leader": "27584",
                    "Type": "tty"
            },
            "5": {
                    "Id": "5",
                    "User": "1000",
                    "TTY": "pts/0",
                    "Scope": "session-5.scope",
                    "Leader": "12033",
                    "Type": "tty"
            },
            "7": {
                    "Id": "7",
                    "User": "1000",
                    "TTY": "pts/1",
                    "Scope": "session-7.scope",
                    "Leader": "13268",
                    "Type": "tty"
            },
            "c1": {
                    "Id": "c1",
                    "User": "42",
                    "TTY": "tty1",
                    "Scope": "session-c1.scope",
                    "Leader": "13679",
                    "Type": "wayland"
            }
        }


    def _expected_logind_sessions(self) -> List[Mapping[str, Any]]:
        """Expected set of logind session attributes to be returned"""
        return [
            {
                "session_id": "13",
                "uid": 1000,
                "tty": "",
                "leader": 19012,
                "session_type": "tty",
                "scope": "session-13.scope",
                "scope_path": "/user.slice/user-1000.slice/session-13.scope"
            },
            {
                "session_id": "14",
                "uid": 1000,
                "tty": "pts/3",
                "leader": 20982,
                "session_type": "tty",
                "scope": "session-14.scope",
                "scope_path": "/user.slice/user-1000.slice/session-14.scope"
            },
            {
                "session_id": "16",
                "uid": 1001,
                "tty": "pts/2",
                "leader": 27584,
                "session_type": "tty",
                "scope": "session-16.scope",
                "scope_path": "/user.slice/user-1001.slice/session-16.scope"
            },
            {
                "session_id": "5",
                "uid": 1000,
                "tty": "pts/0",
                "leader": 12033,
                "session_type": "tty",
                "scope": "session-5.scope",
                "scope_path": "/user.slice/user-1000.slice/session-5.scope"
            },
            {
                "session_id": "7",
                "uid": 1000,
                "tty": "pts/1",
                "leader": 13268,
                "session_type": "tty",
                "scope": "session-7.scope",
                "scope_path": "/user.slice/user-1000.slice/session-7.scope"
            },
            {
                "session_id": "c1",
                "uid": 42,
                "tty": "tty1",
                "leader": 13679,
                "session_type": "wayland",
                "scope": "session-c1.scope",
                "scope_path": "/user.slice/user-42.slice/session-c1.scope"
            }
        ]

class Scenario2CgroupPidsTestCase(test_ps.CgroupPidsTestCase):
    """Scenario2 unit testing for the ps module

    See the docstring for the test_scenario2 module for an overall description
    of Scenario 2 (various sessions on a largely idle system).

    This was generated by the following shell pipeline:
        cat /sys/fs/cgroup/systemd/user.slice/user-1002.slice/session-1267.scope/cgroup.procs |
        xargs -L1 ps -o 'pid,args' --no-headers -p

    In Scenario 2, we deliberately choose the Visual Studio Code session with
    some odd and long-named subprocesses, just to make sure that no parsing
    errors occur within these unusual commandlines.
    """

    def _mock_process_specs(self) -> Mapping[int, str]:
        """Input data to populate the filesystem mock for the cgroup sysfs"""
        # Yes, there are some very long lines here!
        # pylint: disable=line-too-long
        return {
            19012: "sshd: auser [priv]",
            19015: "sshd: auser@notty",
            19016: "-bash",
            19400: "sh",
            19453: "/home/auser/.vscode-server/code-f1a4fb101478ce6ec82fe9627c43efbf9e98c813 command-shell --cli-data-dir /home/auser/.vscode-server/cli --parent-process-id 19400 --on-host=127.0.0.1 --on-port",
            19495: "sh /home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/bin/code-server --connection-token=remotessh --accept-server-license-terms --start-server --enable-remote-auto-shutdown --socket-path=/tmp/code-a14f5532-361c-4951-866a-a9d687ea7ad6",
            19501: "/home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/node /home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/out/server-main.js --connection-token=remotessh --accept-server-license-terms --start-server --enable-remote-auto-shutdown --socket-path=/tmp/code-a14f5532-361c-4951-866a-a9d687ea7ad6",
            19735: "/home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/node /home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/out/bootstrap-fork --type=ptyHost --logsPath /home/auser/.vscode-server/data/logs/20241122T111553",
            20164: "/home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/node --dns-result-order=ipv4first /home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/out/bootstrap-fork --type=extensionHost --transformURIs --useHostProxy=false",
            20175: "/home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/node /home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/out/bootstrap-fork --type=fileWatcher",
            25109: "sleep 180"
        }

    def _expected_process_objects(self) -> List[stop_idle_sessions.ps.Process]:
        """Expected set of processes to be parsed out of the cgroup sysfs"""
        # Yes, there are some very long lines here!
        # pylint: disable=line-too-long
        return [
            stop_idle_sessions.ps.Process(
                    pid=19012,
                    cmdline="sshd: auser [priv]",
                    environ={}
            ),
            stop_idle_sessions.ps.Process(
                    pid=19015,
                    cmdline="sshd: auser@notty",
                    environ={}
            ),
            stop_idle_sessions.ps.Process(
                    pid=19016,
                    cmdline="-bash",
                    environ={}
            ),
            stop_idle_sessions.ps.Process(
                    pid=19400,
                    cmdline="sh",
                    environ={}
            ),
            stop_idle_sessions.ps.Process(
                    pid=19453,
                    cmdline="/home/auser/.vscode-server/code-f1a4fb101478ce6ec82fe9627c43efbf9e98c813 command-shell --cli-data-dir /home/auser/.vscode-server/cli --parent-process-id 19400 --on-host=127.0.0.1 --on-port",
                    environ={}
            ),
            stop_idle_sessions.ps.Process(
                    pid=19495,
                    cmdline="sh /home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/bin/code-server --connection-token=remotessh --accept-server-license-terms --start-server --enable-remote-auto-shutdown --socket-path=/tmp/code-a14f5532-361c-4951-866a-a9d687ea7ad6",
                    environ={}
            ),
            stop_idle_sessions.ps.Process(
                    pid=19501,
                    cmdline="/home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/node /home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/out/server-main.js --connection-token=remotessh --accept-server-license-terms --start-server --enable-remote-auto-shutdown --socket-path=/tmp/code-a14f5532-361c-4951-866a-a9d687ea7ad6",
                    environ={}
            ),
            stop_idle_sessions.ps.Process(
                    pid=19735,
                    cmdline="/home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/node /home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/out/bootstrap-fork --type=ptyHost --logsPath /home/auser/.vscode-server/data/logs/20241122T111553",
                    environ={}
            ),
            stop_idle_sessions.ps.Process(
                    pid=20164,
                    cmdline="/home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/node --dns-result-order=ipv4first /home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/out/bootstrap-fork --type=extensionHost --transformURIs --useHostProxy=false",
                    environ={}
            ),
            stop_idle_sessions.ps.Process(
                    pid=20175,
                    cmdline="/home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/node /home/auser/.vscode-server/cli/servers/Stable-f1a4fb101478ce6ec82fe9627c43efbf9e98c813/server/out/bootstrap-fork --type=fileWatcher",
                    environ={}
            ),
            stop_idle_sessions.ps.Process(
                    pid=25109,
                    cmdline="sleep 180",
                    environ={}
            )
        ]


class Scenario2LoopbackConnectionTestCase(test_ss.LoopbackConnectionTestCase):
    """Scenario2 unit testing for the ss module

    See the docstring for the test_scenario1 module for an overall description
    of Scenario 1 (single active user w/ VNC).

    This was generated by the following shell pipeline:
        /usr/sbin/ss --all --no-header --numeric --oneline --processes --tcp
    """

    def _mock_raw_ss_output(self) -> str:
        """Input data to populate the mocked network connections table"""
        return dedent("""\
            LISTEN     0      128          0.0.0.0:22          0.0.0.0:*     users:(("sshd",pid=948,fd=3))                           
            LISTEN     0      128        127.0.0.1:631         0.0.0.0:*     users:(("cupsd",pid=949,fd=8))                          
            LISTEN     0      128        127.0.0.1:6010        0.0.0.0:*     users:(("sshd",pid=23438,fd=11))                        
            LISTEN     0      5          127.0.0.1:5901        0.0.0.0:*     users:(("Xvnc",pid=20272,fd=6))                         
            LISTEN     0      128          0.0.0.0:111         0.0.0.0:*     users:(("rpcbind",pid=838,fd=4),("systemd",pid=1,fd=30))
            LISTEN     0      1024       127.0.0.1:35249       0.0.0.0:*     users:(("code-f1a4fb1014",pid=19453,fd=9))              
            LISTEN     0      32     192.168.124.1:53          0.0.0.0:*     users:(("dnsmasq",pid=1714,fd=6))                       
            CLOSE-WAIT 25     0      192.168.122.8:53078 151.101.65.91:443   users:(("gnome-shell",pid=13752,fd=55))                 
            ESTAB      0      0      192.168.122.8:22    192.168.122.1:60780 users:(("sshd",pid=23438,fd=4),("sshd",pid=23435,fd=4)) 
            ESTAB      0      0      192.168.122.8:22    192.168.122.1:40108 users:(("sshd",pid=13271,fd=4),("sshd",pid=13268,fd=4)) 
            ESTAB      0      0      192.168.122.8:22    192.168.122.1:57948 users:(("sshd",pid=20985,fd=4),("sshd",pid=20982,fd=4)) 
            ESTAB      0      0      192.168.122.8:22    192.168.122.1:42724 users:(("sshd",pid=27608,fd=4),("sshd",pid=27584,fd=4)) 
            ESTAB      0      0          127.0.0.1:52016     127.0.0.1:35249 users:(("sshd",pid=19015,fd=11))                        
            ESTAB      0      0      192.168.122.8:22    192.168.122.1:46896 users:(("sshd",pid=12036,fd=4),("sshd",pid=12033,fd=4)) 
            CLOSE-WAIT 25     0      192.168.122.8:43884 151.101.65.91:443   users:(("gnome-shell",pid=20373,fd=19))                 
            ESTAB      0      0      192.168.122.8:22    192.168.122.1:38292 users:(("sshd",pid=19015,fd=4),("sshd",pid=19012,fd=4)) 
            ESTAB      0      0          127.0.0.1:35249     127.0.0.1:52016 users:(("code-f1a4fb1014",pid=19453,fd=12))             
            LISTEN     0      128             [::]:22             [::]:*     users:(("sshd",pid=948,fd=4))                           
            LISTEN     0      128            [::1]:631            [::]:*     users:(("cupsd",pid=949,fd=7))                          
            LISTEN     0      128            [::1]:6010           [::]:*     users:(("sshd",pid=23438,fd=10))                        
            LISTEN     0      5              [::1]:5901           [::]:*     users:(("Xvnc",pid=20272,fd=7))                         
            LISTEN     0      128             [::]:111            [::]:*     users:(("rpcbind",pid=838,fd=6),("systemd",pid=1,fd=34))
            ESTAB      0      0              [::1]:5901          [::1]:45028 users:(("Xvnc",pid=20272,fd=24))                        
            ESTAB      0      0              [::1]:45028         [::1]:5901  users:(("sshd",pid=20985,fd=11))                        
        """)

    def _expected_listening_ports(self) -> Set[int]:
        """Expected set of listening ports parsed out of the mock ss data"""
        return set([22, 53, 111, 631, 5901, 6010, 35249])

    def _expected_peer_pairs(self) -> Set[Tuple[Union[IPv4Address,
                                                      IPv6Address], int]]:
        """Expected set of remote peers parsed from the established conns"""
        return set([
                (ip_address("127.0.0.1"), 35249),
                (ip_address("127.0.0.1"), 52016),
                (ip_address("192.168.122.1"), 38292),
                (ip_address("192.168.122.1"), 40108),
                (ip_address("192.168.122.1"), 42724),
                (ip_address("192.168.122.1"), 46896),
                (ip_address("192.168.122.1"), 57948),
                (ip_address("192.168.122.1"), 60780),
                (ip_address("::1"), 45028),
                (ip_address("::1"), 5901),
        ])

    def _expected_connections(self) -> List[stop_idle_sessions.ss.LoopbackConnection]:
        """Expected set of loopback connections identified from these conns

        For Scenario 2, this includes both a VNC loopback connection
        (listening port 5901) and a VS Code loopback connection.
        """

        return [
            stop_idle_sessions.ss.LoopbackConnection(
                    client=stop_idle_sessions.ss.Socket(
                        addr=ip_address('127.0.0.1'),
                        port=52016,
                        processes=[stop_idle_sessions.ps.Process(
                            pid=19015,
                            cmdline="",
                            environ={}
                        )]
                    ),
                    server=stop_idle_sessions.ss.Socket(
                        addr=ip_address('127.0.0.1'),
                        port=35249,
                        processes=[stop_idle_sessions.ps.Process(
                            pid=19453,
                            cmdline="",
                            environ={}
                        )]
                    )
            ),
            stop_idle_sessions.ss.LoopbackConnection(
                    client=stop_idle_sessions.ss.Socket(
                        addr=ip_address('::1'),
                        port=45028,
                        processes=[stop_idle_sessions.ps.Process(
                            pid=20985,
                            cmdline="",
                            environ={}
                        )]
                    ),
                    server=stop_idle_sessions.ss.Socket(
                        addr=ip_address('::1'),
                        port=5901,
                        processes=[stop_idle_sessions.ps.Process(
                            pid=20272,
                            cmdline="",
                            environ={}
                        )]
                    )
            )
        ]


class Scenario2MainLoopTestCase(test_main.MainLoopTestCase):
    """Scenario2 unit testing for the main module

    See the docstring for the test_scenario2 module for an overall description
    of Scenario 2 (various sessions on a largely idle system).

    See also the other Scenario2* TestCases for hints about how to generate
    the input data which was used to specify this test fixture.
    """

    def _mock_get_logind_sessions(self) -> List[Mock]:
        """Input data to mock out the logind module and D-Bus"""
        return [
            test_main.MainLoopTestCase.create_mock_logind_session(
                    session_id="13",
                    session_type="tty",
                    uid=1000,
                    tty="",
                    leader=19012,
                    scope="session-13.scope",
            ),
            test_main.MainLoopTestCase.create_mock_logind_session(
                    session_id="14",
                    session_type="tty",
                    uid=1000,
                    tty="pts/3",
                    leader=20982,
                    scope="session-14.scope",
            ),
            test_main.MainLoopTestCase.create_mock_logind_session(
                    session_id="16",
                    session_type="tty",
                    uid=1001,
                    tty="pts/2",
                    leader=27584,
                    scope="session-16.scope",
            ),
            test_main.MainLoopTestCase.create_mock_logind_session(
                    session_id="5",
                    session_type="tty",
                    uid=1000,
                    tty="pts/0",
                    leader=12033,
                    scope="session-5.scope",
            ),
            test_main.MainLoopTestCase.create_mock_logind_session(
                    session_id="7",
                    session_type="tty",
                    uid=1000,
                    tty="pts/1",
                    leader=13268,
                    scope="session-7.scope",
            ),
            test_main.MainLoopTestCase.create_mock_logind_session(
                    session_id="c1",
                    session_type="wayland",
                    uid=42,
                    tty="tty1",
                    leader=13679,
                    scope="session-c1.scope",
            )
        ]

    def _mock_find_loopback_connections(self) -> List[Mock]:
        """Input data to mock out the ss utility and module"""
        return [
            test_main.MainLoopTestCase.create_mock_loopback_connection(
                    client_addr=ip_address('127.0.0.1'),
                    client_port=52016,
                    client_pids=[19015],
                    server_addr=ip_address('127.0.0.1'),
                    server_port=35249,
                    server_pids=[19453]
            ),
            test_main.MainLoopTestCase.create_mock_loopback_connection(
                    client_addr=ip_address('::1'),
                    client_port=45028,
                    client_pids=[20985],
                    server_addr=ip_address('::1'),
                    server_port=5901,
                    server_pids=[20272]
            )
        ]

    def _mock_map_scope_processes(self) -> Mapping[str, Set[int]]:
        """Input data to mock out the ps and cgroup interface module"""
        return {
            "13": set([19012, 19015, 19016, 19400, 19453, 19495, 19501, 19735,
                       20164, 20175, 28246]),
            "14": set([20982, 20985, 20986]),
            "16": set([27584, 27608, 27996, 28025, 28029, 28030, 28032]),
            "5": set([12033, 12036, 12037, 22103, 22105, 22106, 22135,
                      22136]),
            "7": set([13268, 13271, 13272, 20272, 20277, 20278, 20287, 20288,
                      20295, 20308, 20313, 20318, 20320, 20327, 20362, 20373,
                      20393, 20396, 20402, 20403, 20405, 20410, 20412, 20427,
                      20438, 20447, 20468, 20587, 20594, 20601, 20607, 20616,
                      20620, 20622, 20625, 20626, 20631, 20633, 20637, 20639,
                      20643, 20644, 20651, 20655, 20661, 20663, 20665, 20668,
                      20673, 20674, 20705, 20726, 20736, 20741, 20749, 20765,
                      20767, 20778, 20783, 20790, 20791, 20805, 20810]),
            "c1": set([13679, 13704, 13712, 13713, 13717, 13752, 13793, 13802,
                       13807, 13810, 13818, 13821, 13824, 13827, 13835, 13864,
                       13866, 13870, 13871, 13875, 13877, 13878, 13881, 13883,
                       13890, 13900, 13904, 13907, 13911, 13954, 13988])
        }

    def _mock_username_mapping(self) -> Mapping[int, str]:
        """Convert numeric UIDs to symbolic usernames"""
        return {42: 'gdm', 1000: 'auser', 1001: 'ansible'}

    def _mock_excluded_users(self) -> List[str]:
        """Supplement session assertion testing with a set of excluded users"""
        return ["ansible"]

    def _register_expected_sessions(self) -> None:
        """Register the expected set of fully-fleshed-out session objects"""
        self.register_mock_session(
                session_id="13",
                session_type='tty',
                uid=1000,
                tty=None,
                scope="session-13.scope",
                pids_and_tunnels={
                    19012: ([], []),
                    19015: ([19453], ["13"]),
                    19016: ([], []),
                    19400: ([], []),
                    19453: ([], []),
                    19495: ([], []),
                    19501: ([], []),
                    19735: ([], []),
                    20164: ([], []),
                    20175: ([], []),
                    28246: ([], [])
                },
                assert_skipped=True
        )

        self.register_mock_session(
                session_id="14",
                session_type='tty',
                uid=1000,
                tty='pts/3',
                scope="session-14.scope",
                pids_and_tunnels={
                    20982: ([], []),
                    20985: ([20272], ["7"]),
                    20986: ([], [])
                },
                assert_skipped=False
        )

        self.register_mock_session(
                session_id="16",
                session_type='tty',
                uid=1001,
                tty='pts/2',
                scope="session-16.scope",
                pids_and_tunnels={
                    27584: ([], []),
                    27608: ([], []),
                    27996: ([], []),
                    28025: ([], []),
                    28029: ([], []),
                    28030: ([], []),
                    28032: ([], [])
                },
                assert_skipped=True
        )

        self.register_mock_session(
                session_id="5",
                session_type='tty',
                uid=1000,
                tty='pts/0',
                scope="session-5.scope",
                pids_and_tunnels={
                    12033: ([], []),
                    12036: ([], []),
                    12037: ([], []),
                    22103: ([], []),
                    22105: ([], []),
                    22106: ([], []),
                    22135: ([], []),
                    22136: ([], [])
                },
                assert_skipped=False
        )

        self.register_mock_session(
                session_id="7",
                session_type='tty',
                uid=1000,
                tty='pts/1',
                scope="session-7.scope",
                pids_and_tunnels={
                    13268: ([], []),
                    13271: ([], []),
                    13272: ([], []),
                    20272: ([], []),
                    20277: ([], []),
                    20278: ([], []),
                    20287: ([], []),
                    20288: ([], []),
                    20295: ([], []),
                    20308: ([], []),
                    20313: ([], []),
                    20318: ([], []),
                    20320: ([], []),
                    20327: ([], []),
                    20362: ([], []),
                    20373: ([], []),
                    20393: ([], []),
                    20396: ([], []),
                    20402: ([], []),
                    20403: ([], []),
                    20405: ([], []),
                    20410: ([], []),
                    20412: ([], []),
                    20427: ([], []),
                    20438: ([], []),
                    20447: ([], []),
                    20468: ([], []),
                    20587: ([], []),
                    20594: ([], []),
                    20601: ([], []),
                    20607: ([], []),
                    20616: ([], []),
                    20620: ([], []),
                    20622: ([], []),
                    20625: ([], []),
                    20626: ([], []),
                    20631: ([], []),
                    20633: ([], []),
                    20637: ([], []),
                    20639: ([], []),
                    20643: ([], []),
                    20644: ([], []),
                    20651: ([], []),
                    20655: ([], []),
                    20661: ([], []),
                    20663: ([], []),
                    20665: ([], []),
                    20668: ([], []),
                    20673: ([], []),
                    20674: ([], []),
                    20705: ([], []),
                    20726: ([], []),
                    20736: ([], []),
                    20741: ([], []),
                    20749: ([], []),
                    20765: ([], []),
                    20767: ([], []),
                    20778: ([], []),
                    20783: ([], []),
                    20790: ([], []),
                    20791: ([], []),
                    20805: ([], []),
                    20810: ([], [])
                },
                assert_skipped=False
        )

        self.register_mock_session(
                session_id="c1",
                session_type='wayland',
                uid=42,
                tty='tty1',
                scope="session-c1.scope",
                pids_and_tunnels={
                    13679: ([], []),
                    13704: ([], []),
                    13712: ([], []),
                    13713: ([], []),
                    13717: ([], []),
                    13752: ([], []),
                    13793: ([], []),
                    13802: ([], []),
                    13807: ([], []),
                    13810: ([], []),
                    13818: ([], []),
                    13821: ([], []),
                    13824: ([], []),
                    13827: ([], []),
                    13835: ([], []),
                    13864: ([], []),
                    13866: ([], []),
                    13870: ([], []),
                    13871: ([], []),
                    13875: ([], []),
                    13877: ([], []),
                    13878: ([], []),
                    13881: ([], []),
                    13883: ([], []),
                    13890: ([], []),
                    13900: ([], []),
                    13904: ([], []),
                    13907: ([], []),
                    13911: ([], []),
                    13954: ([], []),
                    13988: ([], [])
                },
                assert_skipped=True
        )
