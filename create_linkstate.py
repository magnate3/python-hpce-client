#!/usr/bin/env python
# -*- coding:utf-8 -*-

import re
import subprocess
import json
import yaml

ADJACENCYSID = 51001

def get_ls(interface):
    '''get linkstate from FRRouting LSDB'''

    cmd = 'sudo vtysh -c "show ip ospf mpls-te interface ' + interface + '"'
    mpls_te = subprocess.check_output(cmd, shell=True)


    cmd = 'sudo vtysh -c "show ip ospf database segment-routing json"'
    sr_db = subprocess.check_output(cmd, shell=True)

    return (mpls_te, sr_db)


def create_ls(interface):
    '''encode raw linkstate to list'''

    mpls_te, sr_db = get_ls(interface)

    decode_mpls_te = mpls_te.decode('utf-8')
    decode_sr_db = json.loads(sr_db.decode('utf-8'))

    dict_mpls_te = {}

    s1 = re.sub(' \(.*?\)', '', decode_mpls_te)
    s2 = re.sub('\(.*?\)', '', s1)
    s3 = s2.replace('  ', '')
    parse_mpls_te = s3.split('\n')

    for i in parse_mpls_te:
        if re.match('#0', i):
            dict_mpls_te[previous] = i.split(': ')[1]
        elif re.match('Maximum Bandwidth', i):
            dict_mpls_te[i.split(': ')[0]] = float(i.split(': ')[1])
        previous = i

    sr_info = 0
    for i in range(len(decode_sr_db['srNodes'])):
        if decode_sr_db['srNodes'][i]['routerID'] == decode_sr_db['srdbID']:
            sr_info = i

    linkstate = [{'Opaque-Type': 1, 'Advertising Router': decode_sr_db['srdbID'], 'Local Interface IP Addresses': [{0: dict_mpls_te['Local Interface IP Address: 1']}], 'Maximum Reservable Bandwidth': dict_mpls_te['Maximum Bandwidth']}]
    linkstate.append({'Opaque-Type': 4, 'Advertising Router': decode_sr_db['srdbID'], 'Segment Routing Range TLV': [None, {'SID Label': decode_sr_db['srNodes'][i]['srgbLabel']}]})
    linkstate.append({'Opaque-Type': 7, 'Advertising Router': decode_sr_db['srdbID'], 'Prefix SID Sub-TLV': [None, None, None, None, {'Index': decode_sr_db['srNodes'][i]['extendedPrefix'][0]['sid']}]})
    linkstate.append({'Opaque-Type': 8, 'Advertising Router': decode_sr_db['srdbID'], 'Adj-SID Sub-TLV': [None, None, None, None, {'Label': ADJACENCYSID}]})

    return linkstate
