#ansible-dynamic-launcher

For those times you don't have fixed host lists

This is a work in progress, I'll add features as needed

###Example

```
python executor.py --range 192.168.1-20 --module shell --args 'ls -la'
```

Or run a playbook

- make sure the executor.py is in the same directory as the playbook you want to run (e.g. the project root)
- make sure the ansible.cfg has your roles relative path as normal

```
python executor.py --name 'boot.yml' --range 10.0.0.1-40
```

An example directory structure

```
roles/
projects/
launcher.yml
executor.py
ansible.cfg
boot.cfg

```

The executor.py needs to be in the same directory as ansible.cfg and boot.cfg as it reads some of both

####Settings

You'll see a couple of the settings in boot.cfg are the same as the ones needed in ansible.cfg; this is purely as parsing the ansible cfg from python was a pain; hopefully they are few and not too tedious.


