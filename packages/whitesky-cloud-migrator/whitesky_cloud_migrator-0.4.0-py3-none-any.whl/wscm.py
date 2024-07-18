#!/usr/local/bin/python
import base64
from functools import wraps
import sys
import time
from typing import Dict, Set
import urllib.parse
import click
import requests
import urllib
import threading
import inquirer
from urllib.parse import urlparse
import re

@click.command()
@click.option("--ws-portal", type=str, required=True, help="Url to the cloud portal, E.g. https://portal.whitesky.cloud")
@click.option("--target-ws-portal", type=str, required=False, help="Url to the target cloud portal, E.g. https://portal.whitesky.cloud. When omitted, the target portal is the same as the source")
@click.option("--migrate-portal", type=str, required=True, help="Url to the cloud portal, E.g. https://migrate.whitesky.cloud")
@click.option("--customer-id", type=str, required=True, help="whitesky customer ID")
@click.option("--target_customer-id", type=str, required=False, help="Target whitesky customer ID. When omitted, the target_customer is the same as the source")
@click.option("--source-cloudspace", type=str, required=True, help="ID of the source cloudspace")
@click.option("--target-cloudspace", type=str, required=True, help="ID of the target cloudspace")
@click.option("--source-vm-id", type=int, multiple=True, help="ID of the virtual machine to create units and targets for. Add this option for every virtual machine you want to migrate or ommit the option to create migration options for all the VMs in the source cloudspace.")
@click.option("--jwt", type=str, required=True, help="JWT authentication token")
@click.option("--target_jwt", type=str, required=False, help="JWT authentication token. When omitted, the target_jwt is the same as the source")
@click.option("--migrate-login", type=str, required=True, help="Login on the migration portal")
@click.option("--migrate-passwd", type=str, required=True, help="Password for the migration portal")
@click.option("--vault", type=str, required=False, help="ID of the Vault to use for the units. Should be SSH-KEY based")
@click.option("--vault-pub-key", type=str, required=False, help="Pub ssh key corresponding to the vault used.")
@click.option("--ignore-target-subnet", type=bool, is_flag=True, help="Set this flag when the target subnet is different from the source")
@click.option("--skip-target-storage-match", type=bool, is_flag=True, help="When matching for target VMs in the target cloudspace, skip the match on storage")
def migrate(ws_portal, target_ws_portal, migrate_portal, source_cloudspace, target_cloudspace, source_vm_id, jwt, target_jwt, migrate_login, migrate_passwd, vault, vault_pub_key, customer_id, target_customer_id, ignore_target_subnet, skip_target_storage_match) -> None:
    migrator = Migrator(ws_portal, target_ws_portal, migrate_portal, source_cloudspace, target_cloudspace, source_vm_id, jwt, target_jwt, migrate_login, migrate_passwd, vault, vault_pub_key, customer_id, target_customer_id, ignore_target_subnet)
    migrator.validate_cloudspaces()
    migrator.login_on_migrate_portal()
    migrator.select_project()
    migrator.list_units()
    migration_ips = migrator.get_migration_ips()
    if not migration_ips:
        print("Aborted!")
        return
    source_cloudspace_portforwards = migrator.list_source_load_balancers()
    target_cloudspace_portforwards = migrator.list_target_load_balancers()
    source_vms = []
    for source_vm in migrator.list_vms_in_source_cloudspace():
        if source_vm_id and source_vm["vm_id"] in source_vm_id or not source_vm_id:
            source_vms.append(source_vm)
    create_source_portforwards(migrator, migration_ips, source_cloudspace_portforwards, source_vms)
    create_source_units(migrator, source_vms, migration_ips["source_ip"])
    target_vms = create_target_vms(migrator, source_vms, skip_target_storage_match)
    create_target_portforwards(migrator, migration_ips, target_cloudspace_portforwards, target_vms)
    create_target_units(migrator, target_vms, migration_ips["target_ip"])
    create_sets(migrator, source_vms)

def create_sets(migrator, source_vms):
    sets = migrator.list_sets()
    for source_vm in source_vms:
        for mset in sets:
            if mset["sourceId"] == source_vm["unit"]["id"] and mset["targetIds"] == [source_vm["target_vm"]["unit"]["id"]]:
                break
        else:
            migrator.create_set(vm=source_vm, vm_name=source_vm["name"])

