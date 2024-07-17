import sys
from stcube.core import CommandExecutor
from stcube._fnc_modules import Module
from stcube._fnc_library import Library
from stcube._fnc_body import FNew, FOpen, FUpdate, FClose

def cmd_entry(param=None):
    _help = """
    Usage: 
        stcube : Start the stcube.
        stcube h|help: Show this help.
        stcube l|last|n|next|p|previous: Open the last project and Start the stcube.
        stcube [project_path]: Open the project in the path and Start the stcube.
    """
    if len(sys.argv) > 1:
        param = sys.argv[1]
    if param and param.upper() in ['HELP', 'H']:
        print( _help )
        return
    elif param and param.upper() in ['LAST', "L", "NEXT", "N", "PREVIOUS", "P"]:
        lpp = HOME_F._LastProjectPath
        target_projet = lpp if lpp else None
    else:
        target_projet = param

    ce = CommandExecutor()

    ce.add(FNew)
    ce.add(FOpen)
    ce.add(FUpdate)
    ce.add(FClose)
    ce.add(Library)
    ce.add(Module)

    ce()  # start the command executor


if __name__ == '__main__':
    cmd_entry(r"C:\Users\22290\Desktop\ATK-M100-407VG")

