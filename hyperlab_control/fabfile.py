import getpass
import logging
import socket

from fabric import Connection, task

# Logging Configuration
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(message)s",
    level=logging.INFO
)

VM_HOSTS = ["atlas"]


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


# Dictionary of hosts and their MAC addresses (Update this with real MACs)
MAC_ADDRESSES = {
    "atlas": "58:47:CA:75:EB:98"  # Replace with the actual MAC address
}


#
#
# @task


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
