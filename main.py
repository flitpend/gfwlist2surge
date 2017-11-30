#!/usr/bin/env python3

import base64
import urllib.request
from argparse import ArgumentParser


__all__ = ['main']


GFWLIST_URL = \
    'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'


def parse_args():
    '''Optional args for input and output files'''
    parser = ArgumentParser()
    parser.add_argument('-i', '--input', required=False, dest='input',\
        help='Optional argument for local GFWList file', metavar='GFWLIST')
    parser.add_argument('-o', '--output', required=False, dest='output', default='gfwlist.conf',\
        help='Optional argument for output file name, default is gfwlist.conf', metavar='SURGE_CONF')
    return parser.parse_args()


def decode_gfwlist(raw):
    '''Return decoded GFWList using base64'''
    try:
        return base64.b64decode(raw)
    except:
        return raw


def parse_gfwlist(content):
    '''Parse GFWList line by line'''
    gfw_list = content.splitlines()
    parsed_list = []

    for item in gfw_list:
        i = bytes.decode(item)

        # Preprocess
        if i.find('.*') >= 0:
            continue
        if i.find('*') >= 0:
            i = i.replace('*', '')
        if i.find('https://') >= 0:
            i = i.replace('https://', '')
        if i.find('http://') >= 0:
            i = i.replace('http://', '')
        if i.find('/') >= 0:
            i = i[:i.index('/')]

        # Parse
        if i.startswith('!') or i.startswith('[') or i.startswith('@'): # comments and whitelists
            continue
        elif i.startswith('||'):
            parsed_list.append(i.lstrip('||'))
        elif i.startswith('|'):
            parsed_list.append(i.lstrip('|'))
        elif i.startswith('.'):
            parsed_list.append(i.lstrip('.'))
        else:
            parsed_list.append(i)

    return parsed_list


def sanitise_gfwlist(content):
    '''Sanitise and sort GFWList'''
    sanitised_list = []
    for item in content:
        if item not in sanitised_list:
            sanitised_list.append(item)

    return sorted(sanitised_list)


def main():
    args = parse_args()
    if args.input:
        with open(args.input, 'r') as fh_read:
            gfwlist_raw = fh_read.read()
    else:
        print('Downloading GFWList from:\n    %s' % GFWLIST_URL)
        gfwlist_raw = urllib.request.urlopen(GFWLIST_URL, timeout=10).read()

    decoded_list = decode_gfwlist(gfwlist_raw)
    parsed_list = parse_gfwlist(decoded_list)
    sanitised_list = sanitise_gfwlist(parsed_list)

    with open(args.output, 'w') as fh_write:
        for line in sanitised_list:
            fh_write.write('DOMAIN-SUFFIX,' + line + ',Proxy\n')


if __name__ == '__main__':
    main()
