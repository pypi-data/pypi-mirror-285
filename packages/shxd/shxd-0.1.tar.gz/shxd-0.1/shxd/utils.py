from typing import Dict, Optional
import sys

class Colors:
    COLORS: Dict[str, str] = {
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'reset': '\033[0m',
    }

    def __getattr__(self, name: str) -> str:
        if name in self.COLORS:
            return self.COLORS[name]
        raise AttributeError(f"Color '{name}' not found.")

    @classmethod
    def get_color(cls, color_name: str) -> str:
        return cls.COLORS.get(color_name, cls.COLORS['reset'])

def send_warn(message: str, color: Optional[str] = 'yellow') -> None:
    sys.stdout.write(Colors().yellow + "WARNING: " + message + Colors().reset + '\n\n') 


colors = Colors()
