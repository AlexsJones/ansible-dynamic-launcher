#ansible-dynamic-launcher

For those times you don't have fixed host lists

This is a work in progress, I'll add features as needed

###Example

```
python ansible-dynamic-launcher/executor.py --range 192.168.1-20 --module shell --args 'ls -la' --workingdir .
```

Or run a playbook

```
python ansibl-dynamic-launcher/executor.py --name 'boot.yml' --range 10.0.0.1-40 --workingdir --args "role=clean_disk".
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
│   ├── goldmaster_key
│   └── goldmaster_key.pub
├── launcher.retry
├── launcher.yml
├── README.md
├── requirements.txt
└── roles
    └── clean_disk
        ├── defaults
        │   └── main.yml
        ├── files
        │   └── disk_space.py
        ├── handlers
        │   └── main.yml
        ├── meta
        │   └── main.yml
        ├── README.md
        ├── tasks
        │   └── main.yml
        ├── templates
        ├── tests
        │   ├── inventory
        │   └── test.yml
        └── vars
            └── main.yml
```

####Assumptions
Assumes your ansible.cfg is in the working directory


####Requirements
- nmap installed on system
- virtualenv for packages

###Configuration 

ansible.cfg

```
scan_args='-sP'  #nmap arguments
syntax=False
private_key_file= #required for passwordless SSH
```
