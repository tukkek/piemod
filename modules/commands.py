# -*- coding: utf-8 -*-
#- commands: framework for modules to easily support chat #commands
import piemod, server, traceback
from piemod import reply

COMMAND_FLAG='_' # prefix makes a server command, suffix makes public command
ONLY_PREFIX_IS_OK="Any #command can be written using it's prefix (#com or #c)"

VAR_COMMANDS='commands'
DATA={
  VAR_COMMANDS:{},
}

def translate(name):
  name=name[1:]
  if name.endswith(COMMAND_FLAG):
    name=name[:-1]
  return '#'+name
  
def denyaccess(name,player):
  return name[-1:]!=COMMAND_FLAG and not piemod.isadmin(player)

def player(args):
  return piemod.players()[args['cn']]

def playertext(args):
  text=args['text']
  if text[0]!='#':
    return
  p=player(args)
  parameters=text[1:].strip().split(' ')
  functions=DATA[VAR_COMMANDS]
  function=None
  for f in functions: #permits using only initial command letters
    command=COMMAND_FLAG+parameters[0]
    if f.startswith(command):
      if f==command:
        function=functions[f]
        break
      if function:
        reply(args,'Not enough letters, consider typing the full command')
        return
      else:
        function=functions[f]
  if function:
    if denyaccess(function.__name__,p):
      reply(args,'403')
      return
    try:
      function(args,parameters[1:])
    except Exception as e:
      reply(args,e.__class__.__name__+': '+str(e))
      traceback.print_exc()
  else:
    reply(args,'Unknown command')
  
def _cs(args,parameters):
  if len(parameters)==0:
    reply(args,'Usage: #cs [cubescript]')
    return
  
  cmd=''
  for p in parameters:
    cmd+=p+' '
  server.cs(cmd[:-1])
  
def _help_(args,txt):
  help='Avaiable commands: '
  commands=[]
  for f in DATA[VAR_COMMANDS]:
    if not denyaccess(DATA[VAR_COMMANDS][f].__name__,player(args)):
      commands.append(f[1:])
  for c in sorted(commands):
    help+='#'+c+' '
  reply(args,help+'\n'+ONLY_PREFIX_IS_OK)

def _commands_(args,txt):
  _help_(args,txt)

def add(fs):
  for f in fs:
    if f[:1]==COMMAND_FLAG and not f[:2]=="__":
      if f[-1:]==COMMAND_FLAG:
        name=f[:-1]
      else:
        name=f
      commands=DATA[VAR_COMMANDS]
      if name in commands:
        raise Exception('Same command found in multiple modules: '+f)
      commands[name]=fs[f]
add(globals())

import notices
notices.add([ONLY_PREFIX_IS_OK])