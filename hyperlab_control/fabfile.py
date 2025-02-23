import getpass
import json
import logging
import os
import socket

import paramiko
from fabric import Connection, task

# Logging Configuration
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    level=logging.INFO
)

VM_HOSTS = ["atlas"]

MAC_ADDRESSES = {
    "atlas": "58:47:CA:75:EB:98"
}


def get_connection(host):
    """Establish an SSH connection to the given host."""
    user = getpass.getuser()
    try:
        logging.info(f"🔄 Connecting to {host} as {user}...")
        return Connection(host=host, user=user)
    except Exception as e:
        logging.error(f"❌ Failed to connect to {host}: {e}")
        return None


def execute_command(conn, command):
    """Execute a PowerShell command and return stdout, or None if it fails."""
    try:
        return conn.run(f'powershell -Command "{command}"', hide=True).stdout.strip()
    except Exception as e:
        logging.error(f"⚠️ Command execution failed: {command}\n{e}")
        return None


@task
def check_connectivity(c):
    """Check connectivity to all VM hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue
        result = execute_command(conn, "whoami")
        if result:
            logging.info(f"✅ Connected to {host} as {result}")


@task
def check_disk_space(c):
    """Check disk space usage on all VM hosts."""
    command = """Get-PSDrive C | Select-Object @{Name='Used (GB)'; Expression={[math]::Round($_.Used / 1GB,2)}}, 
                 @{Name='Free (GB)'; Expression={[math]::Round($_.Free / 1GB,2)}}"""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if conn:
            result = execute_command(conn, command)
            if result:
                logging.info(f"📂 {host} Disk Space:\n{result}")


@task
def check_uptime(c):
    """Check system uptime for all VM hosts."""
    command = "(get-date) - (gcim Win32_OperatingSystem).LastBootUpTime"
    for host in VM_HOSTS:
        conn = get_connection(host)
        if conn:
            result = execute_command(conn, command)
            if result:
                logging.info(f"⏳ {host} System Uptime:\n{result}")


@task
def list_vms(c):
    """List all VMs on all VM hosts."""
    command = "Get-VM"
    for host in VM_HOSTS:
        conn = get_connection(host)
        if conn:
            result = execute_command(conn, command)
            if result:
                logging.info(f"🖥️ {host} VMs:\n{result}")


@task
def manage_vm(c, vm_name, action):
    """Start or stop a VM by name."""
    if action not in ["Start", "Stop", "Save"]:
        logging.error("❌ Invalid action. Use 'Start', 'Stop', or 'Save'.")
        return

    for host in VM_HOSTS:
        conn = get_connection(host)
        if conn:
            result = execute_command(conn, f"{action}-VM -Name {vm_name}")
            if result is not None:
                logging.info(f"✅ {action}ed {vm_name} on {host}")


@task
def start_vm(c, vm_name):
    """Start a VM by name."""
    manage_vm(c, vm_name, "Start")


@task
def stop_vm(c, vm_name):
    """Stop a VM by name."""
    manage_vm(c, vm_name, "Stop")


def get_hyperlab_vms(conn):
    """Retrieve the list of HyperLab VMs from a connection."""
    result = execute_command(conn,
                             "Get-VM | Where-Object { $_.Name -like 'hyperlab*' } | Select-Object -ExpandProperty Name")
    return [vm.strip() for vm in result.split("\n") if vm.strip()] if result else []


@task
def list_hyperlab_vms(c):
    """List only VMs that start with 'hyperlab' on all VM hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue
        hyperlab_vms = get_hyperlab_vms(conn)
        if hyperlab_vms:
            logging.info(f"🖥️ {host} HyperLab VMs:\n" + "\n".join(hyperlab_vms))
        else:
            logging.info(f"⚠️ No HyperLab VMs found on {host}.")


@task
def create_hyperlab_checkpoints(c):
    """Create checkpoints for all HyperLab VMs on all VM hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        hyperlab_vms = get_hyperlab_vms(conn)
        if not hyperlab_vms:
            logging.info(f"⚠️ No HyperLab VMs found on {host}. Skipping checkpoint creation.")
            continue

        for vm_name in hyperlab_vms:
            checkpoint_name = f"Checkpoint-{vm_name}"
            result = execute_command(conn, f'Checkpoint-VM -Name {vm_name} -SnapshotName "{checkpoint_name}"')
            if result is not None:
                logging.info(f"✅ Created checkpoint '{checkpoint_name}' for {vm_name} on {host}")


@task
def list_hyperlab_checkpoints(c):
    """List checkpoints for all HyperLab VMs on all VM hosts (without table formatting)."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        hyperlab_vms = get_hyperlab_vms(conn)
        if not hyperlab_vms:
            logging.info(f"⚠️ No HyperLab VMs found on {host}.")
            continue

        for vm_name in hyperlab_vms:
            checkpoint_data = execute_command(conn, f'Get-VMSnapshot -VMName {vm_name}')
            if checkpoint_data:
                logging.info(f"📂 {host} {vm_name} Checkpoints:\n{checkpoint_data}")
            else:
                logging.info(f"⚠️ No checkpoints found for {vm_name} on {host}.")


