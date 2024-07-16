# This file is placed in the Public Domain.


"help"


SEP = "/"
NAME = __file__.split(SEP)[-3]
TXT = f"""{NAME.upper()} - you have been {NAME}!

    {NAME}   <cmd> [key=val] [key==val]
    {NAME}d  [-v]
    {NAME}sh [-a] [-i] [-v] [mod=mod1,mod2]

OPTIONS

    -a     use all modules
    -h     show help
    -i     start services
    -v     use verbose

COMMANDS
    
    $ {NAME} cmd
    cfg,cmd,dpl,err,exp,imp,mod,mre,nme,pwd,rem,res,rss,thr

MODULES

    $ {NAME} mod
    cmd,err,fnd,hlp,irc,log,mod,req,rss,rst,srv,tdo,thr,tmr,udp,upt
"""


def hlp(event):
    "show help"
    event.reply(TXT)


hlp.target = "cli"
