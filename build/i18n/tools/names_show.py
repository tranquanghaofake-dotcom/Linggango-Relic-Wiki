#!/usr/bin/env python3
"""python3 build/i18n/tools/names_show.py <list.json> <from> <to>: prints `index English` for a slice of a names list (names_todo.js writes it), the lines to translate in one batch."""
import sys, json
u = json.load(open(sys.argv[1], encoding='utf-8'))
for i in range(int(sys.argv[2]), min(int(sys.argv[3]), len(u))): print(i, u[i])
