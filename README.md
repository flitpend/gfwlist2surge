# gfwlist2surge
A simple tool to convert GFWList into surge config expressions.

```
python3 main.py [-i GFWLIST] [-o SURGE_CONF]
    -h, --help          Show this help message and exit
    -i GFWLIST, --input GFWLIST
                        Optional argument for local GFWList file
    -o CONF, --output CONF
                        Optional argument for output file name, default is gfwlist.conf
```

Generates surge.conf with sorted domain list in the following format:

```
DOMAIN-SUFFIX,<domain0>
DOMAIN-SUFFIX,<domain1>
DOMAIN-SUFFIX,<domain2>
DOMAIN-SUFFIX,<domain3>
```

You may create a RULE-SET in Surge config file to quickly add these domains to your rules:

```
RULE-SET,https://raw.githubusercontent.com/flitpend/gfwlist2surge/master/surge.conf,<your_proxy>
```
