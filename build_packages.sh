#! /bin/bash
#################################################################################
#     File Name           :     build_packages.sh
#     Created By          :     jonesax
#     Creation Date       :     [2016-11-21 10:18]
#     Last Modified       :     [2016-11-21 10:20]
#     Description         :      
#################################################################################
mkdir -p debian-package/usr/bin
cp executor.py debian-package/usr/bin/ansible-dynamic-launcher.py 
cp lib/callbacks.py debian-package/usr/bin/callbacks.py
dpkg -b debian-package
