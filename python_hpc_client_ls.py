#!/usr/bin/env python
# -*- coding:utf-8 -*-

import time
import create_linkstate
import linkstate_sockcli


def main():
    '''Send Inter-domain Linkstate to PCE'''
    interface = 'ens5'

    while True:
        linkstate = create_linkstate.create_ls(interface)
        linkstate_sockcli.lsocket(linkstate)
        time.sleep(1)

    return 0


if __name__ == '__main__':
    main()
