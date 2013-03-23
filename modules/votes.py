# -*- coding: utf-8 -*-
#- votes: vote for map and mode at the end of a match; count ggs for handpick
import piemod, shelve, server, contextlib, random
from random import choice
from server import cs, match
from piemod import color, COLORS, debug #TODO debug

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
voteannounce=''

VOTING='voting'
GAME='game'
GAME_VOTERS='game_voters'
DATA={
  VOTING:False,
  GAME:0,
  GAME_VOTERS:[],
}

SHELVE_GAMES='shelve_games'
def gamesshelve():
  return contextlib.closing(shelve.open('piemod-votes-games',writeback=True))
with gamesshelve() as d:
  if not SHELVE_GAMES in d:
    d[SHELVE_GAMES]={}
        
def mapmode(m,mode): 
  cs('mode '+str(mode))
  cs('map '+m)
  
def randommap(mode):
  return choice(MAPS_CAPTURE if mode==MODE_EHOLD or mode==MODE_REGEN else MAPS_CTF)

def playing():
  return len(piemod.playing())
  
def newvotee(mode):
  votee=None
  try:
    with gamesshelve() as s:
      options=[]
      nplayers=playing()
      records=s[SHELVE_GAMES][mode][1 if nplayers==0 else nplayers]
      for m in records:
        for i in range(records[m]):
          options.append(m)
      if random.randint(0,1):
        votee=[mode,choice(options),True]
  except KeyError:
    pass
  if votee==None:
    votee=[mode,randommap(mode),False]
  return newvotee(mode) if votee[1]==match()['map'] else votee

first=newvotee(choice(MODES_INITIAL))
mapmode(first[1],first[0])

def playertext(args):
  if not DATA[VOTING]:
    return
  text=args['text']
  game=0
  if text=='gg':
    game=1
  elif text=='bg':
    game=-1
  cn=args['cn']
  if game!=0:
    if not cn in DATA[GAME_VOTERS]:
      DATA[GAME]+=game
      DATA[GAME_VOTERS].append(cn)
    return
  try:
    vote=int(text)-1
  except ValueError:
    return
  if 0<=vote and vote<len(CANDIDATES):
    VOTES[cn]=vote
  
def gameintermission(args):
  cs('gamespeed 38')
  with gamesshelve() as d:
    debug(str(d[SHELVE_GAMES]))
  votees=[newvotee(MODE_ECTF),newvotee(MODE_ECOLLECT),]
  if playing()>=4:
    votees.append(newvotee(choice(MODES_MISC)))
  global CANDIDATES, VOTES, voteannounce
  CANDIDATES=votees
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
      (color(COLORS['white'],' (handpicked)') if votee[2] else '')+
      '\n'
    )
  voteannounce=voteannounce[:-1]
  piemod.announce(voteannounce)
  DATA[VOTING]=True
  
def gameover(args):
  DATA[VOTING]=False
  del DATA[GAME_VOTERS][:]
  nplayers=playing()
  if DATA[GAME]>=.5*nplayers:
    with gamesshelve() as d:
      thismatch=match()
      mode=thismatch['mode']
      if not mode in d[SHELVE_GAMES]:
        d[SHELVE_GAMES][mode]={}
      m=thismatch['map']
      if not nplayers in d[SHELVE_GAMES][mode]:
        d[SHELVE_GAMES][mode][nplayers]={}
      if m in d[SHELVE_GAMES][mode][nplayers]:
        d[SHELVE_GAMES][mode][nplayers][m]+=1
      else:
        d[SHELVE_GAMES][mode][nplayers][m]=1
  with gamesshelve() as d:
    debug(str(d[SHELVE_GAMES]))
  DATA[GAME]=0
  
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
  handpickeds=[]
  for w in winners:
    if w[2]:
      handpickeds.append(w)
  if len(handpickeds)>0:
    winners=handpickeds
  winner=choice(winners)
  mapmode(winner[1],winner[0])
  return False
  
def playerconnect(args):
  if DATA[VOTING]:
    global voteannounce
    server.msg(args['cn'],voteannounce)
  
import notices
notices.add([
  'Say '+
  color(COLORS['blue'],'gg')+color(COLORS['default'],'')+
  ' (good game) or '+
  color(COLORS['red'],'bg')+color(COLORS['default'],'')+
  ' (bad) during intermission: the server will learn',
  'Handpicks were considered '+
  color(COLORS['blue'],'gg')+color(COLORS['default'],'')+
  's by a server with the same number of players',
])