#!/usr/bin/env python3
# coding: utf-8
__author__ = "uknbr"

import sys
script = "car.py"
sys.argv = [script, "-r", "es"]
exec(open(script).read())