@task
def save_hyperlab_vms(c):
    """Save (pause) all HyperLab VMs on all VM hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        hyperlab_vms = get_hyperlab_vms(conn)
        if not hyperlab_vms:
            logging.info(f"⚠️ No HyperLab VMs found on {host}. Skipping save operation.")
            continue

        for vm_name in hyperlab_vms:
            result = execute_command(conn, f'Save-VM -Name {vm_name}')
            if result is not None:
                logging.info(f"💾 Saved state of {vm_name} on {host}")
            else:
                logging.error(f"⚠️ Failed to save state of {vm_name} on {host}.")


@task
def start_lab(c):
    """Start all HyperLab VMs on all VM hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        hyperlab_vms = get_hyperlab_vms(conn)
        if not hyperlab_vms:
            logging.info(f"⚠️ No HyperLab VMs found on {host}. Skipping start operation.")
            continue

        for vm_name in hyperlab_vms:
            result = execute_command(conn, f'Start-VM -Name {vm_name}')
            if result is not None:
                logging.info(f"▶️ Started {vm_name} on {host}")
            else:
                logging.error(f"⚠️ Failed to start {vm_name} on {host}.")


@task
def stop_lab(c):
    """Stop all HyperLab VMs on all VM hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        hyperlab_vms = get_hyperlab_vms(conn)
        if not hyperlab_vms:
            logging.info(f"⚠️ No HyperLab VMs found on {host}. Skipping stop operation.")
            continue

        for vm_name in hyperlab_vms:
            result = execute_command(conn, f'Stop-VM -Name {vm_name}')
            if result is not None:
                logging.info(f"🛑 Stopped {vm_name} on {host}")
            else:
                logging.error(f"⚠️ Failed to stop {vm_name} on {host}.")


@task
def stop_all_vms(c):
    """Stop all VMs on all VM hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        # Get all VMs
        all_vms = execute_command(conn, "Get-VM | Select-Object -ExpandProperty Name")
        vms = [vm.strip() for vm in all_vms.split("\n") if vm.strip()] if all_vms else []

        if not vms:
            logging.info(f"⚠️ No VMs found on {host}. Skipping stop operation.")
            continue

        for vm_name in vms:
            result = execute_command(conn, f'Stop-VM -Name {vm_name}')
            if result is not None:
                logging.info(f"🛑 Stopped {vm_name} on {host}")
            else:
                logging.error(f"⚠️ Failed to stop {vm_name} on {host}.")


