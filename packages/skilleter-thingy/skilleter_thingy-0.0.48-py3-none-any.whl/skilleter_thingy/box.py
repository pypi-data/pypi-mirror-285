#! /usr/bin/env python3

################################################################################
""" Draw a box with text in
"""
################################################################################

import os
import sys
import argparse
import thingy.colour as colour

################################################################################

def main():
    """The guts"""
    return
################################################################################

def box():
    """Entry point"""

    try:
        main()
    except KeyboardInterrupt:
        sys.exit(1)
    except BrokenPipeError:
        sys.exit(2)

################################################################################

if __name__ == '__main__':
    box()
