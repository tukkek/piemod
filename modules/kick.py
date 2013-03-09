# -*- coding: utf-8 -*-
#- kick: public ban of trolls and cheaters
import server, piemod, threading
from server import msg
from piemod import reply

BAN_GRACE_TIME=30

KICKS={}
ANNOUNCE=[]
PREVENT=[]

def lowername(p):
  return p

def nametocn(ps,args,target):
  cn=None
  target=target.lower()
  for p in ps:
    if ps[p]['name'].lower()==target:
      cn=p
      break
  if cn==None:
    for p in ps:
      name=ps[p]['name']
      if name.lower().startswith(target):
        if cn==None:
          cn=p
        else:
          reply(args,ps[cn]['name']+' or '+name+'?')
          return None
  if cn==None:
    reply(args,'Who?')
    return None
  return cn
  
def preventdouble(args):
  cn=args['cn']
  if cn in PREVENT:
    reply(args,'You already kicked or saved someone in this match')
    return True
  PREVENT.append(cn)
  return False
  
def decide(cn,p):
  name=p['name']
  if p['privilege']!=3 and KICKS[name]>0:
    server.cs('kick '+str(cn))
  del KICKS[name], ANNOUNCE[ANNOUNCE.index(name)]

def _kick_(args,parameters):
  ps=server.players()
  cn=nametocn(ps,args,parameters[0])
  if cn==None or preventdouble(args):
    return
  p=ps[cn]
  name=p['name']
  server.cs('spectator 1 '+name)
  if name in KICKS:
    KICKS[name]+=1
    if not name in ANNOUNCE:
      ANNOUNCE.append(name)
      piemod.announce(name+' will be banned in '+str(BAN_GRACE_TIME)+' seconds! To save this player type: #save '+name)
      threading.Timer(BAN_GRACE_TIME, decide, [cn,p]).start()
  else:
    KICKS[name]=0
    piemod.announce(name+', be nice. Another #kick and you will be banned!')
    
def _save_(args,parameters):
  ps=server.players()
  p=nametocn(ps,args,parameters[0])
  if p==None:
    return
  name=ps[p]['name']
  if name in KICKS and not preventdouble(args):
    KICKS[name]-=1
    piemod.announce('Someone wants to save '+name+'. If you agree the player should be kicked type: #kick '+name.lower())
  
def gameover(args):
  del PREVENT[:]

import notices
notices.add(['To kickban a player type: #kick [name or prefix]'])

import commands
commands.add(globals())