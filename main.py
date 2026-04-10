#!/usr/bin/env python3

import base64
import logging
import re
import urllib.request
from argparse import ArgumentParser
from pathlib import Path
from typing import List, Optional

# Logging format
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

GFWLIST_URL = 'https://raw.githubusercontent.com/gfwlist/gfwlist/refs/heads/master/gfwlist.txt'
# GFWLIST_URL = 'http://repo.or.cz/gfwlist.git/blob_plain/HEAD:/gfwlist.txt'
# GFWLIST_URL = 'https://raw.githubusercontent.com/gfwlist/tinylist/refs/heads/master/tinylist.txt'
GFWLIST_PLAIN = 'https://raw.githubusercontent.com/gfwlist/gfwlist/refs/heads/master/list.txt'
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
        '-p', '--plain',
        required=False,
        dest='plain',
        help='optional argument for using plain text GFWList over base64 encoded list',
        action='store_true')
    parser.add_argument(
        '-t', '--tld',
        required=False,
        dest='tld',
        help='optional argument for updating top domain list',
        action='store_true')
    return parser.parse_args()


def clean_domain(domain: str) -> Optional[str]:
    '''Helper function to clean domain strings'''
    domain = re.sub(r"^[!@[].*", "", domain)    # Comments and disabled domains
    domain = domain.replace('|', '')            # Legit domains
    domain = domain.replace('https://', '')     # Headers
    domain = domain.replace('http://', '')      # Headers
    domain = domain.replace('www.', '', 1)      # Headers
    domain = re.sub(r"^.*\*\d*\.", "", domain)  # *. subdomains
    domain = re.sub(r"/.*$", "", domain)        # Anything after the 1st path separator
    domain = domain.lstrip('.')
    domain = domain.strip()
    return domain


def parse_gfwlist(content: List[str]) -> List[str]:
    '''Parse GFWList line by line'''
    parsed_list = []

    for domain in content:
        domain = clean_domain(domain)
        if domain:
            parsed_list.append(domain)

    return parsed_list


def sanitize_gfwlist(content: List[str]) -> List[str]:
    '''Filter and sort GFWList, remove duplicates'''
    try:
        with open('tld.txt', 'r') as fh:
            tld_list = fh.read().lower().splitlines()
    except FileNotFoundError:
        logging.error("tld.txt file not found.")
        return []

    sanitized_list = []
    seen = set()

    for domain in content:
        domain_suffix = domain.rsplit('.', 1)[-1]
        if (domain_suffix in tld_list) and (domain not in seen):
            sanitized_list.append(domain)
            seen.add(domain)
    return sanitized_list


def add_custom(content: List[str], custom: str) -> List[str]:
    '''Add custom rules'''
    try:
        with open(custom, 'r', encoding='utf-8') as fh:
            custom_list = fh.read().splitlines()
    except FileNotFoundError:
        logging.error(f"Custom rule file {custom} not found.")
        return content
    filtered_custom_list = []
    domain_set = set(content)
    for domain in custom_list:
        if domain in domain_set:
            logging.info(f"Ignored duplicate domain in custom rule: {domain}")
        else:
            filtered_custom_list.append(domain)
    complete_list = content + filtered_custom_list
    return complete_list


def download_file(url: str) -> Optional[bytes]:
    '''Download files'''
    try:
        response = urllib.request.urlopen(url, timeout=10)
        return response.read()
    except urllib.error.URLError as e:
        logging.error(f"Failed to download file from {url}: {e}")
        return None


def update_tld(content: Optional[bytes]) -> None:
    '''Remove comments and XN--* domains from TLD list'''
    if content is None:
        return
    tld_list = content.decode('utf-8').splitlines()
    tld_list.pop(0)
    tld_list = [domain for domain in tld_list if not domain.startswith('XN--')]
    try:
        with open('tld.txt', 'w') as fh:
            for line in tld_list:
                fh.write(line + '\n')
    except IOError as e:
        logging.error(f"Failed to write to tld.txt: {e}")


def main() -> None:
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
                    if args.plain:
                        gfwlist_raw = fh.read()
                    else:
                        gfwlist_raw = base64.b64decode(fh.read()).decode('utf-8')
            except FileNotFoundError:
                logging.error(f"Input file {args.input} not found.")
                return

        else:
            if args.plain:
                logging.info(f"Downloading plain text gfwlist from: {GFWLIST_PLAIN}")
                gfwlist_raw = download_file(GFWLIST_PLAIN).decode('utf-8')
                if gfwlist_raw is None:
                    return
            else:
                logging.info(f"Downloading base64 encoded gfwlist from: {GFWLIST_URL}")
                gfwlist_raw = base64.b64decode(download_file(GFWLIST_URL)).decode('utf-8')
                if gfwlist_raw is None:
                    return

        final_list = sanitize_gfwlist(parse_gfwlist(gfwlist_raw.splitlines()))

        if args.custom:
            final_list = add_custom(final_list, args.custom)

        try:
            with open(args.output, 'w') as fh:
                for line in sorted(final_list):
                    fh.write('.' + line + '\n')
            logging.info(f"Generated {len(final_list)} domains in {args.output}")
        except IOError as e:
            logging.error(f"Failed to write to output file {args.output}: {e}")


if __name__ == '__main__':
    main()
