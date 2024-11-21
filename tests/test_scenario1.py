"""Scenario 1 for unit-testing of logind-idle-sessions-extras

In Scenario 1, there is a single active user with one SSH session and one
non-idle VNC session. The SSH session is actively tunneled into the VNC
session. Separately, the root user is SSH'd into the system (for observation)
and there is an idle GDM session running.
"""


from ipaddress import ip_address, IPv4Address, IPv6Address
from textwrap import dedent
from typing import Any, List, Mapping, Set, Tuple, Union

import logind_idle_session_extras.ps
import logind_idle_session_extras.ss

from . import test_logind, test_ps, test_ss


class Scenario1LogindTestCase(test_logind.LogindTestCase):
    """Scenario1 unit testing for the logind module

    See the docstring for the test_scenario1 module for an overall description
    of Scenario 1 (single active user w/ VNC).

    This was generated by the following shell pipeline:
        loginctl | tail -n +2 | head -n -2 | awk '{print $1}' |
        xargs -L1 loginctl show-session
    """

    def _mock_gio_results_spec(self) -> Mapping[str, Mapping[str, str]]:
        """Input data to populate the mock Gio object (logind API)"""
        return {
            "1267": {
                "Id": "1267",
                "User": "1002",
                "TTY": "pts/2",
                "Scope": "session-1267.scope",
                "Leader": "952165"
            },
            "1301": {
                "Id": "1301",
                "User": "0",
                "TTY": "pts/1",
                "Scope": "session-1301.scope",
                "Leader": "994974"
            },
            "1337": {
                "Id": "1337",
                "User": "1002",
                "TTY": "pts/0",
                "Scope": "session-1337.scope",
                "Leader": "1050298"
            },
            "c1": {
                "Id": "c1",
                "User": "42",
                "TTY": "tty1",
                "Scope": "session-c1.scope",
                "Leader": "5655"
            }
        }

    def _expected_logind_sessions(self) -> List[Mapping[str, Any]]:
        """Expected set of logind session attributes to be returned"""
        return [
            {
                "session_id": "1267",
                "uid": 1002,
                "tty": "pts/2",
                "leader": 952165,
                "scope": "session-1267.scope",
                "scope_path": "/user.slice/user-1002.slice/session-1267.scope"
            },
            {
                "session_id": "1301",
                "uid": 0,
                "tty": "pts/1",
                "leader": 994974,
                "scope": "session-1301.scope",
                "scope_path": "/user.slice/user-0.slice/session-1301.scope"
            },
            {
                "session_id": "1337",
                "uid": 1002,
                "tty": "pts/0",
                "leader": 1050298,
                "scope": "session-1337.scope",
                "scope_path": "/user.slice/user-1002.slice/session-1337.scope"
            },
            {
                "session_id": "c1",
                "uid": 42,
                "tty": "tty1",
                "leader": 5655,
                "scope": "session-c1.scope",
                "scope_path": "/user.slice/user-42.slice/session-c1.scope"
            }
        ]


