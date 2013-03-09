# -*- coding: utf-8 -*-
#- commands: framework for modules to easily support chat #commands
import piemod, server, traceback
from piemod import reply

COMMAND_FLAG='_' # prefix makes a server command, suffix makes public command

VAR_COMMANDS='commands'
DATA={
  VAR_COMMANDS:{},
}

def translate(name):
  name=name[1:]
  if name.endswith(COMMAND_FLAG):
    name=name[:-1]
  return '#'+name

def playertext(args):
  text=args['text']
  if text[0]!='#':
    return
  p=piemod.players()[args['cn']]
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
    if function.__name__[-1:]!=COMMAND_FLAG and not piemod.isadmin(p):
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
notices.add(["Any #command can be written using it's prefix (#com or #c)"])