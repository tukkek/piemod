# -*- coding: utf-8 -*-
#- maintenance: restarts the server at the end of match to reload scripts
import piemod
from piemod import color, announce, COLORS
from server import players, cs
from threading import Timer

ON='maintenance'
WARNING='maintenancewarn'
BYE='maintenancebye'
EXIT='maintenanceexit'

DATA={
  ON:False,
}
  
def playerconnect(args):
  if DATA[ON]:
    piemod.reply(args,DATA[WARNING])
  
def gameintermission(args):
  if DATA[ON]:
    quit()

def _restart(args,parameters):
  maintenance('The server will restart after this match for an automatic upgrade, you can reconnect immediately','Maintenance restart, you can reconnect immediately',1)
  
def _shutdown(args,parameters):
  maintenance('The server will shutdown after this match for maintenance','Maintenance shutdown, come again soon',42)
  
def maintenance(warn,bye,exit):
  DATA[WARNING]=(color(COLORS['red'],'MAINTENANCE MODE\n')+color(COLORS['default'],warn))
  DATA[BYE]=bye
  DATA[EXIT]=exit
  
  announce(DATA[WARNING])
  if len(players())==1:
    quit()
  DATA[ON]=True
  
def tickquit():
  cs('quit '+str(DATA[EXIT]))
  
def schedule(s,f):
  Timer(s, f).start()  

def tickkick():
  for p in players():
    cs('kick '+str(p))
  schedule(1, tickquit)
  
def quit():
  announce(DATA[BYE]) 
  schedule(1, tickkick)
  
import commands
commands.add(globals())