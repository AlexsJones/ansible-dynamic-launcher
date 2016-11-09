#ansible-dynamic-launcher

For those times you don't have fixed host lists

This is a work in progress, I'll add features as needed

###Example

```
pushd ansible-dynamic-launcher
python executor.py --range 192.168.1-20 --module shell --args 'ls -la'
popd
```

Or run a playbook

```
pushd ansible-dynamic-launcher
python executor.py --name 'boot.yml' --range 10.0.0.1-40 --path ../launcher.yml
popd
```

An example directory structure

```
├── ansible.cfg
├── ansible-dynamic-launcher
│   ├── boot.cfg
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


####Settings

boot.cfg needs a few settings (namely the ssh settings ansible would have in the .cfg)
