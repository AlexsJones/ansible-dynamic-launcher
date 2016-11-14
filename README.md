![ansible](https://i.imgur.com/p1o5UUY.png)
#ansible-dynamic-launcher
When you want to run roles on a dynamic range of hosts, use this - it passes through commands and hooks into ansible.cfg

Simply download this as a submodule and run it (Might need to check deps).

###Example

```
python executor.py --range 192.168.1-20 --module shell --args 'ls -la' --workingdir ../
```

Or run a playbook

```
python executor.py --name 'boot.yml' --range 10.0.0.1-40 --workingdir ../ --args "role=clean_disk"
```

An example directory structure

```
├── ansible-dynamic-launcher
│   ├── executor.py
│   ├── lib
│   │   ├── callbacks.py
│   │   └── __init__.py
│   ├── README.md
│   └── requirements.txt
├── keys
│   ├──my_key
├── launcher.yml
├── README.md
├── requirements.txt
└── roles
    └── clean_disk

```

####Requirements
- nmap installed on system
- virtualenv for packages

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
As long as the --workingdir points to your ansible.cfg directory and --name is the name (not path) of your boot yml in that file, you're ready to go...

And add this to your ansible.cfg

```
scan_args='-sP'  #nmap arguments
syntax=False
private_key_file= #required for passwordless SSH
```
