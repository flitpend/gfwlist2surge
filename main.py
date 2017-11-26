#!/usr/bin/env python3

import base64
import urllib.request
from urllib.parse import urlparse

__all__ = ['main']

gfwlist_url = \
    'https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt'


def decode_gfwlist(raw):
    '''Decode raw GFWList using base64'''
    return base64.b64decode(raw)


def get_hostname(url):
    '''Get hostname'''
    if not url.startswith('http:'):
        url = 'http://' + url
    u = urlparse(url)
    return u.hostname


def add_domain(s, url):
    '''Add a hostname to a set'''
    hostname = get_hostname(url)
    if hostname is not None:
        if hostname.startswith('.'):
            hostname = hostname.lstrip('.')
        if hostname.endswith('/'):
            hostname = hostname.rstrip('/')
        s.add(hostname)


def parse_gfwlist(content):
    '''Parse GFWList line by line'''
    gfwList = content.splitlines()
    domainSet = set()

    for item in gfwList:
        i = bytes.decode(item)

        if i.find('.*') >= 0:
            continue
        elif i.find('*') >= 0:
            i = i.replace('*', '/')

        if i.startswith('!'):  # comments
            continue
        elif i.startswith('@'):  # whitelists
            continue
        elif i.startswith('||'):
            add_domain(domainSet, i.lstrip('||'))
        elif i.startswith('|'):
            add_domain(domainSet, i.lstrip('|'))
        elif i.startswith('.'):
            add_domain(domainSet, i.lstrip('.'))
        else:
            add_domain(domainSet, i)

    return domainSet


def sanitise_domainSet(domainSet):
    '''Sanitise domain set'''
    with open('tld.txt', 'r') as f:
        tldSet = set(f.read().splitlines())

    sanitisedSet = set()
    for item in domainSet:
        domain_parts = item.split('.')
        last_root_domain = None
        for i in range(0, len(domain_parts)):
            root_domain = '.'.join(domain_parts[len(domain_parts) - i - 1:])
            if i == 0:
                if not tldSet.__contains__(root_domain):
                    break
            last_root_domain = root_domain
            if tldSet.__contains__(root_domain):
                continue
            else:
                break
        if last_root_domain is not None:
            sanitisedSet.add(last_root_domain)
    return sanitisedSet


def main():
    print('Downloading GFWList from:\n    %s' % gfwlist_url)
    raw = urllib.request.urlopen(gfwlist_url, timeout=10).read()
    decoded = decode_gfwlist(raw)
    parsedSet = parse_gfwlist(decoded)
    sanitisedSet = sanitise_domainSet(parsedSet)
    sortedList = sorted(list(sanitisedSet))
    with open('gfwlist.conf', 'w') as f:
        for item in sortedList:
            f.write('DOMAIN-SUFFIX,' + item + ',Proxy\n')


if __name__ == '__main__':
    main()