@task
def save_vm(c, vm_name):
    """Save (pause) a specific VM on all VM hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        result = execute_command(conn, f'Save-VM -Name {vm_name}')
        if result is not None:
            logging.info(f"💾 Saved state of {vm_name} on {host}")
        else:
            logging.error(f"⚠️ Failed to save state of {vm_name} on {host}.")


@task
def wake_on_lan(c, host):
    """Send a Wake-on-LAN magic packet."""
    mac_bytes = bytes.fromhex(MAC_ADDRESSES[host].replace(':', '').replace('-', ''))
    magic_packet = b'\xff' * 6 + mac_bytes * 16

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(magic_packet, ('255.255.255.255', 9))


@task
def get_host_mac(c):
    """Retrieve the MAC address of the primary network adapter for each host."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        command = 'Get-NetAdapter | Where-Object { $_.Status -eq `"Up`" } | Select-Object -ExpandProperty MacAddress'
        result = execute_command(conn, command)

        if result:
            logging.info(f"🔍 {host} MAC Address: {result}")
        else:
            logging.error(f"⚠️ Failed to retrieve MAC address for {host}.")


@task
def get_host_mac(c):
    """Retrieve the MAC address of the primary network adapter for each host."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        command = 'wmic nic where "NetEnabled=true" get MACAddress'
        result = execute_command(conn, command)

        if result:
            # Extract only the first valid MAC address (avoiding empty lines)
            mac_addresses = [line.strip() for line in result.split("\n") if line.strip()]
            primary_mac = mac_addresses[-1] if mac_addresses else "Unknown"

            logging.info(f"🔍 {host} MAC Address: {primary_mac}")
        else:
            logging.error(f"⚠️ Failed to retrieve MAC address for {host}.")


@task
def shutdown_host(c):
    """Shutdown the host machine."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        logging.info(f"🛑 Shutting down {host}...")
        result = execute_command(conn, 'powershell -ExecutionPolicy Bypass -NoProfile -Command "Stop-Computer -Force"')

        if result is not None:
            logging.info(f"✅ {host} is shutting down.")
        else:
            logging.error(f"⚠️ Failed to shut down {host}.")


@task
def hibernate_host(c):
    """Hibernate the host machine."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        logging.info(f"💤 Hibernating {host}...")
        result = execute_command(conn, 'powershell -ExecutionPolicy Bypass -NoProfile -Command "shutdown /h"')

        if result is not None:
            logging.info(f"✅ {host} is hibernating.")
        else:
            logging.error(f"⚠️ Failed to hibernate {host}.")


@task
def restart_host(c):
    """Restart the host machine."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        logging.info(f"🔄 Restarting {host}...")
        result = execute_command(conn,
                                 'powershell -ExecutionPolicy Bypass -NoProfile -Command "Restart-Computer -Force"')

        if result is not None:
            logging.info(f"✅ {host} is restarting.")
        else:
            logging.error(f"⚠️ Failed to restart {host}.")


def get_ssh_key_path():
    """Return the default SSH key path."""
    home = os.path.expanduser("~")
    return os.path.join(home, ".ssh", "id_rsa")


@task
def setup_ssh(c):
    """Sets up SSH key authentication for an Ubuntu server."""

    # Prompt for the server IP
    server_ip = input("Enter the Ubuntu server IP: ").strip()
    username = getpass.getuser()  # Get the current Windows username
    ssh_key_path = get_ssh_key_path()
    pub_key_path = f"{ssh_key_path}.pub"

    # Check if SSH key exists, generate if not
    if not os.path.exists(ssh_key_path):
        print("SSH key not found. Generating one now...")
        os.system(f'ssh-keygen -t rsa -b 4096 -f "{ssh_key_path}" -N ""')
    else:
        print("SSH key already exists. Using existing key.")

    # Ensure the public key exists
    if not os.path.exists(pub_key_path):
        print("Public key not found. Ensure ssh-keygen ran correctly.")
        return

    # Copy public key to the remote server using ssh-copy-id
    print(f"Copying SSH public key to {server_ip}...")
    os.system(f'ssh-copy-id -i "{pub_key_path}" {username}@{server_ip}')

    # Secure SSH on the server
    print("Configuring SSH settings on the server...")
    os.system()

    print("SSH key authentication setup complete!")
    print(f"You can now SSH into the server using: ssh {username}@{server_ip}")


@task
def get_vm_macs(c):
    """Retrieve VM names and their MAC addresses for all VM hosts."""
    all_vms = []

    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        logging.info(f"🔍 Retrieving VM MAC addresses from {host}...")

        # Force use of 64-bit PowerShell and load Hyper-V module
        command = (
            'powershell -NoProfile -ExecutionPolicy Bypass -Command "Get-VM | Get-VMNetworkAdapter | Select-Object VMName,MacAddress | ConvertTo-Json -Depth 1'
        )

        result = execute_command(conn, command)

        if result:
            try:
                vms = json.loads(result.strip())
                if isinstance(vms, dict):  # Single VM case
                    vms = [vms]

                for vm in vms:
                    vm["Host"] = host

                all_vms.extend(vms)
                logging.info(f"✅ Retrieved {len(vms)} VM MACs from {host}.")
            except json.JSONDecodeError as e:
                logging.error(f"⚠️ Failed to parse JSON from {host}: {e}\nRaw Output:\n{result}")
        else:
            logging.error(f"⚠️ No VM MAC addresses found on {host}.")

    if all_vms:
        print(json.dumps(all_vms, indent=4))
    else:
        logging.info("⚠️ No VM MAC addresses retrieved.")


def retrieve_vm_macs_via_ssh(host):
    """
    Retrieve VM MAC addresses via direct SSH and return as a list of dictionaries.

    Args:
        host (str): The remote machine's hostname or IP.

    Returns:
        list[dict]: A list of VM MAC addresses with structure:
        [
            {"Host": "atlas", "VMName": "VM1", "MacAddress": "00:15:5D:23:4A:12"},
            {"Host": "atlas", "VMName": "VM2", "MacAddress": "00:15:5D:67:89:AB"}
        ]
    """
    username = getpass.getuser()
    mac_list = []

    try:
        logging.info(f"🔍 Connecting via SSH to {host}...")

        # Establish SSH connection
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username)

        logging.info(f"✅ SSH connection established with {host}")

        # Run PowerShell command to retrieve VM MAC addresses
        command = (
            'powershell -NoProfile -ExecutionPolicy Bypass -Command '
            '"Get-VM | Get-VMNetworkAdapter | Select-Object VMName,MacAddress | ConvertTo-Json -Depth 1"'
        )
        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        client.close()

        if error:
            logging.error(f"⚠️ PowerShell Error from {host}:\n{error}")
            return mac_list  # Return empty list if error occurs

        if output:
            try:
                vms = json.loads(output)

                if isinstance(vms, dict):  # Single VM case
                    vms = [vms]

                for vm in vms:
                    vm["Host"] = host  # Attach host info

                mac_list.extend(vms)
                logging.info(f"✅ Retrieved {len(vms)} VM MACs from {host}.")
            except json.JSONDecodeError as e:
                logging.error(f"⚠️ Failed to parse JSON from {host}: {e}\nRaw Output:\n{output}")

    except Exception as e:
        logging.error(f"❌ SSH connection failed to {host}: {e}")

    return mac_list  # Return list of VM MAC addresses


@task
def vm_macs(c):
    """Fabric task to retrieve VM MAC addresses via direct SSH and display them."""
    all_vm_macs = []

    for host in VM_HOSTS:
        vm_macs = retrieve_vm_macs_via_ssh(host)
        all_vm_macs.extend(vm_macs)

    # Print structured output
    if all_vm_macs:
        print(json.dumps(all_vm_macs, indent=4))
    else:
        logging.info("⚠️ No VM MAC addresses retrieved.")


def retrieve_vm_network_info(host):
    """
    Retrieve VM names, MAC addresses, and IP addresses via SSH using PowerShell.

    Args:
        host (str): The remote machine's hostname or IP.

    Returns:
        list[dict]: A list of VM network information with structure:
        [
            {"Host": "atlas", "VMName": "VM1", "IP": "192.168.1.101", "MAC": "00:15:5D:23:4A:12"},
            {"Host": "atlas", "VMName": "VM2", "IP": "192.168.1.102", "MAC": "00:15:5D:67:89:AB"}
        ]
    """
    username = getpass.getuser()
    vm_network_info = []

    try:
        logging.info(f"🔍 Connecting via SSH to {host}...")

        # Establish SSH connection
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(hostname=host, username=username)

        logging.info(f"✅ SSH connection established with {host}")

        # PowerShell command to get VM Names, MAC addresses, and IP addresses
        command = (
            'powershell -NoProfile -ExecutionPolicy Bypass -Command '
            '"Get-VM | Get-VMNetworkAdapter | Select-Object VMName, MacAddress, IPAddresses | '
            'ConvertTo-Json -Depth 2"'
        )

        stdin, stdout, stderr = client.exec_command(command)

        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        client.close()

        if error:
            logging.error(f"⚠️ PowerShell Error from {host}:\n{error}")
            return vm_network_info  # Return empty list if error occurs

        if output:
            try:
                vms = json.loads(output)

                if isinstance(vms, dict):  # Single VM case
                    vms = [vms]

                for vm in vms:
                    ip_addresses = vm.get("IPAddresses", [])
                    primary_ip = ip_addresses[0] if ip_addresses else "Unknown"

                    vm_data = {
                        "Host": host,
                        "VMName": vm.get("VMName", "Unknown"),
                        "MAC": vm.get("MacAddress", "Unknown"),
                        "IP": primary_ip
                    }

                    vm_network_info.append(vm_data)

                logging.info(f"✅ Retrieved {len(vm_network_info)} VM network entries from {host}.")

            except json.JSONDecodeError as e:
                logging.error(f"⚠️ Failed to parse JSON from {host}: {e}\nRaw Output:\n{output}")

    except Exception as e:
        logging.error(f"❌ SSH connection failed to {host}: {e}")

    return vm_network_info  # Return list of VM network information


@task
def get_vm_net_info(c):
    """Fabric task to retrieve VM names, MAC, and IP addresses via SSH."""
    all_vm_network_data = []

    for host in VM_HOSTS:
        network_data = retrieve_vm_network_info(host)
        all_vm_network_data.extend(network_data)

    # Print structured output
    if all_vm_network_data:
        print(json.dumps(all_vm_network_data, indent=4))
    else:
        logging.info("⚠️ No VM network information retrieved.")


@task
def enable_nested_virtualization(c, vm_name):
    """Enable Nested Virtualization for a specific VM."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        if not conn:
            continue

        logging.info(f"🔧 Enabling Nested Virtualization for {vm_name} on {host}...")

        # PowerShell command to enable Nested Virtualization
        command = f'Set-VMProcessor -VMName "{vm_name}" -ExposeVirtualizationExtensions $true'

        result = execute_command(conn, command)
        if result is not None:
            logging.info(f"✅ Nested Virtualization enabled for {vm_name} on {host}.")
        else:
            logging.error(f"⚠️ Failed to enable Nested Virtualization for {vm_name} on {host}.")


@task
def lst(c):
    c.run("fab --list")

