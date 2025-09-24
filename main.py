#!/usr/bin/env python3

import base64
import logging
import urllib.request
from pathlib import Path
from argparse import ArgumentParser

# Logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

__all__ = ['main']

GFWLIST_URL = 'https://raw.githubusercontent.com/gfwlist/gfwlist/refs/heads/master/gfwlist.txt'
# GFWLIST_URL = 'https://gitlab.com/gfwlist/gfwlist/raw/master/gfwlist.txt'
# GFWLIST_URL = 'https://bitbucket.org/gfwlist/gfwlist/raw/HEAD/gfwlist.txt'
# GFWLIST_URL = 'https://pagure.io/gfwlist/raw/master/f/gfwlist.txt'

TLDLIST_URL = 'https://data.iana.org/TLD/tlds-alpha-by-domain.txt'


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
        logging.warning("Failed to decode GFWList using base64, using raw content.")
        return raw.splitlines()


def parse_gfwlist(content):
    '''Parse GFWList line by line'''
    parsed_list = []

    for item in content:
        # Skip comments and disabled domains
        if item.find('.*') >= 0 or item.startswith('!') or item.startswith('[') or item.startswith('@'):
            continue

        item = item.replace('https://', '').replace('http://', '').replace('*', '').replace('www.', '', 1).replace('|', '').lstrip('.')

        if item.find('/') >= 0:
            item = item[:item.index('/')]

        parsed_list.append(item)

    return parsed_list


def sanitise_gfwlist(content):
    '''Sanitise and sort GFWList'''
    try:
        with open('tld.txt', 'r') as fh:
            tld_list = fh.read().lower().splitlines()
    except FileNotFoundError:
        logging.error("tld.txt file not found.")
        return []
    sanitised_list = []
    for item in content:
        domain_suffix = item.split('.')[-1]
        if (domain_suffix in tld_list) and (item not in sanitised_list):
            sanitised_list.append(item)
    return sanitised_list


def add_custom(content, custom):
    '''Add custom rules'''
    try:
        with open(custom, 'r') as fh:
            custom_list = fh.read().splitlines()
    except FileNotFoundError:
        logging.error(f"Custom rule file {custom} not found.")
        return content
    for item in custom_list:
        if item in content:
            custom_list.remove(item)
            logging.info(f"Ignored duplicate domain in custom rule: {item}")
    complete_list = content + custom_list
    return complete_list


def download_file(url):
    '''Download files'''
    try:
        response = urllib.request.urlopen(url, timeout=10)
        return response.read()
    except urllib.error.URLError as e:
        logging.error(f"Failed to download file from {url}: {e}")
        return None


def update_tld(content):
    '''Remove comments and XN--* domains from TLD list'''
    if content is None:
        return
    tld_list = content.decode('utf-8').splitlines()
    tld_list.pop(0)
    for item in reversed(tld_list):
        if item.startswith('XN--'):
            tld_list.remove(item)
    try:
        with open('tld.txt', 'w') as fh:
            for line in tld_list:
                fh.write(line + '\n')
    except IOError as e:
        logging.error(f"Failed to write to tld.txt: {e}")


def main():
    args = parse_args()
    local_tld = Path('./tld.txt')

    if args.tld or (not local_tld.exists()):
        logging.info(f"Downloading TLD list from: {TLDLIST_URL}")
        tldlist_raw = download_file(TLDLIST_URL)
        update_tld(tldlist_raw)

    if not args.tld:
        if args.input:
            try:
                with open(args.input, 'r') as fh:
                    gfwlist_raw = fh.read()
            except FileNotFoundError:
                logging.error(f"Input file {args.input} not found.")
                return
        else:
            logging.info(f"Downloading gfwlist from: {GFWLIST_URL}")
            gfwlist_raw = download_file(GFWLIST_URL)
            if gfwlist_raw is None:
                return

        final_list = sanitise_gfwlist(parse_gfwlist(decode_gfwlist(gfwlist_raw)))

        if args.custom:
            final_list = add_custom(final_list, args.custom)

        try:
            with open(args.output, 'w') as fh:
                for line in sorted(final_list):
                    fh.write('.' + line + '\n')
        except IOError as e:
            logging.error(f"Failed to write to output file {args.output}: {e}")


if __name__ == '__main__':
    main()
