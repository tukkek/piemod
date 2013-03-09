# -*- coding: utf-8 -*-
#- bots: ensure at least 2 players per team, autobalance with bots, public changing of bot skill level
import piemod
from threading import Timer
from server import cs

DEFAULT_SKILL=95

import notices
notices.add([
  'Say "#botskill [1-100]" to change their skill level',
  'Never ask for balance again! We autobalance teams with bots',
  'The default bot skill level is '+str(DEFAULT_SKILL),
  "We add bots to ensure at least 2 players on each team",
])

CURRENT='bots'
SKILL='botskill'
DATA={
  CURRENT:0,
  SKILL:DEFAULT_SKILL,
}

def playerspectate(args):
  bots()
def playerconnect(args):
  bots()
def playerdisconnect(args):
  bots()
def gameover(args):
  nobots()
  Timer(2,bots).start()
  
def nobots():
  changebots(-DATA[CURRENT])
  
def _botskill_(args,parameters):
  DATA[SKILL]=int(parameters[0])
  nobots()
  bots()
    
def safeteam(teams,keys,i):
  try:
    return teams[keys[i]]
  except IndexError:
    return 0
        
def bots():
  ps=piemod.playing()
  nps=len(ps)
  if nps==0:
    nobots()
    return
  teams={}
  for p in ps:
    team=ps[p]['team']
    teams[team]=(teams[team]+1) if team in teams else 1
  if len(teams)>2:
    nobots()
    return
  if nps>2:
    teamskeys=list(teams.keys())
    team0=safeteam(teams,teamskeys,0)
    team1=safeteam(teams,teamskeys,1)
    diff=team0-team1
    if diff==0:
      nobots()
      return
    bots=diff if diff>0 else -diff
  else:
    bots=4-nps
  current=DATA[CURRENT]
  changebots(bots-current)
  
def changebots(add):
  DATA[CURRENT]+=add
  if add>0:
    for i in range(0,add):
      cs('addbot '+str(DATA[SKILL]))
  else:
    for i in range(add,0):
      cs('delbot')

import commands
commands.add(globals())