# GFWList Surge and Clash config converter
This simple python script does the following:
* Automatically download the latest GFWList, or use your local copy as input
* Combine with your own custom domain list (if provided)
* Generate surge.conf or clash.yaml as output

```
usage: main.py [-h] [-c CUSTOM.CONF] [-cl] [-i GFWLIST] [-o FILENAME] [-p] [-t]

optional arguments:
  -h, --help            show this help message and exit
  -c CUSTOM.CONF, --custom CUSTOM.CONF
                        optional argument for local custom domain list
  -cl, --clash          optional argument for clash payload output, default is clash.yaml
  -i GFWLIST, --input GFWLIST
                        optional argument for local GFWList file (base64 encoded)
  -o FILENAME, --output FILENAME
                        optional argument for output file name, default is surge.conf, or clash.yaml if -cl is used
  -p, --plain           optional argument for using plain text GFWList over base64 encoded list
  -t, --tld             optional argument for updating top domain list
```

## Client configuration

Simply add a one liner in your Surge config file. Replace `<your_proxy>` with your own proxy group:

```
DOMAIN-SET,https://raw.githubusercontent.com/flitpend/gfwlist2surge/master/surge.conf,<your_proxy>
```

Alternatively, if you use Clash, add the following section to your profile:
```yaml
rule-providers:
  gfwlist:
    type: http
    url: "https://raw.githubusercontent.com/flitpend/gfwlist2surge/master/clash.yaml"
    interval: 604800
    proxy: <your_proxy>
    behavior: domain
    size-limit: 0

rules:
  - RULE-SET,gfwlist,<your_proxy>
```

<br/>

## Usage examples

1. Fetch GFWList and convert to surge.conf
```sh
python3 main.py 
```

2. Merge GFWList and your custom domain list, then convert to surge.conf
```sh
python3 main.py -c custom.conf
```

3. Merge GFWList and your custom domain list, then convert to clash.yaml
```sh
python3 main.py -c custom.conf -cl
```

4. Merge local GFWList (in plain text) and your custom domain list, then convert to foo.conf for Surge
```sh
python3 main.py -p -i list.txt -c custom.conf -o foo.conf
```

5. Merge local GFWList (base64 encoded) and your custom domain list, then convert to bar.txt for Clash
```sh
python3 main.py -i list.txt -c custom.conf -o bar.txt -cl
```

6. Update tld.txt (top level domain)
```sh
python3 main.py -t
```
