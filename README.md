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
launcher.yml
ansible.cfg
roles/
projects/
ansible-dynamic-launcher/
  executor.py
  boot.cfg
  < -- run from here --> 
```


####Settings

boot.cfg needs a few settings (namely the ssh settings ansible would have in the .cfg)