class Scenario1CgroupPidsTestCase(test_ps.CgroupPidsTestCase):
    """Scenario1 unit testing for the ps module

    See the docstring for the test_scenario1 module for an overall description
    of Scenario 1 (single active user w/ VNC).

    This was generated by the following shell pipeline:
        cat /sys/fs/cgroup/systemd/user.slice/user-1002.slice/session-1267.scope/cgroup.procs |
        xargs -L1 ps -o 'pid,args' --no-headers -p

    In Scenario 1, we deliberately choose the Xvnc session which has a TON of
    child processes, just to make sure that no parsing errors occur with these
    unusual commandlines.
    """

    def _mock_process_specs(self) -> Mapping[int, str]:
        """Input data to populate the filesystem mock for the cgroup sysfs"""
        # Yes, there are some very long lines here!
        # pylint: disable=line-too-long
        return {
            772211: "/usr/libexec/gvfsd-metadata",
            952570: "/usr/bin/Xvnc :1 -auth /u/wk/auser/.Xauthority -desktop computer:1 (auser) -fp catalogue:/etc/X11/fontpath.d -geometry 1024x768 -pn -rfbauth /u/wk/auser/.vnc/passwd -rfbport 5901 -localhost",
            952581: "/bin/sh /u/wk/auser/.vnc/xstartup",
            952582: "/usr/libexec/gnome-session-binary",
            952591: "dbus-launch --sh-syntax --exit-with-session",
            952592: "/usr/bin/dbus-daemon --syslog --fork --print-pid 5 --print-address 7 --session",
            952644: "/usr/libexec/at-spi-bus-launcher",
            952649: "/usr/bin/dbus-daemon --config-file=/usr/share/defaults/at-spi2/accessibility.conf --nofork --print-address 3",
            952652: "/usr/libexec/at-spi2-registryd --use-gnome-session",
            952656: "/usr/libexec/gvfsd",
            952663: "/usr/libexec/gvfsd-fuse /run/user/1002/gvfs -f -o big_writes",
            952715: "/usr/bin/gnome-keyring-daemon --start --components=pkcs11",
            952727: "/usr/bin/gnome-shell",
            952766: "ibus-daemon --xim --panel disable",
            952768: "/usr/libexec/xdg-permission-store",
            952770: "/usr/libexec/gnome-shell-calendar-server",
            952774: "/usr/libexec/ibus-dconf",
            952775: "/usr/libexec/ibus-extension-gtk3",
            952777: "/usr/libexec/ibus-x11 --kill-daemon",
            952779: "/usr/libexec/ibus-portal",
            952805: "/usr/libexec/evolution-source-registry",
            952817: "/usr/libexec/goa-daemon",
            952819: "/usr/libexec/dconf-service",
            952837: "/usr/libexec/goa-identity-service",
            952841: "/usr/libexec/gvfs-udisks2-volume-monitor",
            952853: "/usr/libexec/gvfs-mtp-volume-monitor",
            952861: "/usr/libexec/gvfs-goa-volume-monitor",
            952868: "/usr/libexec/gvfs-gphoto2-volume-monitor",
            952875: "/usr/libexec/gvfs-afc-volume-monitor",
            952885: "/usr/libexec/gsd-power",
            952888: "/usr/libexec/gsd-print-notifications",
            952889: "/usr/libexec/gsd-rfkill",
            952890: "/usr/libexec/gsd-screensaver-proxy",
            952891: "/usr/libexec/gsd-sharing",
            952892: "/usr/libexec/gsd-smartcard",
            952893: "/usr/libexec/gsd-sound",
            952894: "/usr/libexec/gsd-xsettings",
            952895: "/usr/libexec/gsd-subman",
            952898: "/usr/libexec/gsd-wacom",
            952904: "/usr/libexec/gsd-account",
            952905: "/usr/libexec/gsd-clipboard",
            952907: "/usr/libexec/gsd-a11y-settings",
            952909: "/usr/libexec/gsd-datetime",
            952910: "/usr/libexec/evolution-calendar-factory",
            952911: "/usr/libexec/gsd-color",
            952913: "/usr/libexec/gsd-keyboard",
            952919: "/usr/libexec/gsd-housekeeping",
            952921: "/usr/libexec/gsd-mouse",
            952935: "/usr/libexec/gsd-media-keys",
            952941: "/usr/libexec/ibus-engine-simple",
            952959: "/usr/libexec/gsd-printer",
            953009: "/usr/libexec/evolution-calendar-factory-subprocess --factory all --bus-name org.gnome.evolution.dataserver.Subprocess.Backend.Calendarx952910x2 --own-path /org/gnome/evolution/dataserver/Subprocess/Backend/Calendar/952910/2",
            953028: "/usr/libexec/evolution-addressbook-factory",
            953050: "/usr/libexec/evolution-addressbook-factory-subprocess --factory all --bus-name org.gnome.evolution.dataserver.Subprocess.Backend.AddressBookx953028x2 --own-path /org/gnome/evolution/dataserver/Subprocess/Backend/AddressBook/953028/2",
            953201: "/usr/libexec/gsd-disk-utility-notify",
            953207: "/usr/bin/gnome-software --gapplication-service",
            953209: "/usr/libexec/evolution/evolution-alarm-notify",
            953210: "/usr/libexec/tracker-miner-fs",
            953212: "/usr/libexec/tracker-miner-apps",
            953217: "/usr/libexec/tracker-store"
        }

    def _expected_process_objects(self) -> List[logind_idle_session_extras.ps.Process]:
        """Expected set of processes to be parsed out of the cgroup sysfs"""
        # Yes, there are some very long lines here!
        # pylint: disable=line-too-long
        return [
            logind_idle_session_extras.ps.Process(
                    pid=772211,
                    cmdline="/usr/libexec/gvfsd-metadata"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952570,
                    cmdline="/usr/bin/Xvnc :1 -auth /u/wk/auser/.Xauthority -desktop computer:1 (auser) -fp catalogue:/etc/X11/fontpath.d -geometry 1024x768 -pn -rfbauth /u/wk/auser/.vnc/passwd -rfbport 5901 -localhost"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952581,
                    cmdline="/bin/sh /u/wk/auser/.vnc/xstartup"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952582,
                    cmdline="/usr/libexec/gnome-session-binary"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952591,
                    cmdline="dbus-launch --sh-syntax --exit-with-session"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952592,
                    cmdline="/usr/bin/dbus-daemon --syslog --fork --print-pid 5 --print-address 7 --session"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952644,
                    cmdline="/usr/libexec/at-spi-bus-launcher"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952649,
                    cmdline="/usr/bin/dbus-daemon --config-file=/usr/share/defaults/at-spi2/accessibility.conf --nofork --print-address 3"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952652,
                    cmdline="/usr/libexec/at-spi2-registryd --use-gnome-session"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952656,
                    cmdline="/usr/libexec/gvfsd"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952663,
                    cmdline="/usr/libexec/gvfsd-fuse /run/user/1002/gvfs -f -o big_writes"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952715,
                    cmdline="/usr/bin/gnome-keyring-daemon --start --components=pkcs11"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952727,
                    cmdline="/usr/bin/gnome-shell"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952766,
                    cmdline="ibus-daemon --xim --panel disable"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952768,
                    cmdline="/usr/libexec/xdg-permission-store"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952770,
                    cmdline="/usr/libexec/gnome-shell-calendar-server"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952774,
                    cmdline="/usr/libexec/ibus-dconf"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952775,
                    cmdline="/usr/libexec/ibus-extension-gtk3"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952777,
                    cmdline="/usr/libexec/ibus-x11 --kill-daemon"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952779,
                    cmdline="/usr/libexec/ibus-portal"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952805,
                    cmdline="/usr/libexec/evolution-source-registry"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952817,
                    cmdline="/usr/libexec/goa-daemon"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952819,
                    cmdline="/usr/libexec/dconf-service"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952837,
                    cmdline="/usr/libexec/goa-identity-service"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952841,
                    cmdline="/usr/libexec/gvfs-udisks2-volume-monitor"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952853,
                    cmdline="/usr/libexec/gvfs-mtp-volume-monitor"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952861,
                    cmdline="/usr/libexec/gvfs-goa-volume-monitor"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952868,
                    cmdline="/usr/libexec/gvfs-gphoto2-volume-monitor"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952875,
                    cmdline="/usr/libexec/gvfs-afc-volume-monitor"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952885,
                    cmdline="/usr/libexec/gsd-power"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952888,
                    cmdline="/usr/libexec/gsd-print-notifications"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952889,
                    cmdline="/usr/libexec/gsd-rfkill"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952890,
                    cmdline="/usr/libexec/gsd-screensaver-proxy"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952891,
                    cmdline="/usr/libexec/gsd-sharing"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952892,
                    cmdline="/usr/libexec/gsd-smartcard"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952893,
                    cmdline="/usr/libexec/gsd-sound"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952894,
                    cmdline="/usr/libexec/gsd-xsettings"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952895,
                    cmdline="/usr/libexec/gsd-subman"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952898,
                    cmdline="/usr/libexec/gsd-wacom"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952904,
                    cmdline="/usr/libexec/gsd-account"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952905,
                    cmdline="/usr/libexec/gsd-clipboard"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952907,
                    cmdline="/usr/libexec/gsd-a11y-settings"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952909,
                    cmdline="/usr/libexec/gsd-datetime"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952910,
                    cmdline="/usr/libexec/evolution-calendar-factory"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952911,
                    cmdline="/usr/libexec/gsd-color"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952913,
                    cmdline="/usr/libexec/gsd-keyboard"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952919,
                    cmdline="/usr/libexec/gsd-housekeeping"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952921,
                    cmdline="/usr/libexec/gsd-mouse"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952935,
                    cmdline="/usr/libexec/gsd-media-keys"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952941,
                    cmdline="/usr/libexec/ibus-engine-simple"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=952959,
                    cmdline="/usr/libexec/gsd-printer"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=953009,
                    cmdline="/usr/libexec/evolution-calendar-factory-subprocess --factory all --bus-name org.gnome.evolution.dataserver.Subprocess.Backend.Calendarx952910x2 --own-path /org/gnome/evolution/dataserver/Subprocess/Backend/Calendar/952910/2"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=953028,
                    cmdline="/usr/libexec/evolution-addressbook-factory"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=953050,
                    cmdline="/usr/libexec/evolution-addressbook-factory-subprocess --factory all --bus-name org.gnome.evolution.dataserver.Subprocess.Backend.AddressBookx953028x2 --own-path /org/gnome/evolution/dataserver/Subprocess/Backend/AddressBook/953028/2"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=953201,
                    cmdline="/usr/libexec/gsd-disk-utility-notify"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=953207,
                    cmdline="/usr/bin/gnome-software --gapplication-service"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=953209,
                    cmdline="/usr/libexec/evolution/evolution-alarm-notify"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=953210,
                    cmdline="/usr/libexec/tracker-miner-fs"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=953212,
                    cmdline="/usr/libexec/tracker-miner-apps"
            ),
            logind_idle_session_extras.ps.Process(
                    pid=953217,
                    cmdline="/usr/libexec/tracker-store"
            )
        ]


