/*!
 * @file
 * @author Kek <http://cuddle-clan.org>
 *
 * Piemod provides a Python engine to Cube 2: Sauerbraten servers.
 *
 * Certain module functions will be executed upon determined server events.
 * Those events are listed in the "Function Documentation" section.
 *
 * @section Links
 *
 * Code repository, documentation and bug tracking system: https://github.com/tukkek/piemod
 *
 * Chat: #piemod at irc.gamesurge.net or https://gamesurge.net/chat/piemod
 *
 * @section handlers Python event handlers
 *
 * Functions that can be defined as entry-points to the modules are named here as "event_foo".
 * In Python you should name them as "foo" only.
 *
 * Handlers take only one variable: a dictionary, whose keys are the parameter names in \a italic here.
 *
 * @section server Server module
 *
 * Importing the provided 'server' in a module enables you to communicate back with the server.
 * The function listed here as 'server_bar' can then be found in Python as 'server.bar'.
 *
 * @section example Example (welcome.py)
 *
 * @code
 * import server
 *
 * welcome = 'Hello world!'
 *
 * def connect(args):
 *  server.msg(args['cn'],welcome)
 *  server.cs('quit')
 * @endcode
 *
 * @section Types
 *
 * This document shows C parameter types. It's easy to assume from those which Python types they will convert to:
 *
 * <table>
 *  <tr><td><b>C</b></td><td><b>Python</b></td></tr>
 *  <tr><td>bool</td><td>bool</td></tr>
 *  <tr><td>int</td><td>int</td></tr>
 *  <tr><td>char*</td><td>str</td></tr>
 * </table>
 *
 * @section Configuration
 *
 * Add the line below to server-init.cfg, where [path] is the directory Python modules should be loaded from.
 *
 * @code
 * alias piemodfolder [path]
 * @endcode
 *
 * @section License
 * ZLIB.
 * It can be found in <a href="https://github.com/tukkek/piemod/blob/master/readme_source.txt#L45">src/readme_source.txt</a>.
 *
 * As required, all modified files should carry a header notice.
 * Piemod covers only source files, no media is included.
 *
 * @section dp Development philosophy
 *
 * @subsection pc Python > C
 * Always prefer Python modules to changing C.
 * Python is easier and faster to write, debug and maintain.
 *
 * @subsection cp CubeScript > Piemod
 * Always prefer adding CubeScript support to creating new Python<->C stuff.
 *
 * @subsection deo Doxygen > *
 * Always update the documentation before the code and revise it after coding.
 * Fail to do so and you might be liable to users requesting your sepukku.
 *
 * @section gf Generated files
 *
 * @subsection pd piemod.diff
 * Git <a href='https://github.com/tukkek/piemod/blob/master/piemod.diff'>diff</a> from previous release.
 *
 * @subsection mrt modules/README.txt
 * <a href='https://github.com/tukkek/piemod/blob/master/modules/README.txt'>Brief description</a> of the example Python modules.
 *
 * @section hw Help wanted!
 * Piemod is looking for commit contributors who can extend the source code and respect the project's philosophy.
 * New or modified Python modules are also welcome, as we aim to offer more features in the default package.
 *
 * You can also help by opening issues on the <a href='https://github.com/tukkek/piemod/issues'>bug tracking system</a> for feature requests or bug reports.
 *
 * @section Dependencies
 *
 * To run piemod you will need a <a href="http://www.python.org/download/releases/3.3.0/">Python 3 runtime</a> in your system.
 *
 * What you will need to compile:
 * <ul>
 * <li><a href="http://www.python.org/download/releases/3.3.0/">Python 3.3m development libraries</a></li>
 * <li><a href="http://www.doxygen.org">Doxygen</a> (not needed if you remove the <a href="https://github.com/tukkek/piemod/blob/master/Makefile#L184">single Doxygen line</a> from the makefile)</li>
 * <li>Cube 2: Sauerbraten <a href="https://github.com/tukkek/piemod/blob/master/readme_source.txt#L45">dependencies</a>.</li>
 * </ul>
 */
#include <Python.h>
#include <setjmp.h>
#include <stdlib.h>
#include <dirent.h>

extern void suicide(clientinfo *ci);
namespace aiman{
    extern bool dorefresh;
}

