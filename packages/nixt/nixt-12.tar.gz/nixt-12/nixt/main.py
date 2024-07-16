# This file is placed in the Public Domain.
# pylint: disable=W0718


"main"


import getpass
import os
import sys
import termios
import time


from .cfg    import Config
from .cli    import CLI
from .cmds   import command
from .cons   import Console
from .defer  import Errors
from .disk   import Persist, skel
from .event  import Event
from .launch import launch
from .log    import Logging, debug
from .parse  import parse
from .utils  import daemon, forever, modnames, pidfile, privileges, skip, spl


from .cmds import scan as scancmd
from .disk import scan as scancls


from . import modules
from . import user


Cfg         = Config()
Cfg.mod     = "cmd,err,hlp,mod,thr"
Cfg.name    = __file__.split(os.sep)[-2]
Cfg.user    = getpass.getuser()
Cfg.wdr     = os.path.expanduser(f"~/.{Cfg.name}")
Cfg.pidfile = os.path.join(Cfg.wdr, f"{Cfg.name}.pid")


Persist.workdir = Cfg.wdr


def background():
    "main"
    daemon("-v" in sys.argv)
    skel()
    pidfile(Cfg.pidfile)
    privileges(Cfg.user)
    if "-v" in sys.argv:
        enable(print)
    Cfg.mod = ",".join(modnames(modules, user))
    scan(Cfg.mod, modules, user)
    init(Cfg.mod, modules, user)
    forever()


def cli():
    "command line interface."
    parse(Cfg, " ".join(sys.argv[1:]))
    Cfg.dis = Cfg.sets.dis
    Cfg.mod = ",".join(modnames(modules, user))
    enable(print)
    scan(Cfg.mod, modules, user)
    if "h" in Cfg.opts:
        cmnd("hlp", print)
        return
    cmnd(Cfg.otxt, print)


def cmnd(txt, outer):
    "do a command using the provided output function."
    if not txt:
        return None
    clis = CLI(outer)
    evn = Event()
    evn.txt = txt
    command(clis, evn)
    evn.wait()
    return evn


def console():
    "start console"
    parse(Cfg, " ".join(sys.argv[1:]))
    skel()
    if "a" in Cfg.opts:
        Cfg.mod = ",".join(modnames(modules, user))
    if "v" in Cfg.opts:
        enable(print)
        dte = " ".join(time.ctime(time.time()).replace("  ", " ").split()[1:])
        debug(f'{dte} {Cfg.name.upper()} {Cfg.opts.upper()} {Cfg.mod.upper()}')
    scan(Cfg.mod, modules, user)
    if "i" in Cfg.opts:
        thrs = init(Cfg.mod, modules, user)
        for thr in thrs:
            thr.join()
    csl = Console(print, input)
    csl.start()
    forever()


def enable(outer):
    "enable printing."
    CLI.out = Errors.out = Logging.out = outer


def init(modstr, *pkgs, disable=None):
    "scan modules for commands and classes"
    thrs = []
    for mod in spl(modstr):
        if disable and mod in spl(disable):
            continue
        for pkg in pkgs:
            modi = getattr(pkg, mod, None)
            if not modi:
                continue
            if "init" not in dir(modi):
                continue
            thrs.append(launch(modi.init))
            break
    return thrs


def scan(modstr, *pkgs, disable=""):
    "scan modules for commands and classes"
    mds = []
    for modname in spl(modstr):
        if skip(modname, disable):
            continue
        for pkg in pkgs:
            module = getattr(pkg, modname, None)
            if not module:
                continue
            scancmd(module)
            scancls(module)
    return mds


def terminal():
    "start terminal."
    wrap(console)


def wrap(func):
    "restore console."
    old2 = None
    try:
        old2 = termios.tcgetattr(sys.stdin.fileno())
    except termios.error:
        pass
    try:
        func()
    except (KeyboardInterrupt, EOFError):
        sys.stdout.write("\n")
        sys.stdout.flush()
    finally:
        if old2:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old2)


def __dir__():
    return (
        'Cfg',
        'background',
        'cli',
        'cmnd',
        'console',
        'enable',
        'init',
        'scan',
        'terminal',
        'wrap'
    )
