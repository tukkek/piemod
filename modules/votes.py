# -*- coding: utf-8 -*-
#- votes: vote for map and mode at the end of a match
import piemod
from random import choice
from server import cs
from piemod import color, COLORS

MAPS_CAPTURE=["abbey","akroseum","alithia","arabic","asgard","asteroids","c_egypt","c_valley","campo","capture_night","caribbean","collusion","core_refuge","core_transfer","corruption","cwcastle","damnation","dirtndust","donya","duomo","dust2","eternal_valley","evilness","face-capture","fb_capture","fc3","fc4","fc5","forge","frostbyte","hades","hallo","haste","hidden",","",""infamy","killcore3","kopenhagen","lostinspace","mbt12","mercury","monastery","nevil_c","nitro","nmp4","nmp8","nmp9","nucleus","ogrosupply","paradigm","ph-capture","reissen","relic","river_c","serenity","snapper_rocks","spcr","subterra","suburb","tempest","tortuga","turbulence","twinforts","urban_c","valhalla","venice","xenon",]
MAPS_CTF=["abbey","akroseum","asgard","authentic","autumn","bad_moon","berlin_wall","bt_falls","campo","capture_night","catch22","core_refuge","core_transfer","damnation","desecration","dust2","eternal_valley","europium","evilness","face-capture","flagstone","forge","forgotten","garden","hallo","haste","hidden","infamy","kopenhagen","l_ctf","mach2","mbt1","mbt12","mbt4","mercury","mill","nitro","nucleus","recovery","redemption","reissen","sacrifice","shipwreck","siberia","snapper_rocks","spcr","subterra","suburb","tejen","tempest","tortuga","turbulence","twinforts","urban_c","valhalla","wdcd","xenon"] #arbana (bot issues)

MODE_REGEN=10
MODE_ECTF=17
MODE_EPROTECT=18
MODE_EHOLD=19
MODE_ECOLLECT=22

MODES_INITIAL=[MODE_ECTF,MODE_ECOLLECT,]
MODES_MISC=[MODE_EPROTECT,MODE_EHOLD,]
MODES_NAMES={
  MODE_ECTF:'ectf',
  MODE_EPROTECT:'eprotect',
  MODE_EHOLD:'ehold',
  MODE_ECOLLECT:'ecollect',
}

CANDIDATES=[]
VOTES={}

VOTING='voting'
DATA={
  VOTING:False,
}

def mapmode(m,mode): 
  cs('mode '+str(mode))
  cs('map '+m)
  
def randommap(mode):
  return choice(MAPS_CAPTURE if mode==MODE_EHOLD or mode==MODE_REGEN else MAPS_CTF)
mode=choice(MODES_INITIAL)
mapmode(randommap(mode),mode)

def playertext(args):
  if not DATA[VOTING]:
    return
  vote=int(args['text'])-1
  if 0<=vote and vote<len(CANDIDATES):
    VOTES[args['cn']]=vote
  
def gameintermission(args):
  cs('gamespeed 38')
  votees=[
    [MODE_ECTF,randommap(MODE_ECTF)],
    [MODE_ECOLLECT,randommap(MODE_ECOLLECT)],
  ]
  if len(piemod.playing())>=4:
    miscmode=choice(MODES_MISC)
    votees.append([miscmode,randommap(miscmode)])
  global CANDIDATES
  CANDIDATES=votees
  global VOTES
  VOTES={}
  voteannounce='Type:\n'
  i=0
  for votee in votees:
    i=i+1
    voteannounce+=(
      ' '+
      color(COLORS['blue'],str(i))+
      color(COLORS['default'],' for ')+
      color(COLORS['green'],MODES_NAMES[votee[0]])+
      color(COLORS['default'],' in ')+
      color(COLORS['red'],votee[1])+
      '\n'
    )
  piemod.announce(voteannounce)
  DATA[VOTING]=True
  
def gameover(args):
  DATA[VOTING]=False
  count=[]
  for v in CANDIDATES:
    count.append(0)
  most=0
  for v in VOTES:
    vote=VOTES[v]
    newcount=count[vote]+1
    count[vote]=newcount
    if newcount>most:
      most=newcount
  winners=[]
  i=0
  for c in count:
    if c==most:
      winners.append(CANDIDATES[i])
    i=i+1
  winner=choice(winners)
  mapmode(winner[1],winner[0])