//configuration
//#define PIEMOD_DIR "/home/alex/bin/sauerbraten/collect/piemod/piemod/src/piemod/"
#define EXIT_AFTER_INIT false

//constants
#define ABNORMAL_EXIT_STATUS 420

vector<PyObject*> modules;

void abort(){
    exit(ABNORMAL_EXIT_STATUS);
}

void clean(PyObject* cleanme[]){
    for (unsigned int i=0;i<sizeof cleanme/sizeof cleanme[0];i++){
        Py_DECREF(cleanme[i]);
    }
}

/*!
 * Executes CubeScript.
 * The avaiable functions are easy to read in <a href='https://github.com/tukkek/piemod/blob/master/fpsgame/piemodcs.cpp'>piemodcs.cpp</a>, all should work as expected in client-side cubescript.
 * @param cubescript CubeScript to be executed.
 * @return Result from the code execution.
 */
int server_cs(const char * cubescript) {
    return execute(cubescript);
}

static PyObject* _server_cs(PyObject *self, PyObject *args) {
    const char *command;
    return PyArg_ParseTuple(args, "s", &command)?PyLong_FromLong(server_cs(command)):NULL;
}

/*!
 * Get all players' information.
 * @return Dictionary of all players by client number.
 * Each player is a dictionary with the following keys:
 * <table>
 *  <tr><td><b>Key</b></td><td><b>Type</b></td><td><b>Description</b></td></tr>
 *  <tr><td>name</td><td>str</td><td>Nickname</td></tr>
 *  <tr><td>privilege</td><td>int</td><td>Privilege level (none=0, master=1, auth=2, admin=3)</td></tr>
 *  <tr><td>status</td><td>int</td>
 *      <td>Player status (alive=0, dead=1, spawning=2, lagged=3, editing=4, spectator=5)</td></tr>
 *  <tr><td>team</td><td>str</td><td>Player's current team</td></tr>
 * </table>
 */
PyObject* server_players() {
    PyObject *dict=PyDict_New();
    loopv(clients) {
        clientinfo* c=clients[i];
        if (c->state.aitype!=AI_NONE){
            continue;
        }
        PyObject *p=PyDict_New(),
                *cnK=PyUnicode_FromString("name"),
                *cnP=PyUnicode_FromString(c->name),
                *privK=PyUnicode_FromString("privilege"),
                *privP=PyLong_FromLong(c->privilege),
                *statusK=PyUnicode_FromString("status"),
                *statusP=PyLong_FromLong(c->state.state),
                *teamK=PyUnicode_FromString("team"),
                *teamP=PyUnicode_FromString(c->team)
                ;
        PyDict_SetItem(p,cnK,cnP);
        PyDict_SetItem(p,privK,privP);
        PyDict_SetItem(p,statusK,statusP);
        PyDict_SetItem(p,teamK,teamP);
        PyDict_SetItem(dict,PyLong_FromLong(c->clientnum),p);
    }
    return dict;
}

static PyObject* _server_players(PyObject *self, PyObject *args) {
    return PyArg_ParseTuple(args, "")?server_players():NULL;
}

/*!
 * Get match information.
 * @return Dictionary with the following keys:
 * <table>
 *  <tr><td><b>Key</b></td><td><b>Type</b></td><td><b>Description</b></td></tr>
 *  <tr><td>map</td><td>str</td><td>Name of the map currently being played</td></tr>
 *  <tr><td>mode</td><td>int</td><td>
 *      Current game mode (-1=demo playback, 0=ffa, 1=coop edit, 2=teamplay, 3=instagib, 4=instagib team,
 *      5=efficiency, 6=efficiency team, 7=tactics mode, 8=tactics team mode, 9=capture mode, 10=regen capture,
 *      11=ctf, 12=insta, 13=protect, 14=insta protect, 15=hold mode,16=insta hold, 17=efficiency ctf,
 *      18=efficiency protect, 19=efficiency hold, 20=collect, 21=insta collect, 22=efficiency collect)
 *  </td></tr>
 * </table>
 */
