from collections import namedtuple
from typing import Any, Dict, Optional
from .commands import CMD_FUNCS
from itertools import chain
from typing import Optional

CommandInfo = namedtuple('CommandInfo', 'name, summary, main_function')

commands: Dict[str, Dict[str, CommandInfo]] = {
    'native': {

        'help': CommandInfo(
            'help',
            'Return command list.',
            'function'

        ),
        'ping': CommandInfo(
            'ping',
            'Return pong.',
            CMD_FUNCS['native']['ping']

        ),
        'credits': CommandInfo(
            'credits',
            'Return credits.',
            'function'
        ),
        'duplicate': CommandInfo(
            'duplicate',
            'It will duplicate the terminal',
            'function'
            ),
        'codedir': CommandInfo(
            'codedir',
            'Create a directory, change the shell location to this directory and open vs code in this directory',
            'function'
            ),
        'clear': CommandInfo(
            'clear',
            'Clear the terminal',
            'function'
            ),
        'clone': CommandInfo(
            'clone',
            'Clone a git repository',
            CMD_FUNCS['native']['clone']
            ),
        'req': CommandInfo(
            'request',
            'Send a GET request to a server',
            'function'
        ),
        'ports': CommandInfo(
            'ports',
            'Display all open ports.',
            'function'
        ),
        'port': CommandInfo(
            'port',
            'Check if a port is open.',
            'function'
        ),
        'requirements': CommandInfo(
            'requirements',
            'Install or Update the requirements from a requirements.txt file',
            'function'
        ),
    },
    'venv': {
        '': CommandInfo(
            '',
            'Create a virtual environment',
            'function'
        ),
        'activate': CommandInfo(
            'activate',
            'Activate the virtual environment',
            'function'
        ),
        'deactivate': CommandInfo(
            'deactivate',
            'Deactivate the virtual environment',
            'function'
        ),

    }
}

def find_function(name: str) -> Optional[object]:
    for cmds_tree in commands.values():
        for cmd in cmds_tree.values():
            if cmd.name == name:
                return cmd.main_function
    return None


