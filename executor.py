#!/usr/bin/env python
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
import os
import sys
import jinja2
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.plugins.callback import CallbackBase
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor
from tempfile import NamedTemporaryFile
from optparse import OptionParser
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.playbook.play import Play
import nmap
import configobj
import re 
import json
from colorama import init
init(strip=not sys.stdout.isatty()) # strip colors if stdout is redirected
from termcolor import cprint 
from pyfiglet import figlet_format
from ansible.plugins.callback import CallbackBase
from ansible import constants as C


class CallbackModule(CallbackBase):

    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'oneline'

    def _command_generic_msg(self, hostname, result,  caption):
        stdout = result.get('stdout','').replace('\n', '\\n')
        if 'stderr' in result and result['stderr']:
            stderr = result.get('stderr','').replace('\n', '\\n')
            return "%s | %s | rc=%s | (stdout) %s (stderr) %s" % (hostname, caption, result.get('rc', -1), stdout, stderr)
        else:
            return "%s | %s | rc=%s | (stdout) %s" % (hostname, caption, result.get('rc', -1), stdout)

    def v2_runner_on_failed(self, result, ignore_errors=False):
        if 'exception' in result._result:
            if self._display.verbosity < 3:
                # extract just the actual error message from the exception text
                error = result._result['exception'].strip().split('\n')[-1]
                msg = "An exception occurred during task execution. To see the full traceback, use -vvv. The error was: %s" % error
            else:
                msg = "An exception occurred during task execution. The full traceback is:\n" + result._result['exception'].replace('\n','')

            if result._task.action in C.MODULE_NO_JSON and 'module_stderr' not in result._result:
                self._display.display(self._command_generic_msg(result._host.get_name(), result._result,'FAILED'), color=C.COLOR_ERROR)
            else:
                self._display.display(msg, color=C.COLOR_ERROR)

        self._display.display("%s | FAILED! => %s" % (result._host.get_name(), self._dump_results(result._result, indent=0).replace('\n','')), color=C.COLOR_ERROR)

    def v2_runner_on_ok(self, result):
        if result._task.action in C.MODULE_NO_JSON:
            self._display.display(self._command_generic_msg(result._host.get_name(), result._result,'SUCCESS'), color=C.COLOR_OK)
        else:
            self._display.display("%s | SUCCESS => %s" % (result._host.get_name(), self._dump_results(result._result, indent=0).replace('\n','')), color=C.COLOR_OK)


    def v2_runner_on_unreachable(self, result):
        self._display.display("%s | UNREACHABLE!: %s" % (result._host.get_name(), result._result.get('msg','')), color=C.COLOR_UNREACHABLE)

    def v2_runner_on_skipped(self, result):
        self._display.display("%s | SKIPPED" % (result._host.get_name()), color=C.COLOR_SKIP)
    
class Boot(object):

    options = namedtuple('Options', ['listtags', 
        'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks', 
        'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 
        'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 
        'become_user', 'verbosity', 'check','remote_tmp'])

    def __init__(self,working_dir):
        self.results_callback = CallbackModule()
        self.variable_manager = VariableManager()
        self.loader = DataLoader()
        self.nm = nmap.PortScanner()
        self.hosts = []
        self.inventory = """
                    [local]
                    127.0.0.1
                    [local:vars]
                    ansible_connection=local
                    [DYNAMIC]
                    {{ host_list }}
                    """
    
        os.chdir(working_dir)
        self.con = configobj.ConfigObj('ansible.cfg')

    def scan(self,range):
        self.nm.scan(range,arguments=self.con['defaults']['scan_args'])
        self.hosts = self.nm.all_hosts()
        if not self.hosts:
            print("No hosts found")
            sys.exit(1)

        inventory_template = jinja2.Template(self.inventory)
        rendered_inventory = inventory_template.render({
            'host_list': "\n".join(self.hosts),
            })

        hosts = NamedTemporaryFile(delete=False)
        hosts.write(rendered_inventory)
        hosts.close()
        self.inventory = Inventory(loader=self.loader, 
                variable_manager=self.variable_manager,  
                host_list=hosts.name)

        #There are many more options that could be added here
        self.options = Boot.options(listtags=False, listtasks=False, listhosts=False, 
                syntax=self.con.get('defaults').as_bool('syntax'), 
                connection='smart', module_path=None, forks=100, 
                remote_user=self.con['defaults']['remote_user'],
                private_key_file=self.con['defaults']['private_key_file'],
                ssh_common_args=None, 
                ssh_extra_args=None, sftp_extra_args=None, 
                scp_extra_args=None, 
                become=True, become_method=None, 
                become_user=self.con['defaults']
                ['become_user'], 
                verbosity=3, 
                check=False,
                remote_tmp=self.con['defaults']['remote_tmp'])

        self.passwords = {}

    def execute_module(self,module_name, module_args):
        play_source = dict(
                name = "Ansible play",
                hosts = "DYNAMIC",
                gather_facts = "no",
                tasks = [
                    dict(action=dict(module=module_name, args=module_args),
                        register="shell_out")
                        ]
                )
        play = Play().load(play_source, variable_manager=self.variable_manager,
                loader=self.loader)
        tqm = None
        try:
            tqm = TaskQueueManager(
                    inventory = self.inventory,
                    variable_manager = self.variable_manager,
                    loader = self.loader,
                    options = self.options,
                    passwords = self.passwords,
                    stdout_callback=self.results_callback)
            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()

    def execute_boot(self,playbook_path,args):        
        playbook_path = playbook_path
        if not os.path.exists(playbook_path):
            print('The playbook does not exist')
            sys.exit(1)
        
        default_vars = {'hosts': 'DYNAMIC'} 
        
        if args:
            regex = re.compile(r"\b(\w+)\s*=\s*([^=]*)(?=\s+\w+\s*:|$)")
            d = dict(regex.findall(args))
            print("Passing through extra vars: " + str(d))
            default_vars.update(d)
            
        self.variable_manager.extra_vars = default_vars 

        pbex = PlaybookExecutor(playbooks=[playbook_path], 
                inventory=self.inventory, 
                variable_manager=self.variable_manager, 
                loader=self.loader, options=self.options, passwords=self.passwords)
        pbex._tqm._stdout_callback = self.results_callback
        results = pbex.run()

if __name__ == "__main__":

    cprint(figlet_format('Ansible Dynamic Launcher', font='big'),
                   'red', attrs=['bold'])
    parser = OptionParser()
    parser.add_option("-m","--module",
            help="Name of ansible module to run")
    parser.add_option("-a","--args",
            help ="Argument of module running")
    parser.add_option("-r","--range",
            help ="an nmap friendly host range to scan e.g. 127.0.0.1-100")
    parser.add_option("-n","--name",
            help="name of the playbook to run e.g. boot.yml")

    parser.add_option("-w","--workingdir",
            help="working dir with ansible.cfg in the root")
    (options,args) = parser.parse_args()

    if not options.workingdir:
        print("Requires working directory set")
        sys.exit(1)

    b = Boot(options.workingdir)

    if options.range:
        b.scan(options.range)
    else:
        print("Requires --range of hosts in nmap format e.g. 10.0.0.1-100")
        sys.exit(1)
    if options.module:
        b.execute_module(options.module, options.args)
    else:
        if options.name: 
            b.execute_boot(options.name,options.args)
        else:
            print("Cannot run without a playbook")
            sys.exit(1)
