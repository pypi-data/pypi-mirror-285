from .native.ping import ping
from .native.clone import clone


CMD_FUNCS = {
    'native': {
        'ping': ping,
        'clone': clone
    }
}



