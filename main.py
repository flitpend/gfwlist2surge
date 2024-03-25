#!/usr/bin/env python3

import base64
import re
import urllib.request
from pathlib import Path
from argparse import ArgumentParser

__all__ = ['main']


GFWLIST_URL = \
    'https://gitlab.com/gfwlist/gfwlist/raw/master/gfwlist.txt'


# GFWLIST_URL = \
#     'https://raw.githubusercontent.com/gfwlist/tinylist/master/tinylist.txt'


TLDLIST_URL = \
    'https://data.iana.org/TLD/tlds-alpha-by-domain.txt'


def parse_args():
    parser = ArgumentParser()
    parser.add_argument(
        '-c',
        '--custom',
        required=False,
        dest='custom',
        help='Optional argument for local custom domain list',
        metavar='CUSTOM.CONF')
    parser.add_argument(
        '-i',
        '--input',
        required=False,
        dest='input',
        help='Optional argument for local GFWList file (base64 encoded)',
        metavar='GFWLIST')
    parser.add_argument(
        '-o',
        '--output',
        required=False,
        dest='output',
        default='surge.conf',
        help='Optional argument for Surge config output, default is surge.conf',
        metavar='SURGE.CONF')
    parser.add_argument(
        '-t',
        '--tld',
        required=False,
        dest='tld',
        help='Optional argument for updating top domain list',
        action='store_true')
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
        if i.find('*.') >= 0:
            i = re.sub(r'^.+\*\.', '', i)
        if i.find('*') >= 0:
            i = i.replace('*', '')
        if i.find('https://') >= 0:
            i = i.replace('https://', '')
        if i.find('http://') >= 0:
            i = i.replace('http://', '')
        if i.find('/') >= 0:
            i = i[:i.index('/')]

        # Parse
        if i.startswith('!') or i.startswith('[') or i.startswith('@'):
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
    with open('tld.txt', 'r') as fh:
        tld_list = fh.read().lower().splitlines()

    sanitised_list = []
    for item in content:
        domain_suffix = item.split('.')[-1]
        if (domain_suffix in tld_list) and (item not in sanitised_list):
            sanitised_list.append(item)

    return sorted(sanitised_list)


def add_custom(content, custom):
    '''Add custom rules'''
    with open(custom, 'r') as fh:
        custom_list = fh.read().splitlines()

    for item in custom_list:
        if item in content:
            custom_list.remove(item)
            print('Removed duplicate domain in custom rule: %s' % item)

    complete_list = content + custom_list
    return sorted(complete_list)


def update_tld(content):
    '''Remove comments from TLD list'''
    tld_byte_list = content.splitlines()
    tld_list = []
    for item in tld_byte_list:
        i = bytes.decode(item)
        if not (i.startswith('#') or '-' in i):
            tld_list.append(i)

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

    if args.input:
        with open(args.input, 'r') as fh:
            gfwlist_raw = fh.read()
    else:
        print('Downloading gfwlist from:\n    %s' % GFWLIST_URL)
        gfwlist_raw = urllib.request.urlopen(GFWLIST_URL, timeout=10).read()

    decoded_list = decode_gfwlist(gfwlist_raw)
    parsed_list = parse_gfwlist(decoded_list)
    sanitised_list = sanitise_gfwlist(parsed_list)

    if args.custom:
        prefinal_list = add_custom(sanitised_list, args.custom)
    else:
        prefinal_list = sanitised_list

    '''Process domains that starts with .www.'''
    final_list = []
    for item in prefinal_list:
        item = re.sub('^www\.', '', item)
        final_list.append(item)

    with open(args.output, 'w') as fh:
        for line in final_list:
            fh.write('.' + line + '\n')


if __name__ == '__main__':
    main()