def create_target_vms(migrator: "Migrator", source_vms, skip_target_storage_match):
    migrator.get_target_vm_image_ids()
    target_vms = migrator.list_vms_in_target_cloudspace()
    vms_created = False
    result = []
    for source_vm in source_vms:
        for target_vm in target_vms:
            if source_vm["name"] == target_vm["name"]:
                if target_vm["image_id"] not in (migrator.ubuntu_server_image_in_target["image_id"], migrator.windows_server_image_in_target["image_id"]) \
                    or target_vm["memory"] != source_vm["memory"] \
                    or target_vm["vcpus"] != source_vm["vcpus"] \
                    or (target_vm["storage"] != source_vm["storage"] and not skip_target_storage_match):
                    raise ValueError(f"The target cloudspace contains a VM with same name but conflicting properties for vm '{source_vm['name']}', please fix and retry. Aborting ... ")
                print("Found migration target for vm", source_vm["name"])
                source_vm["target_vm"] = target_vm
                result.append(target_vm)
                break
        else:
            target_vm = migrator.create_target_vm(vm=source_vm, vm_name=source_vm["name"])
            vms_created = True
    if vms_created:
        target_vms = migrator.list_vms_in_target_cloudspace()
        result = []
        for source_vm in source_vms:
            for target_vm in target_vms:
                if source_vm["name"] == target_vm["name"]:
                    if target_vm["image_id"] not in (migrator.ubuntu_server_image_in_target["image_id"], migrator.windows_server_image_in_target["image_id"]) \
                        or target_vm["memory"] != source_vm["memory"] \
                        or target_vm["vcpus"] != source_vm["vcpus"] \
                        or (target_vm["storage"] != source_vm["storage"] and not skip_target_storage_match):
                        raise ValueError(f"The target cloudspace contains a VM with same name but conflicting properties for vm '{source_vm['name']}', please fix and retry. Aborting ... ")
                    source_vm["target_vm"] = target_vm
                    result.append(target_vm)
                    break
            else:
                raise RuntimeError(f"Expected target vm for {source_vm['name']} was not found!")
    return result


def create_source_units(migrator: "Migrator", vms, ip):
    for vm in vms:
        for unit in migrator.units:
            purl = urlparse(unit["uri"])
            if vm["os"] == "Windows":
                if unit["agentPort"] == vm["agent_port"] and purl.port == 9999 and purl.hostname == ip:
                    vm["unit"] = unit
                    break
            else:
                if unit["agentPort"] == vm["agent_port"] and purl.port == vm["ssh_port"] and purl.hostname == ip:
                    vm["unit"] = unit
                    break
        else:
            migrator.create_source_unit(vm=vm, vm_name=vm["name"])
            if vm["os"] == "Windows":
                if not migrator.install_agent_in_windows_source(vm, vm_name=vm["name"]):
                    questions = [
                        inquirer.Confirm('confirm',
                                        message=f"The automated installation of the agent failed for source vm {vm['name']}. Install it manually via downloading the agent into the virtual machine yourself.",
                                        default=True),
                    ]
                    answers = inquirer.prompt(questions)

def create_target_units(migrator: "Migrator", vms, ip):
    for vm in vms:
        for unit in migrator.units:
            purl = urlparse(unit["uri"]) 
            port = vm["ssh_port"] if vm["os"] == "Linux" else 9999
            if unit["agentPort"] == vm["agent_port"] and purl.port == port and purl.hostname == ip:
                vm["unit"] = unit
                break
        else:
            migrator.create_target_unit(vm=vm, vm_name=vm["name"])
            if vm["os"] == "Windows":
                if not migrator.install_agent_in_windows_target(vm=vm, vm_name=vm["name"]):
                    questions = [
                        inquirer.Confirm('confirm',
                                        message=f"The automated installation of the agent failed for target vm {vm['name']}. Install it manually via downloading the agent into the virtual machine yourself.",
                                        default=True),
                    ]
                    answers = inquirer.prompt(questions)


