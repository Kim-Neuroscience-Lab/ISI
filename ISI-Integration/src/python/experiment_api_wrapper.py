#!/usr/bin/env python3
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
server_path = os.path.join(current_dir, "simple_server.py")
os.execv(sys.executable, [sys.executable, server_path])
