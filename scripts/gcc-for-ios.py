#!/usr/bin/env python3
"""Adapt GNU driver flags/data directives; preserve the upstream game ABI."""
import base64
import os
import pathlib
import re
import subprocess
import sys

args = [arg for arg in sys.argv[1:] if not arg.startswith('-miphoneos-version-min=')]
result = subprocess.run([os.environ['MELEE_GNU_COMPILER'], *args])
if result.returncode == 0 and '-S' in args and '-o' in args:
    output = pathlib.Path(args[args.index('-o') + 1])
    assembly = output.read_text()
    assembly = re.sub(
        r'^\s*\.base64\s+"([A-Za-z0-9+/=]+)"\s*$',
        lambda match: '\t.byte ' + ','.join(str(byte) for byte in base64.b64decode(match[1])),
        assembly, flags=re.M)
    output.write_text(assembly)
sys.exit(result.returncode)
