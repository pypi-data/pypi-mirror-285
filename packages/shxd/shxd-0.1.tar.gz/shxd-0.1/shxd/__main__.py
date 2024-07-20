import sys
import argparse
from .parser import default_parser
from .utils import colors, send_warn
from . import find_function

def main():

    parser = default_parser
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments to be processed by the CLI.')

    args = parser.parse_args()

    
    if not args.args:
        send_warn('to use shxd you need to pass commands or arguments.')
        args.args.append('')
    
    
#    sys.stdout.write(colors.red + 'No args!' + colors.reset + '\n')

    
    
 #   sys.stdout.write('Arguments received: ' + ' '.join(args.args) + '\n')
    cmd = find_function(args.args[0])
    if cmd:
        if len(args.args) > 1:
            cmd(*args.args[1:])
        else:
            cmd()
    else:
        return sys.stdout.write('Command not found!\n')

        