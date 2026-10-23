#!/usr/bin/env python3
import sys
sys.path.insert(0, '.')
import importlib.util
spec = importlib.util.spec_from_file_location('agent_daemon', 'agent_daemon.py')
mod = importlib.util.module_from_spec(spec)
# Only import, don't execute __main__
spec.loader.exec_module(mod)
mod.build_html()
print('HTML rebuilt')
