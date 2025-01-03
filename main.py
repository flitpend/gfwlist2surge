#!/usr/bin/env python3

import base64
import re
import urllib.request
from pathlib import Path
from argparse import ArgumentParser

__all__ = ['main']


GFWLIST_URL = \
    'https://gitlab.com/gfwlist/gfwlist/raw/master/gfwlist.txt'
#    'https://raw.githubusercontent.com/gfwlist/tinylist/master/tinylist.txt'
#    'https://bitbucket.org/gfwlist/gfwlist/raw/HEAD/gfwlist.txt'
#    'https://pagure.io/gfwlist/raw/master/f/gfwlist.txt'


TLDLIST_URL = \
    'https://data.iana.org/TLD/tlds-alpha-by-domain.txt'


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '-c', '--custom',
        required=False,
        dest='custom',
        help='optional argument for local custom domain list',
        metavar='CUSTOM.CONF')
    parser.add_argument(
        '-i', '--input',
        required=False,
        dest='input',
        help='optional argument for local GFWList file (base64 encoded)',
        metavar='GFWLIST')
    parser.add_argument(
        '-o', '--output',
        required=False,
        dest='output',
        default='surge.conf',
        help='optional argument for Surge config output, default is surge.conf',
        metavar='SURGE.CONF')
    parser.add_argument(
        '-t', '--tld',
        required=False,
        dest='tld',
        help='optional argument for updating top domain list',
        action='store_true')
    return parser.parse_args()


def decode_gfwlist(raw):
    '''Return decoded GFWList using base64'''
    try:
        return base64.b64decode(raw).decode('utf-8').splitlines()
    except base64.binascii.Error:
        return raw.splitlines()


def parse_gfwlist(content):
    '''Parse GFWList line by line'''
    parsed_list = []

    for item in content:
        # Preprocess
        if item.find('.*') >= 0:
            continue
        if item.startswith('!') or item.startswith('[') or item.startswith('@'):
            continue

        item = item.replace('https://', '').replace('http://', '').replace('*', '').replace('www.', '', 1).replace('|', '').lstrip('.')

        if item.find('/') >= 0:
            item = item[:item.index('/')]

        # Parse
        parsed_list.append(item)

    return parsed_list


def sanitise_gfwlist(content):
    '''Sanitise and sort GFWList'''
    with open('tld.txt', 'r') as fh:
        tld_list = fh.read().lower().splitlines()

    sanitised_list = []

    for item in content:
        domain_suffix = item.split('.')[-1]
        if (domain_suffix in tld_list) and (item not in sanitised_list):
            sanitised_list.append(item)

    return sanitised_list


def add_custom(content, custom):
    '''Add custom rules'''
    with open(custom, 'r') as fh:
        custom_list = fh.read().splitlines()

    for item in custom_list:
        if item in content:
            custom_list.remove(item)
            print('Ignored duplicate domain in custom rule: %s' % item)

    complete_list = content + custom_list
    return complete_list


def update_tld(content):
    '''Remove comments and XN--* domains from TLD list'''
    tld_list = content.decode('utf-8').splitlines()
    tld_list.pop(0)
    for item in reversed(tld_list):
        if item.startswith('XN--'):
            tld_list.remove(item)

    with open('tld.txt', 'w') as fh:
        for line in tld_list:
            fh.write(line + '\n')


def main():
    args = parse_args()
    local_tld = Path('./tld.txt')

    if args.tld or (not local_tld.exists()):
        print('Downloading TLD list from:\n    %s' % TLDLIST_URL)
        tldlist_raw = urllib.request.urlopen(TLDLIST_URL, timeout=10).read()
        update_tld(tldlist_raw)

    if not args.tld:
        if args.input:
            with open(args.input, 'r') as fh:
                gfwlist_raw = fh.read()
        else:
            print('Downloading gfwlist from:\n    %s' % GFWLIST_URL)
            gfwlist_raw = urllib.request.urlopen(GFWLIST_URL, timeout=10).read()

        final_list = sanitise_gfwlist(parse_gfwlist(decode_gfwlist(gfwlist_raw)))

        if args.custom:
            final_list = add_custom(final_list, args.custom)

        with open(args.output, 'w') as fh:
            for line in sorted(final_list):
                fh.write('.' + line + '\n')


if __name__ == '__main__':
    main()
