# 全新创建rancher服务资源组。

# bash 获取登陆凭证：
# az ad sp create-for-rbac --name localtest-sp-rbac --skip-assignment


import os
import paramiko
from azure.mgmt.resource import ResourceManagementClient
from azure.identity import AzureCliCredential
from azure.identity import AzureCliCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient


os.environ["AZURE_SUBSCRIPTION_ID"] = "f6038766-7885-4773-974b-be0383525457"
os.environ["AZURE_LOCATION"] = "southeastasia"
# Acquire a credential object using CLI-based authentication.
credential = AzureCliCredential()
# Retrieve subscription ID from environment variable.
subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]

def create_vm_rancher(location="southeastasia"):
    print("创建rancher 虚拟机")
    credential = AzureCliCredential()
    subscription_id = os.environ["AZURE_SUBSCRIPTION_ID"]
    resource_client = ResourceManagementClient(credential, subscription_id)
    RESOURCE_GROUP_NAME = "ranchar-server-4"
    rg_result = resource_client.resource_groups.create_or_update(RESOURCE_GROUP_NAME,
        {
            "location": location
        }
    )
    print(f"Provisioned resource group {rg_result.name} in the {rg_result.location} region")
    VNET_NAME = "python-example-vnet"
    SUBNET_NAME = "python-example-subnet"
    IP_NAME = "python-example-ip"
    IP_CONFIG_NAME = "python-example-ip-config"
    NIC_NAME = "python-example-nic"
    # Obtain the management object for networks
    network_client = NetworkManagementClient(credential, subscription_id)

    # Provision the virtual network and wait for completion
    poller = network_client.virtual_networks.begin_create_or_update(RESOURCE_GROUP_NAME,
        VNET_NAME,
        {
            "location": location,
            "address_space": {
                "address_prefixes": ["10.0.0.0/16"]
            }
        }
    )

    vnet_result = poller.result()

    print(f"Provisioned virtual network {vnet_result.name} with address prefixes {vnet_result.address_space.address_prefixes}")

    # Step 3: Provision the subnet and wait for completion
    poller = network_client.subnets.begin_create_or_update(RESOURCE_GROUP_NAME, 
        VNET_NAME, SUBNET_NAME,
        { "address_prefix": "10.0.0.0/24" }
    )
    subnet_result = poller.result()
    print(f"Provisioned virtual subnet {subnet_result.name} with address prefix {subnet_result.address_prefix}")

    # Step 4: Provision an IP address and wait for completion
    poller = network_client.public_ip_addresses.begin_create_or_update(RESOURCE_GROUP_NAME,
        IP_NAME,
        {
            "location": location,
            "sku": { "name": "Standard" },
            "public_ip_allocation_method": "Static",
            "public_ip_address_version" : "IPV4"
        }
    )

    ip_address_result = poller.result()

    print(f"Provisioned public IP address {ip_address_result.name} with address {ip_address_result.ip_address}")

    # Step 5: Provision the network interface client
    poller = network_client.network_interfaces.begin_create_or_update(RESOURCE_GROUP_NAME,
        NIC_NAME, 
        {
            "location": location,
            "ip_configurations": [ {
                "name": IP_CONFIG_NAME,
                "subnet": { "id": subnet_result.id },
                "public_ip_address": {"id": ip_address_result.id }
            }]
        }
    )

    nic_result = poller.result()
    print(f"Provisioned network interface client {nic_result.name}")

    # Step 6: Provision the virtual machine

    # Obtain the management object for virtual machines
    compute_client = ComputeManagementClient(credential, subscription_id)

    VM_NAME = "ExampleVM"
    USERNAME = "azureuser"
    PASSWORD = "ChangePa$$w0rd24"

    print(f"Provisioning virtual machine {VM_NAME}; this operation might take a few minutes.")
    # Provision the VM specifying only minimal arguments, which defaults to an Ubuntu 18.04 VM
    # on a Standard DS1 v2 plan with a public IP address and a default virtual network/subnet.

    poller = compute_client.virtual_machines.begin_create_or_update(RESOURCE_GROUP_NAME, VM_NAME,
        {
            "location": location,
            "storage_profile": {
                "image_reference": {
                    "publisher": 'Canonical',
                    "offer": "UbuntuServer",
                    "sku": "16.04.0-LTS",
                    "version": "latest"
                }
            },
            "hardware_profile": {
                "vm_size": "Standard_DS1_v2"
            },
            "os_profile": {
                "computer_name": VM_NAME,
                "admin_username": USERNAME,
                "admin_password": PASSWORD
            },
            "network_profile": {
                "network_interfaces": [{
                    "id": nic_result.id,
                }]
            }        
        }
    )
    vm_result = poller.result()
    print(f"成功创建虚拟机 {vm_result.name}")

    print("通过ssh的方式连接使用虚拟机")

def _ssh_init_ranchar(host,password,username="code",port=22,):
    ssh = paramiko.SSHClient() 
    # 允许连接不在~/.ssh/known_hosts文件中的主机
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())    
    # 连接服务器
    ssh.connect(hostname=host, port=port, username=username, password=password)    
    # 执行命令，不要执行top之类的在不停的刷新的命令(可以执行多条命令，以分号来分隔多条命令)
    # stdin, stdout, stderr = ssh.exec_command("cd %s;mkdir %s" % ("/www/wwwroot", "aa"))
    stdin, stdout, stderr = ssh.exec_command("ping 8.8.8.8 -c 10")
    stdin.write("终端等待输入...\n")   # test.py文件有input()函数，如果不需要与终端交互，则不写这两行
    stdin.flush()
