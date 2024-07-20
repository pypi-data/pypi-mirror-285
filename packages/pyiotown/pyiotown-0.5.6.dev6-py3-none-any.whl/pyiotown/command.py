all = ('__version__')

from pbr.version import VersionInfo
__version__ = VersionInfo('pyiotown').release_string()

import argparse
import sys

def main():
  parser = argparse.ArgumentParser(description=f"PyIOTOWN Command Line Interface version {__version__}")
  parser.add_argument('username', nargs='?', help='Username')
  parser.add_argument('url', nargs='?', help='IOTOWN server URL')
  parser.add_argument('command', nargs='?', help='up\nload')
  parser.add_argument('--dev', nargs='?', help='Device ID')
  parser.add_argument('--data', nargs='?', help='Data string')
  
  args = parser.parse_args()

  if args.command == 'upload':
    print(args.command)
  else:
    print(f"Unrecognized command: '{args.command}'", file=sys.stderr)
    return 1
  return 0

if __name__ == 'main':
  main()