PyObject* server_match() {
    PyObject *p=PyDict_New(),
            *mapK=PyUnicode_FromString("map"),
            *mapP=PyUnicode_FromString(smapname),
            *modeK=PyUnicode_FromString("mode"),
            *modeP=PyLong_FromLong(gamemode),
            *scoresK=PyUnicode_FromString("scores"),
            *scoresP=PyDict_New()
            ;
    PyDict_SetItem(p,mapK,mapP);
    PyDict_SetItem(p,modeK,modeP);
    PyDict_SetItem(p,scoresK,scoresP);
    loopv(clients)
    {
        clientinfo *o = clients[i];
        PyDict_SetItem(scoresP,PyUnicode_FromString(o->team),PyLong_FromLong(smode->getteamscore(o->team)));
    }
    return p;
}

static PyObject* _server_match(PyObject *self, PyObject *args) {
    return PyArg_ParseTuple(args, "")?server_match():NULL;
}

/*!
 * Send message to a player.
 * @param cn Number of the destination client for the message.
 * @param text Message to be sent.
 */
void server_msg(int cn,char* text) {
    sendf(cn, 1, "ris", N_SERVMSG, text);
}

static PyObject* _server_msg(PyObject *self, PyObject *args) {
    int cn;
    char* text;
    if (PyArg_ParseTuple(args, "is", &cn,&text)){
        server_msg(cn,text);
        Py_RETURN_NONE;
    } else {
        return NULL;
    }
}

static PyMethodDef ServerMethods[] = {
    {"cs",  _server_cs, METH_VARARGS,""},
    {"players",  _server_players, METH_VARARGS,""},
    {"msg",  _server_msg, METH_VARARGS,""},
    {"match",  _server_match, METH_VARARGS,""},
    {NULL, NULL, 0, NULL} // Sentinel
};
static struct PyModuleDef server = {PyModuleDef_HEAD_INIT,"server",NULL,-1,ServerMethods};

PyMODINIT_FUNC
PyInit_server(void) {
    return PyModule_Create(&server);
}

void piemod(){
    conoutf(CON_INIT,"init: piemod");

    const char* folder=getalias("piemodfolder");
    conoutf(CON_INIT,"module folder: %s",folder);
    setenv("PYTHONPATH", folder, 0);
    PyImport_AppendInittab("server", PyInit_server);
    Py_Initialize();

    DIR *dir= opendir(folder);
    if (dir == NULL) {
        conoutf(CON_INIT,"Can't open piemod modules dir!");
        abort();
    }

    while (true) {
        struct dirent *ent=readdir(dir);
        if (ent==NULL){
            break;
        }

        char* file=ent->d_name;
        if (!strstr(file,".py")||strstr(file,".pyc")||strstr(file,".py~")) {
            continue;
        }
        for (int i=1;;i++) {
            if (file[i]=='.'){
                char newfile[0];
                copystring(newfile,file,i+1);
                file=newfile;
                break;
            }
        }

        PyObject *pName=PyUnicode_FromString(file),*pModule=PyImport_Import(pName);
        if (pModule == NULL) {
            PyErr_Print();
            conoutf(CON_INIT,"Failed to load: %s", file);
            abort();
        }
        conoutf(CON_INIT,"Module: %s", file);
        modules.put(pModule);

        PyObject *cleanme[]={pName};
        clean(cleanme);
    };
    closedir(dir);
    if (EXIT_AFTER_INIT){
        exit(0);
    }
}

PyObject* piemod_event(const char* function,PyObject* dict){
    PyObject *pArgs=PyTuple_New(1),*output=NULL;
    PyTuple_SetItem(pArgs, 0, dict); //steals dict reference
    for (int i=0;i<modules.length();i++){
        PyObject *pReturn=NULL,*pFunc=PyObject_GetAttrString(modules[i], function);
        if (pFunc && PyCallable_Check(pFunc)) {
            pReturn = PyObject_CallObject(pFunc, pArgs);
            if (pReturn == NULL) {
                conoutf(CON_ERROR,"piemod: error");
                PyErr_Print();
            } else {
                if (pReturn!=Py_None&&output==NULL) { //for now it only considers only the first non-None output
                    Py_INCREF(pReturn);
                    output=pReturn;
                } else {
                    //Py_DECREF(pReturn);
                }
            }
        } else if (PyErr_Occurred()){
            PyErr_Clear();
        }

        PyObject *cleanme[]={pFunc,pReturn};
        for (unsigned int i=0;i<sizeof cleanme/sizeof cleanme[0];i++){
            Py_XDECREF(cleanme[i]);
        }
    }

    PyObject* cleanme[]={pArgs};
    clean(cleanme);
    return output; //passes reference
}

