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
        sys.stdout.write(colors.red + 'No args!' + colors.reset + '\n')
        return
    
    
    sys.stdout.write('Arguments received: ' + ' '.join(args.args) + '\n')
    
    return find_function(args.args[0])() or sys.stdout.write('Command not found!\n')

        