def create_source_portforwards(migrator: "Migrator", migration_ips, source_cloudspace_portforwards, vms):
    source_ports_in_use = set(migrator.get_source_ports_in_use())
    for vm in vms:
        migrator.get_vm_os(vm=vm, vm_name=vm["name"])
        for port_fw in source_cloudspace_portforwards:
            if port_fw["pub_ip"] == migration_ips["source_ip"]:
                source_ports_in_use.add(port_fw["pub_port"])
            if port_fw["vm_name"] != vm["name"]:
                continue
            if vm["os"] == "Windows":
                if port_fw["private_port"] == 455 and port_fw["pub_ip"] == migration_ips["source_ip"]:
                    vm["smb_port"] = port_fw["pub_port"]
            else:
                if port_fw["private_port"] == 22 and port_fw["pub_ip"] == migration_ips["source_ip"]:
                    vm["ssh_port"] = port_fw["pub_port"]
            if port_fw["private_port"] == 8999 and port_fw["pub_ip"] == migration_ips["source_ip"]:
                vm["agent_port"] = port_fw["pub_port"]
            if (vm.get("ssh_port") or vm.get("smb_port")) and vm.get("agent_port"):
                break
        else:
            if vm["os"] == "Windows":
                if not vm.get("smb_port"):
                    # port = free(source_ports_in_use)
                    # migrator.create_smb_source_portforward(vm=vm, vm_name=vm["name"], port=port)
                    # source_ports_in_use.add(port)
                    port = None
                    vm["smb_port"] = port
            else:
                if not vm.get("ssh_port"):
                    port = free(source_ports_in_use)
                    migrator.create_ssh_source_portforward(vm=vm, vm_name=vm["name"], port=port)
                    source_ports_in_use.add(port)
                    vm["ssh_port"] = port
            if not vm.get("agent_port"):
                port = free(source_ports_in_use)
                migrator.create_agent_source_portforward(vm=vm, vm_name=vm["name"], port=port)
                source_ports_in_use.add(port)
                vm["agent_port"] = port


def create_target_portforwards(migrator: "Migrator", migration_ips, target_cloudspace_portforwards, vms):
    target_ports_in_use = set(migrator.get_target_ports_in_use())
    for vm in vms:
        migrator.get_target_vm_os(vm=vm, vm_name=vm["name"])
        for port_fw in target_cloudspace_portforwards:
            if port_fw["pub_ip"] == migration_ips["target_ip"]:
                target_ports_in_use.add(port_fw["pub_port"])
            if port_fw["vm_name"] != vm["name"]:
                continue
            if port_fw["private_port"] == 22 and port_fw["pub_ip"] == migration_ips["target_ip"]:
                vm["ssh_port"] = port_fw["pub_port"]
            if port_fw["private_port"] == 8999 and port_fw["pub_ip"] == migration_ips["target_ip"]:
                vm["agent_port"] = port_fw["pub_port"]
            if port_fw["private_port"] == 9000 and port_fw["pub_ip"] == migration_ips["target_ip"]:
                vm["data_port"] = port_fw["pub_port"]
            if vm.get("ssh_port") and vm.get("data_port") and vm.get("agent_port"):
                break
        else:
            if not vm.get("data_port"):
                port = free(target_ports_in_use)
                migrator.create_data_target_portforward(vm=vm, vm_name=vm["name"], port=port)
                target_ports_in_use.add(port)
                vm["data_port"] = port
            if not vm.get("ssh_port") and vm["os"] == "Linux":
                port = free(target_ports_in_use)
                migrator.create_ssh_target_portforward(vm=vm, vm_name=vm["name"], port=port)
                target_ports_in_use.add(port)
                vm["ssh_port"] = port
            if not vm.get("agent_port"):
                port = free(target_ports_in_use)
                migrator.create_agent_target_portforward(vm=vm, vm_name=vm["name"], port=port)
                target_ports_in_use.add(port)
                vm["agent_port"] = port



def free(in_use: Set[int]) -> int:
    for port in range(10000, 60001):
        if port not in in_use:
            return port


def animate(prompt):

    def wrapper(f):

        @wraps(f)
        def wrapped(*args, **kwargs):
            animation = "|/-\\"
            idx = 0
            stop_animation = threading.Event()

            def animate():
                print(f"{prompt.format(**kwargs)}  ", end="")
                nonlocal idx
                while not stop_animation.is_set():
                    print(chr(8), end="")
                    print(animation[idx % len(animation)], end="")
                    sys.stdout.flush()
                    idx += 1
                    time.sleep(0.1)
                print(f"{chr(8)}{chr(8)}", end="")
                sys.stdout.flush()
                print()
                    
            # Start the animation in a separate thread
            t = threading.Thread(target=animate)
            t.start()
            try:
                return f(*args, **kwargs)
            finally:
                # Stop the animation and wait for the thread to finish
                stop_animation.set()
                t.join()
        
        return wrapped
    
    return wrapper


