import os
import sys
import jinja2
from collections import namedtuple
from ansible.parsing.dataloader import DataLoader
from ansible.vars import VariableManager
from ansible.inventory import Inventory
from ansible.executor.playbook_executor import PlaybookExecutor
from tempfile import NamedTemporaryFile
from optparse import OptionParser
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.playbook.play import Play
import nmap
import yaml


class Boot(object):

    options = namedtuple('Options', ['listtags', 
        'listtasks', 'listhosts', 'syntax', 'connection','module_path', 'forks', 
        'remote_user', 'private_key_file', 'ssh_common_args', 'ssh_extra_args', 
        'sftp_extra_args', 'scp_extra_args', 'become', 'become_method', 
        'become_user', 'verbosity', 'check'])

    def __init__(self):
        self.variable_manager = VariableManager()
        self.loader = DataLoader()
        self.nm = nmap.PortScanner()
        self.hosts = []
        self.inventory = """
                    [DYNAMIC]
                    {{ host_list }}
                    """
        with open("boot.cfg","r") as f:
            self.configuration = yaml.load(f)

    def scan(self,range='10.65.82.60-100'):
        self.nm.scan(range,arguments=self.configuration['configuration']
                ['scan_args'])
        self.hosts = self.nm.all_hosts()
        if not self.hosts:
            print("No hosts found")
            sys.exit()

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

        self.options = Boot.options(listtags=False, listtasks=False, listhosts=False, 
                syntax=False, connection='ssh', module_path=None, forks=100, 
                remote_user=self.configuration['configuration']['remote_user'],
                private_key_file=self.configuration['configuration']['private_key_file']
                ,ssh_common_args=None, 
                ssh_extra_args=None, sftp_extra_args=None, scp_extra_args=None, 
                become=True, become_method=None, 
                become_user=self.configuration['configuration']
                ['become_user'], 
                verbosity=3, check=False)

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
        play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        tqm = None
        try:
            tqm = TaskQueueManager(
                    inventory = self.inventory,
                    variable_manager = self.variable_manager,
                    loader = self.loader,
                    options = self.options,
                    passwords = self.passwords)
            result = tqm.run(play)
        finally:
            if tqm is not None:
                tqm.cleanup()

    def execute_boot(self):        
        playbook_path = 'boot.yml'
        if not os.path.exists(playbook_path):
            print('[INFO] The playbook does not exist')
            sys.exit()
        
        self.variable_manager.extra_vars = {'hosts': 'DYNAMIC'} 
        pbex = PlaybookExecutor(playbooks=[playbook_path], 
                inventory=self.inventory, 
                variable_manager=self.variable_manager, 
                loader=self.loader, options=self.options, passwords=self.passwords)

        results = pbex.run()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-m","--module",
            help="Name of ansible module to run")
    parser.add_option("-a","--args",
            help ="Argument of module running")
    parser.add_option("-r","--range",
            help ="an nmap friendly host range to scan e.g. 127.0.0.1-100")

    (options,args) = parser.parse_args()

    b = Boot()

    if options.range:
        b.scan(options.range)
    else:
        b.scan(b.configuration['configuration']['scan_range'])

    if options.module:
        b.execute_module(options.module, options.args)
    else:
        b.execute_boot()
