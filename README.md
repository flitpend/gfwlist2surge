# gfwlist2surge
A simple tool to convert GFWList into surge config expressions.

```
python3 main.py [-h] [-i GFWLIST] [-o SURGE_CONF]
    -h, --help          show this help message and exit
    -i GFWLIST, --input GFWLIST
                        Optional argument for local GFWList file
    -o CONF, --output CONF
                        Optional argument for output file name, default is gfwlist.conf
```

Generates gfwlist.conf with sorted domain list in the following format:

```
DOMAIN-SUFFIX,<domain0>,Proxy
DOMAIN-SUFFIX,<domain1>,Proxy
DOMAIN-SUFFIX,<domain2>,Proxy
DOMAIN-SUFFIX,<domain3>,Proxy
```
