# GFWList Surge and Clash config converter
Automatically combine the latest GFWList or your local copy with your own custom.conf (if provided) as input files, and generate surge.conf or clash.txt as output file.

```
Usage: main.py [-h] [-c CUSTOM.CONF] [-cl] [-i GFWLIST] [-o FILENAME] [-p] [-t]

  -h, --help            show this help message and exit
  -c, --custom CUSTOM.CONF
                        optional argument for local custom domain list
  -cl, --clash          optional argument for clash payload output, default is clash.txt
  -i, --input GFWLIST   optional argument for local GFWList file (base64 encoded)
  -o, --output FILENAME
                        optional argument for output file name, default is surge.conf, or clash.txt if -cl is used
  -p, --plain           optional argument for using plain text GFWList over base64 encoded list
  -t, --tld             optional argument for updating top domain list
```

## Client configuration

You may add a one liner in Surge config file to quickly add these domains to your rules:

```
DOMAIN-SET,https://raw.githubusercontent.com/flitpend/gfwlist2surge/master/surge.conf,<your_proxy>
```

Alternatively, if you use Clash, add the following lines to your profile:
```
rule-providers:
  gfwlist:
    type: http
    url: "https://raw.githubusercontent.com/flitpend/gfwlist2surge/master/clash.txt"
    interval: 604800
    proxy: <your_proxy>
    behavior: domain
    size-limit: 0

rules:
  - RULE-SET,gfwlist,<your_proxy>
```

<br>
<br>

## Usage examples

Example 1: fetch GFWList and convert to surge.conf
```sh
python3 main.py 
```

<br>
<br>

Example 2: merge GFWList and your custom domain list, then convert to surge.conf
```sh
python3 main.py -c custom.conf
```

<br>
<br>

Example 3: merge GFWList and your custom domain list, then convert to clash.txt
```sh
python3 main.py -c custom.conf -cl
```

<br>
<br>

Example 4: merge local GFWList (plain text, not base64 encoded) and your custom domain list, then convert to yourfilename.conf for Surge
```sh
python3 main.py -p -i list.txt -c custom.conf -o yourfilename.conf
```

<br>
<br>

Example 5: merge local GFWList (base64 encoded) and your custom domain list, then convert to yourfilename.txt for Clash
```sh
python3 main.py -i list.txt -c custom.conf -o yourfilename.txt -cl
```

<br>
<br>

Example 6: update tld.txt (top level domain)
```sh
python3 main.py -t
```