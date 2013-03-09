# -*- coding: utf-8 -*-
#- notices: framework for server announcements
import piemod, random, traceback
from threading import Timer

VAR_NOTICES='notices'
DATA={
  VAR_NOTICES:[],
}

NOTICES=[]
def add(fs):
  for f in fs:
    NOTICES.append(f)

def msgtick():
  if len(DATA[VAR_NOTICES])==0:
    DATA[VAR_NOTICES]=list(NOTICES)
    random.shuffle(DATA[VAR_NOTICES])
  piemod.announce(DATA[VAR_NOTICES].pop())
  schedulemsgs(5)
    
def schedulemsgs(mins):
  Timer(mins*60, msgtick).start()
schedulemsgs(2.5)