class Scenario1LoopbackConnectionTestCase(test_ss.LoopbackConnectionTestCase):
    """Scenario1 unit testing for the ss module

    See the docstring for the test_scenario1 module for an overall description
    of Scenario 1 (single active user w/ VNC).

    This was generated by the following shell pipeline:
        /usr/sbin/ss --all --no-header --numeric --oneline --processes --tcp
    """

    def _mock_raw_ss_output(self) -> str:
        """Input data to populate the mocked network connections table"""
        return dedent("""\
            LISTEN    0      100         127.0.0.1:25           0.0.0.0:*     users:(("master",pid=5337,fd=14))                          
            LISTEN    0      5           127.0.0.1:5901         0.0.0.0:*     users:(("Xvnc",pid=952570,fd=6))                           
            LISTEN    0      128           0.0.0.0:111          0.0.0.0:*     users:(("rpcbind",pid=4410,fd=4),("systemd",pid=1,fd=42))  
            LISTEN    0      128           0.0.0.0:22           0.0.0.0:*     users:(("sshd",pid=4960,fd=3))                             
            LISTEN    0      2048        127.0.0.1:631          0.0.0.0:*     users:(("cupsd",pid=162159,fd=8))                          
            ESTAB     0      452        10.0.0.169:22        10.0.3.209:57343 users:(("sshd",pid=1256518,fd=4),("sshd",pid=1256491,fd=4))
            SYN-SENT  0      1          10.0.0.169:45198 151.101.193.91:443   users:(("gnome-software",pid=1259638,fd=22))               
            TIME-WAIT 0      0          10.0.0.169:41180     10.0.4.244:636                                                              
            TIME-WAIT 0      0          10.0.0.169:53546     10.0.2.100:3128                                                             
            ESTAB     0      0           127.0.0.1:5901       127.0.0.1:49688 users:(("Xvnc",pid=952570,fd=23))                          
            SYN-SENT  0      1          10.0.0.169:40676 151.101.129.91:443   users:(("gnome-shell",pid=1259171,fd=34))                  
            ESTAB     0      0          10.0.0.169:22         10.0.1.53:41516 users:(("sshd",pid=1259753,fd=4),("sshd",pid=1259733,fd=4))
            ESTAB     0      0           127.0.0.1:49688      127.0.0.1:5901  users:(("sshd",pid=1256518,fd=7))                          
            ESTAB     0      0          10.0.0.169:22         10.0.1.53:39700 users:(("sshd",pid=1050325,fd=4),("sshd",pid=1050298,fd=4))
            TIME-WAIT 0      0          10.0.0.169:41178     10.0.4.244:636                                                              
            ESTAB     0      0          10.0.0.169:725       10.0.1.202:2049                                                             
            TIME-WAIT 0      0          10.0.0.169:53532     10.0.2.100:3128                                                             
            ESTAB     0      0          10.0.0.169:22         10.0.1.53:54592 users:(("sshd",pid=995013,fd=4),("sshd",pid=994974,fd=4))  
            TIME-WAIT 0      0          10.0.0.169:41196     10.0.4.244:636                                                              
            TIME-WAIT 0      0          10.0.0.169:41176     10.0.4.244:636                                                              
            SYN-SENT  0      1          10.0.0.169:49948 151.101.193.91:443   users:(("gnome-shell",pid=6978,fd=32))                     
            ESTAB     0      612        10.0.0.169:22        10.0.3.209:57353 users:(("sshd",pid=1258236,fd=4),("sshd",pid=1258006,fd=4))
            TIME-WAIT 0      0          10.0.0.169:53550     10.0.2.100:3128                                                             
            ESTAB     0      0          10.0.0.169:861       10.0.1.203:2049                                                             
            LISTEN    0      100             [::1]:25              [::]:*     users:(("master",pid=5337,fd=15))                          
            LISTEN    0      5               [::1]:5901            [::]:*     users:(("Xvnc",pid=952570,fd=7))                           
            LISTEN    0      128              [::]:111             [::]:*     users:(("rpcbind",pid=4410,fd=6),("systemd",pid=1,fd=44))  
            LISTEN    0      2048            [::1]:631             [::]:*     users:(("cupsd",pid=162159,fd=7))                          
        """)

    def _expected_listening_ports(self) -> Set[int]:
        """Expected set of listening ports parsed out of the mock ss data"""
        return set([22, 25, 111, 631, 5901])

    def _expected_peer_pairs(self) -> Set[Tuple[Union[IPv4Address,
                                                      IPv6Address], int]]:
        """Expected set of remote peers parsed from the established conns"""
        return set([
                (ip_address('10.0.1.53'), 39700),
                (ip_address('10.0.1.53'), 41516),
                (ip_address('10.0.1.53'), 54592),
                (ip_address('10.0.1.202'), 2049),
                (ip_address('10.0.1.203'), 2049),
                (ip_address('10.0.3.209'), 57343),
                (ip_address('10.0.3.209'), 57353),
                (ip_address('127.0.0.1'), 5901),
                (ip_address('127.0.0.1'), 49688)
        ])

    def _expected_connections(self) -> List[logind_idle_session_extras.ss.LoopbackConnection]:
        """Expected set of loopback connections identified from these conns"""
        return [
            logind_idle_session_extras.ss.LoopbackConnection(
                    client=logind_idle_session_extras.ss.Socket(
                        addr=ip_address('127.0.0.1'),
                        port=49688,
                        processes=[logind_idle_session_extras.ps.Process(
                            pid=1256518,
                            cmdline=""
                        )]
                    ),
                    server=logind_idle_session_extras.ss.Socket(
                        addr=ip_address('127.0.0.1'),
                        port=5901,
                        processes=[logind_idle_session_extras.ps.Process(
                            pid=952570,
                            cmdline=""
                        )]
                    )
            )
        ]