class Migrator:

    def __init__(self, ws_portal: str, target_ws_portal: str, migrate_portal: str, source_cloudspace:str, target_cloudspace: str, source_vm_id: int, jwt: str, target_jwt: str, migrate_login: str, migrate_password: str, vault: str, vault_pub_key: str, customer_id: str, target_customer_id: str, ignore_target_subnet: bool) -> None:
        self.ws_portal = ws_portal
        self.target_ws_portal = target_ws_portal if target_ws_portal else ws_portal
        self.migrate_portal = migrate_portal
        self.source_cloudspace = source_cloudspace
        self.target_cloudspace = target_cloudspace
        self.source_vm_id = source_vm_id
        self.jwt = jwt
        self.target_jwt = target_jwt if target_jwt else jwt
        self.migrate_login = migrate_login
        self.migrate_password = migrate_password
        self.vault = vault
        self.vault_pub_key = vault_pub_key
        self.customer_id = customer_id
        self.target_customer_id = target_customer_id if target_customer_id else customer_id
        self.mp_session = requests.Session()
        self.source_location, _ = base64.urlsafe_b64decode(self.source_cloudspace.encode() + b"=" * (-len(self.source_cloudspace.encode()) % 4)).decode().split(":",1)
        self.target_location, _ = base64.urlsafe_b64decode(self.target_cloudspace.encode() + b"=" * (-len(self.target_cloudspace.encode()) % 4)).decode().split(":",1)
        self.ignore_target_subnet = ignore_target_subnet

    @animate("Validating cloudspaces")
    def validate_cloudspaces(self):
        if self.ignore_target_subnet:
            return
        source = self.ws_get(f"/api/1/customers/{self.customer_id}/cloudspaces/{self.source_cloudspace}")
        target = self.ws_get_target(f"/api/1/customers/{self.target_customer_id}/cloudspaces/{self.target_cloudspace}")
        if source["private_network"] != target["private_network"]:
            raise RuntimeError("Source and target cloudspaces have different subnets! Aborting ...")

    @animate("Logging in on the migration portal")
    def login_on_migrate_portal(self):
        response = self.mp_session.post(f"{self.migrate_portal}/api/v1/user/login", json={"username": self.migrate_login, "password": self.migrate_password})
        response.raise_for_status()

    def select_project(self):
        response = self.mp_session.get(f"{self.migrate_portal}/api/v1/project", params={"archived": "false", "tenantId":1})
        response.raise_for_status()
        projects = [{"id": project["id"], "name": project["name"]} for project in response.json()["result"]["projects"]]
        projects.append({"id": 0, "name": "Create a new project"})
        questions = [
            inquirer.List("project", 
                          message="Please select the project",
                          choices=projects),
        ]
        self.project = inquirer.prompt(questions)["project"]
        if self.project["id"] == 0 and self.project["name"] == "Create a new project":
            name = ""
            while not name:
                questions = [
                    inquirer.Text("name",
                                message="Enter project name")
                ]
                prompt_response = inquirer.prompt(questions)
                for project in projects:
                    if project["name"] == prompt_response["name"]:
                        break
                else:
                    response = self.mp_session.post(f"{self.migrate_portal}/api/v1/project/create", json={"annotation": "", "mode": "migrate", "name": prompt_response["name"], "tenantId": 1})
                    response.raise_for_status()
                    self.project = {"id": response.json()["result"]["id"], "name": prompt_response["name"]}
                    break

    @animate("Listing existing units")
    def list_units(self):
        response = self.mp_session.get(f"{self.migrate_portal}/api/v1/unit?archived=false&projectId={self.project['id']}")
        response.raise_for_status()
        self.units = response.json()["result"]["units"] or []
        return self.units
    
    @animate("Getting vm {vm_name} os")
    def get_vm_os(self, vm, vm_name):
        response = self.ws_get(f"/api/1/customers/{self.customer_id}/locations/{self.source_location}/vm-images/{vm['image_id']}")
        os = response["os_type"]
        if os not in ("Windows", "Linux"):
            raise RuntimeError(f"Unknown os {os}")
        vm["os"] = os

    @animate("Getting vm {vm_name} os")
    def get_target_vm_os(self, vm, vm_name):
        response = self.ws_get(f"/api/1/customers/{self.target_customer_id}/locations/{self.target_location}/vm-images/{vm['image_id']}")
        os = response["os_type"]
        if os not in ("Windows", "Linux"):
            raise RuntimeError(f"Unknown os {os}")
        vm["os"] = os

    @animate("Getting target OS image IDs")
    def get_target_vm_image_ids(self):
        response = self.ws_get_target(f"/api/1/customers/{self.target_customer_id}/locations/{self.target_location}/vm-images")
        self.ubuntu_server_image_in_target = None
        self.windows_server_image_in_target = None
        for vm_image in response["result"]:
            if "image:5fda5c1a1ed0bc000145b631" in vm_image["tags"]:
                self.ubuntu_server_image_in_target = vm_image
            if "image:63f49bd6b4b6f40001feb2e9" in vm_image["tags"]:
                self.windows_server_image_in_target = vm_image
            if self.ubuntu_server_image_in_target and self.windows_server_image_in_target:
                break
        else:
            RuntimeError("The target location does not hold the (correct) images")
        return self.ubuntu_server_image_in_target, self.windows_server_image_in_target
    
    @animate("Creating target vm for {vm_name}")
    def create_target_vm(self, vm, vm_name):
        vm_details = self.ws_get(f"/api/1/customers/{self.customer_id}/cloudspaces/{self.source_cloudspace}/vms/{vm['vm_id']}")
        for disk in vm_details["disks"]:
            if disk["disk_type"] not in ("BOOT", "DATA"):
                raise RuntimeError(f"VM {vm_name} has special disks. Please create the target manually! Aborting ...")
        for disk in vm_details["disks"]:
            if disk["disk_type"] == "BOOT":
                boot_disk_size = disk["disk_size"]
                break
        else:
            raise RuntimeError(f"VM {vm_name} does not have a boot disk! Aborting ... ")
        if not self.ignore_target_subnet:
            for nic in vm_details["network_interfaces"]:
                if nic["nic_type"] == "INTERNAL":
                    private_ip = nic["ip_address"]
                    break
            else:
                raise RuntimeError(f"VM {vm_name} has no cloudspace network interface! Aborting ...")
        if vm["os"] == "Linux":
            if not self.vault or not self.vault_pub_key:
                raise ValueError("For migrating Linux machines, the --vault and --vault-pub-key options are required")
        params = {
            "name": vm["name"],
            "description": vm_details["description"],
            "data_disks": ",".join(str(disk["disk_size"]) for disk in vm_details["disks"] if disk["disk_type"] != "BOOT"),
            "vcpus": vm_details["vcpus"],
            "memory": vm_details["memory"],
            "user_data": self.vault_pub_key,
            "image_id": self.ubuntu_server_image_in_target["image_id"] if vm["os"] == "Linux" else self.windows_server_image_in_target["image_id"],
            "disk_size": boot_disk_size,
            "enable_vm_agent": "false" if vm["os"] == "Linux" else "true",
            "boot_type": "bios"
        }
        if not self.ignore_target_subnet:
            params["private_ip"] = private_ip
        if not params["data_disks"]:
            del params["data_disks"]
        target_vm = self.ws_post_target(f"/api/1/customers/{self.target_customer_id}/cloudspaces/{self.target_cloudspace}/vms", body={"gpu_id":"","vgpu_name":""}, **params)
        if vm_details["cpu_topology"]["cores"] != 1 or vm_details["cpu_topology"]["threads"] != 1:
            self.ws_post(f"/api/1/customers/{self.target_customer_id}/cloudspaces/{self.target_cloudspace}/vms/{target_vm['vm_id']}/stop?force=false")
            self.ws_post(f"/api/1/customers/{self.target_customer_id}/cloudspaces/{self.target_cloudspace}/vms/{target_vm['vm_id']}/cpu-topology", body=vm_details["cpu_topology"])
            self.ws_post(f"/api/1/customers/{self.target_customer_id}/cloudspaces/{self.target_cloudspace}/vms/{target_vm['vm_id']}/start")
        return target_vm

    @animate("Creating source unit for vm {vm_name}")
    def create_source_unit(self, vm, vm_name):
        if vm["os"] == "Linux":
            uri = f"ssh://{self.migration_ips['source_ip']}:{vm['ssh_port']}"
            if not self.vault or not self.vault_pub_key:
                raise ValueError("For migrating Linux machines, the --vault and --vault-pub-key options are required")
        else:
            uri = f"smb://{self.migration_ips['source_ip']}:9999"
        vm["uri"] = uri
        response = self.mp_session.post(f"{self.migrate_portal}/api/v1/unit/createWithAgent", json={
            "agentIp": self.migration_ips["source_ip"],
            "agentPort": vm["agent_port"],
            "annotation": f"{self.ws_portal}/customer/{self.customer_id}/cloudspaces/{self.source_cloudspace}/vms/{vm['vm_id']}",
            "name": f"OLD - {vm['name']}",
            "os": vm["os"],
            "projectId": self.project["id"],
            "uri": vm["uri"],
            "vaultId": self.vault if vm["os"] == "Linux" else None
        })
        response.raise_for_status()
        vm["unit"] = response.json()["result"]["unit"]
        if vm["os"] == "Linux":
            response = self.mp_session.post(f"{self.migrate_portal}/api/v1/agent/{vm['unit']['id']}/install")
            response.raise_for_status()

    @animate("Installing agent in windows source vm {vm_name}")
    def install_agent_in_windows_source(self, vm, vm_name):
        for _ in range(5):
            try:
                while True:
                    response = self.ws_get(f"/api/1/customers/{self.customer_id}/cloudspaces/{self.source_cloudspace}/vms/{vm['vm_id']}/agent")
                    if response["status"] == "RUNNING":
                        break
                    time.sleep(5)
                response = self.mp_session.get(f"{self.migrate_portal}/api/v1/agent/{vm['unit']['id']}/link/new")
                response.raise_for_status()
                install_script = response.json()["result"]["curl_cmd"].replace("http://", "https://")
                self.ws_post(f"/api/1/customers/{self.customer_id}/cloudspaces/{self.source_cloudspace}/vms/{vm['vm_id']}/file", body={
                        "content": base64.b64encode(install_script.encode()).decode(),
                        "filepath": "C:\\install_agent.ps1",
                        "append": False
                    })
                self.ws_post(f"/api/1/customers/{self.customer_id}/cloudspaces/{self.source_cloudspace}/vms/{vm['vm_id']}/exec", body={
                        "command": "powershell",
                        "args": [
                            "-ExecutionPolicy",
                            "Bypass",
                            "-File",
                            "C:\\install_agent.ps1"
                        ]
                    })
                return True
            except:
                time.sleep(10)
                pass
        return False

            
    @animate("Listing sets")
    def list_sets(self):
        response = self.mp_session.get(f"{self.migrate_portal}/api/v1/set?projectId={self.project['id']}")
        response.raise_for_status()
        self.sets = response.json()["result"]["sets"]
        return self.sets
    
    @animate("Creating set for vm {vm_name}")
    def create_set(self, vm, vm_name):
        response = self.mp_session.post(f"{self.migrate_portal}/api/v1/set/create", json={
            "annotation": "Created by migrate.py",
            "name": f"Migrate {vm['name']}",
            "projectId": self.project["id"],
            "sourceId": vm["unit"]["id"],
            "targetIds": [vm["target_vm"]["unit"]["id"]]
        })
        response.raise_for_status()

    @animate("Creating target unit for vm {vm_name}")
    def create_target_unit(self, vm, vm_name):
        if vm["os"] == "Linux":
            if not self.vault or not self.vault_pub_key:
                raise ValueError("For migrating Linux machines, the --vault and --vault-pub-key options are required")
        uri = f"ssh://{self.migration_ips['target_ip']}:{vm['ssh_port']}" if vm["os"] == "Linux" else f"smb://{self.migration_ips['target_ip']}:9999"
        vm["uri"] = uri
        response = self.mp_session.post(f"{self.migrate_portal}/api/v1/unit/createWithAgent", json={
            "agentIp": self.migration_ips["target_ip"],
            "agentPort": vm["agent_port"],
            "annotation": f"{self.ws_portal}/customer/{self.customer_id}/cloudspaces/{self.source_cloudspace}/vms/{vm['vm_id']}",
            "name": f"NEW - {vm['name']}",
            "os": vm["os"],
            "projectId": self.project["id"],
            "uri": vm["uri"],
            "vaultId": self.vault if vm["os"] == "Linux" else None
        })
        vm["unit"] = response.json()["result"]["unit"]
        if vm["os"] == "Linux":
            response = self.mp_session.post(f"{self.migrate_portal}/api/v1/agent/{vm['unit']['id']}/install")
            response.raise_for_status()

    @animate("Installing agent in windows target vm {vm_name}")
    def install_agent_in_windows_target(self, vm, vm_name) -> bool:
        for _ in range(5):
            try:
                while True:
                    response = self.ws_get_target(f"/api/1/customers/{self.target_customer_id}/cloudspaces/{self.target_cloudspace}/vms/{vm['vm_id']}/agent")
                    if response["status"] == "RUNNING":
                        break
                    time.sleep(5)
                response = self.mp_session.get(f"{self.migrate_portal}/api/v1/agent/{vm['unit']['id']}/link/new")
                response.raise_for_status()
                install_script = response.json()["result"]["curl_cmd"].replace("http://", "https://")
                self.ws_post_target(f"/api/1/customers/{self.target_customer_id}/cloudspaces/{self.target_cloudspace}/vms/{vm['vm_id']}/file", body={
                        "content": base64.b64encode(install_script.encode()).decode(),
                        "filepath": "C:\\install_agent.ps1",
                        "append": False
                    })
                self.ws_post_target(f"/api/1/customers/{self.target_customer_id}/cloudspaces/{self.target_cloudspace}/vms/{vm['vm_id']}/exec", body={
                        "command": "powershell",
                        "args": [
                            "-ExecutionPolicy",
                            "Bypass",
                            "-File",
                            "C:\\install_agent.ps1"
                        ]
                    })
                return True
            except:
                time.sleep(10)
                pass
        return False
            

    @animate("Listing the virtual machines in the source cloudspace")
    def list_vms_in_source_cloudspace(self):
        self.source_vms = self.ws_get(f"/api/1/customers/{self.customer_id}/cloudspaces/{self.source_cloudspace}/vms")["result"]
        for vm in self.source_vms:
            vm["private_ip"] = vm["network_interfaces"][0]["ip_address"]
        return self.source_vms

    @animate("Listing the virtual machines in the target cloudspace")
    def list_vms_in_target_cloudspace(self):
        self.target_vms = self.ws_get_target(f"/api/1/customers/{self.target_customer_id}/cloudspaces/{self.target_cloudspace}/vms")["result"]
        for vm in self.target_vms:
            vm["private_ip"] = vm["network_interfaces"][0]["ip_address"]
        return self.target_vms

    @animate("Get source cloudspace info")
    def list_source_cloudspace_external_ips(self):
        self.source_external_ips = self.ws_get(f"/api/1/customers/{self.customer_id}/cloudspaces/{self.source_cloudspace}/external-networks")["result"]
        return self.source_external_ips
    
    def get_migration_ips(self):
        questions = [
            inquirer.List("source_ip", 
                          message="Please select the external migration ip of the source cloudspace",
                          choices=[network["external_network_ip"] for network in self.list_source_cloudspace_external_ips()]),
            inquirer.List("target_ip", 
                          message="Please select the esternal migration ip for the target cloudspace",
                          choices=[network["external_network_ip"] for network in self.list_target_cloudspace_external_ips()])
        ]
        self.migration_ips = inquirer.prompt(questions)
        self.migration_ips["source_ip"], _ = self.migration_ips["source_ip"].split("/", 1)
        self.migration_ips["target_ip"], _ = self.migration_ips["target_ip"].split("/", 1)
        return self.migration_ips
    
    @animate("Get target cloudspace info")
    def list_target_cloudspace_external_ips(self):
        self.target_external_ips = self.ws_get_target(f"/api/1/customers/{self.target_customer_id}/cloudspaces/{self.target_cloudspace}/external-networks")["result"]
        return self.target_external_ips
    
    @animate("Getting source ports in use by portforwards")
    def get_source_ports_in_use(self):
        result = []
        for pf in self.ws_get(f"/api/1/customers/{self.customer_id}/cloudspaces/{self.source_cloudspace}/portforwards")["result"]:
            if pf["public_ip"] == self.migration_ips["source_ip"]:
                result.append(pf["public_port"])
        return result

    @animate("Getting target ports in use by portforwards")
    def get_target_ports_in_use(self):
        result = []
        for pf in self.ws_get_target(f"/api/1/customers/{self.target_customer_id}/cloudspaces/{self.target_cloudspace}/portforwards")["result"]:
            if pf["public_ip"] == self.migration_ips["target_ip"]:
                result.append(pf["public_port"])
        return result

    @animate("Listing load balancers in the source cloudspace")
    def list_source_load_balancers(self):
        lbs = self.ws_get(f"/api/1/customers/{self.customer_id}/cloudspaces/{self.source_cloudspace}/ingress/load-balancers")["result"]
        self.source_port_fwds = [pf for pf in (self.parse_port_forward_name(lb["name"]) for lb in lbs) if pf]
        return self.source_port_fwds

    @animate("Listing load balancers in the target cloudspace")
    def list_target_load_balancers(self):
        lbs = self.ws_get_target(f"/api/1/customers/{self.target_customer_id}/cloudspaces/{self.target_cloudspace}/ingress/load-balancers")["result"]
        self.target_port_fwds = [pf for pf in (self.parse_port_forward_name(lb["name"]) for lb in lbs) if pf]
        return self.target_port_fwds
    
    def create_port_forward(self, cloudspace, vm, pub_ip, pub_port, private_port):
        name = self.get_port_forward_name(vm, pub_ip, pub_port, private_port)
        api = cloudspace == self.source_cloudspace and self.ws_post or self.ws_post_target
        pool_id = api(f"/api/1/customers/{self.customer_id}/cloudspaces/{cloudspace}/ingress/server-pools", name=name)["id"]
        api(f"/api/1/customers/{self.customer_id}/cloudspaces/{cloudspace}/ingress/server-pools/{pool_id}/hosts", address=vm["private_ip"])
        api(f"/api/1/customers/{self.customer_id}/cloudspaces/{cloudspace}/ingress/load-balancers", body={
            "name": name,
            "type": "tcp",
            "front_end": {
                "port": pub_port,
                "ip_address": pub_ip,
                "tls": {
                    "is_enabled": False,
                    "tls_termination": True
                }
            },
            "back_end": {
                "serverpool_id": pool_id,
                "target_port": private_port
            }
        })

    def get_port_forward_name(self, vm, pub_ip, pub_port, private_port):
        return f"port-forward-{pub_ip}:{pub_port}->{vm['name']}:{private_port}"
    
    def parse_port_forward_name(self, name):
        match = re.match(r"^port-forward-(.*?):(\d+)->(.*?):(\d+)$", name)
        if not match:
            return None
        return {
            "pub_ip": match.group(1),
            "pub_port": int(match.group(2)),
            "vm_name": match.group(3),
            "private_port": int(match.group(4))
        }

    @animate("Creating ssh access for source vm {vm_name}")
    def create_ssh_source_portforward(self, vm=None, vm_name=None, port=None) -> None:
        self.create_port_forward(self.source_cloudspace, vm, self.migration_ips["source_ip"], port, 22)

    @animate("Creating ssh access for target vm {vm_name}")
    def create_ssh_target_portforward(self, vm=None, vm_name=None, port=None) -> None:
        self.create_port_forward(self.target_cloudspace, vm, self.migration_ips["target_ip"], port, 22)

    @animate("Creating smb access for source vm {vm_name}")
    def create_smb_source_portforward(self, vm=None, vm_name=None, port=None) -> None:
        self.create_port_forward(self.source_cloudspace, vm, self.migration_ips["source_ip"], port, 455)

    @animate("Creating agent access for source vm {vm_name}")
    def create_agent_source_portforward(self, vm=None, vm_name=None, port=None) -> None:
        self.create_port_forward(self.source_cloudspace, vm, self.migration_ips["source_ip"], port, 8999)

    @animate("Creating agent access for target vm {vm_name}")
    def create_agent_target_portforward(self, vm=None, vm_name=None, port=None) -> None:
        self.create_port_forward(self.target_cloudspace, vm, self.migration_ips["target_ip"], port, 8999)

    @animate("Creating data access for target vm {vm_name}")
    def create_data_target_portforward(self, vm=None, vm_name=None, port=None) -> None:
        self.create_port_forward(self.target_cloudspace, vm, self.migration_ips["target_ip"], port, 9000)

    def ws_get(self, path: str, __jwt__: str = None, **kwargs: Dict[str,str]) -> Dict:
        resp = requests.get(f"{self.ws_portal}{path}?{urllib.parse.urlencode(kwargs)}", headers={"Authorization": f"Bearer {__jwt__ or self.jwt}"})
        resp.raise_for_status()
        return resp.json()

    def ws_get_target(self, *args, **kwargs) -> Dict:
        return self.ws_get(*args, __jwt__=self.target_jwt, **kwargs)
    
    def ws_post(self, path: str, body: Dict = None, __jwt__: str = None, **kwargs: Dict[str,str]) -> Dict:
        resp = requests.post(f"{self.ws_portal}{path}?{urllib.parse.urlencode(kwargs)}", headers={"Authorization": f"Bearer {__jwt__ or self.jwt}"}, json=body)
        resp.raise_for_status()
        return resp.json()
    
    def ws_post_target(self, *args, **kwargs) -> Dict:
        return self.ws_post(*args, __jwt__=self.target_jwt, **kwargs)

    def ws_put(self, path: str, body: Dict = None, __jwt__: str = None, **kwargs: Dict[str,str]) -> Dict:
        resp = requests.put(f"{self.ws_portal}{path}?{urllib.parse.urlencode(kwargs)}", headers={"Authorization": f"Bearer {__jwt__ or self.jwt}"}, json=body)
        resp.raise_for_status()
        return resp.json()
    
    def ws_put_target(self, *args, **kwargs) -> Dict:
        return self.ws_put_target(*args, __jwt__=self.target_jwt, **kwargs)

    def ws_delete(self, path: str, __jwt__: str = None, **kwargs: Dict[str,str]) -> Dict:
        resp = requests.delete(f"{self.ws_portal}{path}?{urllib.parse.urlencode(kwargs)}", headers={"Authorization": f"Bearer {__jwt__ or self.jwt}"})
        resp.raise_for_status()

    def ws_delete_target(self, *args, **kwargs) -> Dict:
        return self.ws_delete(*args, __jwt__=self.target_jwt, **kwargs)


def main():
    migrate(auto_envvar_prefix="WS")

if __name__ == "__main__":
    main()