/*!
 * New client connected. Adding bots will not raise an event.
 * @param cn The client number of the connecting client.
 */
void event_playerconnect(int cn){
    PyObject *dict=PyDict_New(),
            *cnK=PyUnicode_FromString("cn"),
            *cnP=PyLong_FromLong(cn)
            ;
    PyDict_SetItem(dict,cnK,cnP);
    piemod_event("playerconnect",dict);

    PyObject *cleanme[]={cnK,cnP};
    clean(cleanme);
}

/*!
 * Chat message was sent.
 * @param cn Number of the client who sent the message.
 * @param text Text sent.
 * @param team False if the message was public, True if only for the author's team.
 * @return If you return False the message will be blocked and not sent to other players.
 */
bool event_playertext(int cn,string text, bool team) {
    PyObject *dict=PyDict_New(),
            *cnK=PyUnicode_FromString("cn"),
            *cnP=PyLong_FromLong(cn),
            *textK=PyUnicode_FromString("text"),
            *textP=PyUnicode_FromString(text),
            *teamK=PyUnicode_FromString("team"),
            *teamP=PyBool_FromLong(team)
            ;
    PyDict_SetItem(dict,cnK,cnP);
    PyDict_SetItem(dict,teamK,teamP);
    PyDict_SetItem(dict,textK,textP);
    PyObject* output = piemod_event("playertext",dict);

    PyObject* cleanme[]={cnK,cnP,teamK,teamP,textK,textP};
    clean(cleanme);
    if (output!=NULL){
        Py_DECREF(output);
        if (output==Py_False){
            return false;
        }
    }
    return true;
}

/*!
 * Called a certain delay after event_gameintermission() .
 * @return If you return False then a new map is not going to be automatically loaded.
 * This can be done for manual control over map and mode rotation.
 */
bool event_gameover() {
    PyObject *dict=PyDict_New()
            ;
    PyObject* output = piemod_event("gameover",dict);

    /*PyObject *cleanme[]={dict};
    clean(cleanme);*/

    if (output!=NULL){
        Py_DECREF(output);
        if (output==Py_False){
            return false;
        }
    }
    return true;
}

/*!
 * Called at the beggining of a match.
 */
void event_gamestart() {
    piemod_event("gamestart",PyDict_New());
}

/*!
 * A player has moved from or to spectator.
 * @param cn Client number of the player.
 * @param spectator True if client is now spectating, False if he is no longer spectating.
 */
void event_playerspectate(int cn,bool spectator) {
    PyObject *dict=PyDict_New(),
            *cnK=PyUnicode_FromString("cn"),
            *cnP=PyLong_FromLong(cn),
            *specK=PyUnicode_FromString("spectator"),
            *specP=PyBool_FromLong(spectator)
            ;
    PyDict_SetItem(dict,cnK,cnP);
    PyDict_SetItem(dict,specK,specP);
    piemod_event("playerspectate",dict);

    PyObject *cleanme[]={cnK,cnP,specK,specP};
    clean(cleanme);
}

/*!
 * A player has left the game.
 * @param cn Client number of the player.
 */
void event_playerdisconnect(int cn) {
    PyObject *dict=PyDict_New(),
            *cnK=PyUnicode_FromString("cn"),
            *cnP=PyLong_FromLong(cn)
            ;
    PyDict_SetItem(dict,cnK,cnP);
    piemod_event("playerdisconnect",dict);

    PyObject *cleanme[]={cnK,cnP};
    clean(cleanme);
}

/*!
 * A player has switched team.
 * @param cn Client number of the player.
 */
void event_playerswitchteam(int cn) {
    PyObject *dict=PyDict_New(),
            *cnK=PyUnicode_FromString("cn"),
            *cnP=PyLong_FromLong(cn)
            ;
    PyDict_SetItem(dict,cnK,cnP);
    piemod_event("playerswitchteam",dict);

    PyObject *cleanme[]={cnK,cnP};
    clean(cleanme);
}

/*!
 * Called when a game ends and the scoreboard is shown.
 */
void event_gameintermission(){
    PyObject *dict=PyDict_New()
            ;
    piemod_event("gameintermission",dict);

    /*PyObject *cleanme[]={dict};
    clean(cleanme);*/
}

