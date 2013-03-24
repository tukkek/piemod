# -*- coding: utf-8 -*- 
import server
from server import players

def debug(txt):
  print(' '+txt)
  
  ps=players()
  for p in ps:
    if isadmin(ps[p]):
      msg(p,txt)

COLORS={
  'green':0,
  'blue':1,
  'yellow':2,
  'red':3,
  'black':4,
  'purple':5,
  'orange':6,
  'default':6,
  'white':7,
}
def color(color,txt):
  return '\f'+str(color)+txt

def msg(cn,txt):
  server.msg(cn,color(COLORS['default'],txt))
    
def announce(txt):
  for cn in players():
    msg(cn,txt)
  
def playerconnect(args):
  print('Connected: '+players()[args['cn']]['name'])
  reply(args,'Welcome to a piemod server')
  reply(args,'More info at GitHub or gamesurge.net/chat/piemod')
  
def isadmin(player):
  return player['privilege']==3
  
def isspectating(player):
  return player['status']==5
  
def debugplayers():
  ps=players()
  for cn in ps:
    p=ps[cn]
    s=' '+str(cn)
    for key in ['name','privilege','status','team',]:
      s+=' '+str(p[key])
    debug(s)
    
def playing():
  allps=players()
  ps={}
  for p in allps:
    if not isspectating(allps[p]):
      ps[p]=allps[p]
  return ps

def reply(args,txt):
  msg(args['cn'],txt)