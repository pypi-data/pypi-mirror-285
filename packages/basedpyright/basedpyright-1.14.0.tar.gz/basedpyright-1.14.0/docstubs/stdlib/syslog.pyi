import sys
from typing import Literal, overload

if sys.platform != "win32":
    LOG_ALERT: Literal[1]
    LOG_AUTH: Literal[32]
    LOG_AUTHPRIV: Literal[80]
    LOG_CONS: Literal[2]
    LOG_CRIT: Literal[2]
    LOG_CRON: Literal[72]
    LOG_DAEMON: Literal[24]
    LOG_DEBUG: Literal[7]
    LOG_EMERG: Literal[0]
    LOG_ERR: Literal[3]
    LOG_INFO: Literal[6]
    LOG_KERN: Literal[0]
    LOG_LOCAL0: Literal[128]
    LOG_LOCAL1: Literal[136]
    LOG_LOCAL2: Literal[144]
    LOG_LOCAL3: Literal[152]
    LOG_LOCAL4: Literal[160]
    LOG_LOCAL5: Literal[168]
    LOG_LOCAL6: Literal[176]
    LOG_LOCAL7: Literal[184]
    LOG_LPR: Literal[48]
    LOG_MAIL: Literal[16]
    LOG_NDELAY: Literal[8]
    LOG_NEWS: Literal[56]
    LOG_NOTICE: Literal[5]
    LOG_NOWAIT: Literal[16]
    LOG_ODELAY: Literal[4]
    LOG_PERROR: Literal[32]
    LOG_PID: Literal[1]
    LOG_SYSLOG: Literal[40]
    LOG_USER: Literal[8]
    LOG_UUCP: Literal[64]
    LOG_WARNING: Literal[4]

    if sys.version_info >= (3, 13):
        LOG_FTP: Literal[88]
        LOG_INSTALL: Literal[112]
        LOG_LAUNCHD: Literal[192]
        LOG_NETINFO: Literal[96]
        LOG_RAS: Literal[120]
        LOG_REMOTEAUTH: Literal[104]

    def LOG_MASK(pri: int, /) -> int:
        """Calculates the mask for the individual priority pri."""
        ...
    def LOG_UPTO(pri: int, /) -> int:
        """Calculates the mask for all priorities up to and including pri."""
        ...
    def closelog() -> None:
        """Reset the syslog module values and call the system library closelog()."""
        ...
    def openlog(ident: str = ..., logoption: int = ..., facility: int = ...) -> None:
        """Set logging options of subsequent syslog() calls."""
        ...
    def setlogmask(maskpri: int, /) -> int:
        """Set the priority mask to maskpri and return the previous mask value."""
        ...
    @overload
    def syslog(priority: int, message: str) -> None:
        """
        syslog([priority=LOG_INFO,] message)
        Send the string message to the system logger.
        """
        ...
    @overload
    def syslog(message: str) -> None:
        """
        syslog([priority=LOG_INFO,] message)
        Send the string message to the system logger.
        """
        ...
