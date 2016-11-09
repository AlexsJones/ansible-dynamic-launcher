#ansible-dynamic-launcher

For those times you don't have fixed host lists

This is a work in progress, I'll add features as needed

###Example

```
python executor.py --range 192.168.1-20 --module shell --args 'ls -la'
```

Or run a playbook

(Make sure to set the roles path in the .cfg files)

```
python executor.py --name 'myrole' --range 10.0.0.1-40
```
