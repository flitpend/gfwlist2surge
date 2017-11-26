# gfwlist2surge
A simple tool to convert GFWList into surge config expressions.

Run with `python3 main.py`

Generates gfwlist.conf with sorted domain list in the following format:

```
DOMAIN-SUFFIX,<domain0>,Proxy
DOMAIN-SUFFIX,<domain1>,Proxy
DOMAIN-SUFFIX,<domain2>,Proxy
DOMAIN-SUFFIX,<domain3>,Proxy
```
