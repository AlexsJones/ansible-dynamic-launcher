![ansible](https://i.imgur.com/p1o5UUY.png)
#ansible-dynamic-launcher
When you want to run roles on a dynamic range of hosts, use this - it passes through commands and hooks into ansible.cfg

Simply download this as a submodule and run it (Might need to check deps).

*The -w needs to be specified to a path with a valid ansible.cfg*

Example using showterm: http://showterm.io/a92ed411995b74f9b5fae#fast

###Download options

- clone this repo as a submodule
- `build_packages.sh` and install with `dpkg`
- `wget -O ansible-dynamic-launcher.py https://raw.githubusercontent.com/AlexsJones/ansible-dynamic-launcher/master/executor.py`
- `curl -o ansible-dynamic-launcher.py https://raw.githubusercontent.com/AlexsJones/ansible-dynamic-launcher/master/executor.py`

###Example

```
python executor.py --range 192.168.1-20 --module shell --args 'ls -la' --workingdir ../
```

Or run a playbook

```
python executor.py --name 'boot.yml' --range 10.0.0.1-40 --workingdir ../ --args "role=clean_disk"
```

####Note you can make far more complex range scans by just editing the nmap args in the config.


An example directory structure in a project using this as a submodule

```
├── ansible.cfg
├── ansible-dynamic-launcher
│   ├── executor.py
│   ├── lib
│   │   ├── callbacks.py
│   │   └── __init__.py
│   ├── README.md
│   └── requirements.txt
├── keys
│   ├── goldmaster_key
│   └── goldmaster_key.pub
├── launcher.yml
├── README.md
├── requirements.txt
└── roles
    └── clean_disk

```

####Requirements
- openssl-dev installed
- nmap installed on system

Or use `source env/bin/activate && pip install -r requirements`

###Configuration 

```
Usage: executor.py [options]

Options:
  -h, --help            show this help message and exit
  -m MODULE, --module=MODULE
                        Name of ansible module to run
  -a ARGS, --args=ARGS  Argument of module running
  -r RANGE, --range=RANGE
                        an nmap friendly host range to scan e.g. 127.0.0.1-100
  -n NAME, --name=NAME  name of the playbook to run e.g. boot.yml
  -w WORKINGDIR, --workingdir=WORKINGDIR
                        working dir with ansible.cfg in the root
```
As long as the --workingdir points to your ansible.cfg directory and --name is the name (not path) of your playbook yml in that file, you're ready to go...

And add this to your ansible.cfg

```
scan_args='-sP'  #nmap arguments
syntax=False
private_key_file= #required for passwordless SSH
```
