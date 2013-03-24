ICOMMAND(addbot, "i", (int* s),aiman::addai(clamp(*s, 1, 101), 4));
ICOMMAND(delbot, "", (),aiman::deleteai());
ICOMMAND(map, "s", (char* map),changemap(map,gamemode));
ICOMMAND(mode, "i", (int* mode),gamemode=*mode);
ICOMMAND(gamespeed, "i", (int* speed),changegamespeed(*speed));
ICOMMAND(kick, "i", (int* victim),{addban(getclientip(*victim), 4*60*60000);disconnect_client(*victim, DISC_KICK);});
ICOMMAND(quit, "i", (int* code),exit(*code));
ICOMMAND(intermission, "", (),startintermission());

int parseplayer(const char *arg){
    char *end;
    int n = strtol(arg, &end, 10);
    if(*arg && !*end){
        if(!clients.inrange(n)) return -1;
        return n;
    }
    // try case sensitive first
    loopv(clients){
        clientinfo *o = clients[i];
        if(!strcmp(arg, o->name)) return o->clientnum;
    }
    // nothing found, try case insensitive
    loopv(clients){
        clientinfo *o = clients[i];
        if(!strcasecmp(arg, o->name)) return o->clientnum;
    }
    return -1;
}
void togglespectator(int val, const char *who){
    int spectator=parseplayer(who);
    clientinfo *spinfo = (clientinfo *)getclientinfo(spectator); // no bots
    if(!spinfo) return;
    if(spinfo->state.state!=CS_SPECTATOR && val) {
        if(spinfo->state.state==CS_ALIVE) suicide(spinfo);
        if(smode) smode->leavegame(spinfo);
        spinfo->state.state = CS_SPECTATOR;
    } else if(spinfo->state.state==CS_SPECTATOR && !val) {
        spinfo->state.state = CS_DEAD;
        spinfo->state.respawn();
    }
    sendf(-1, 1, "ri3", N_SPECTATOR, spectator, val);
}
ICOMMAND(spectator, "is", (int *val, char *who), togglespectator(*val, who));

void setteam(int* who, const char *team)
{
    clientinfo *wi = clients[*who];
    if(wi->state.state==CS_ALIVE) suicide(wi);
    copystring(wi->team, team, MAXTEAMLEN+1);
    aiman::changeteam(wi);
    sendf(-1, 1, "riisi", N_SETTEAM, *who, wi->team, 1);
}
COMMAND(setteam, "is");
