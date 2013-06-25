# -*- coding: utf-8 -*-
#- demos: record demo for all matches
import server, notices
def enable():
  server.cs('recorddemo 1')
def gamestart(args):
  enable()
enable()
server.cs('intermission') #force new game so actual first game will be recorded
notices.add(['All games are recorded, type /listdemos and /getdemo to grab the replay'])