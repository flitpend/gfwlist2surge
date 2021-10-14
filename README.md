# gfwlist2surge
A simple tool to convert GFWList into surge config expressions.

```
python3 main.py [-i GFWLIST] [-o SURGE.CONF]
    optional arguments:
        -h, --help            show this help message and exit
        -c CUSTOM.CONF, --custom CUSTOM.CONF
                              Optional argument for your own custom domain list
        -i GFWLIST, --input GFWLIST
                              Optional argument for local GFWList file (base64 encoded)
        -o SURGE.CONF, --output SURGE.CONF
                              Optional argument for Surge config output file name, default is surge.conf
        -r, --refreshtld      Optional argument for refreshing top domain list
```

Automatically combine GFWList with your custom.conf (if provided), and generate surge.conf with uniquified and sorted domain list in the following format:

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
