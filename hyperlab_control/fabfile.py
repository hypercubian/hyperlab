import getpass
import re

from fabric import Connection, task
from tabulate import tabulate

# Define multiple remote hosts
VM_HOSTS = ["atlas"]


def get_connection(host):
    """Create a connection for the specified host."""
    user = getpass.getuser()  # Automatically use local username
    print(f"🔄 Connecting to {host} as {user}...")
    return Connection(host=host, user=user)


@task
def check_connectivity(c):
    """Check SSH connectivity on all hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        result = conn.run('powershell -Command "whoami"', hide=True)
        print(f"✅ Connected to {host} as {result.stdout.strip()}")


@task
def check_disk_space(c):
    """Check disk space on all hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        result = conn.run('powershell -Command "Get-PSDrive C | Select-Object Used, Free"', hide=True)
        print(f"📂 {host} Disk Space:\n{result.stdout.strip()}")


@task
def check_uptime(c):
    """Check system uptime on all hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        result = conn.run('powershell -Command "(get-date) - (gcim Win32_OperatingSystem).LastBootUpTime"', hide=True)
        print(f"⏳ {host} System Uptime:\n{result.stdout.strip()}")


@task
def check_all(c):
    """Run all system checks on all hosts."""
    check_connectivity(c)
    check_disk_space(c)
    check_uptime(c)


@task
def list_vms(c):
    """List all VMs on all hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        result = conn.run('powershell -Command "Get-VM"', hide=True)
        print(f"🖥️ {host} VMs:\n{result.stdout.strip()}")


@task
def stop_vm(c, vm_name):
    """Stop a VM on all hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        result = conn.run(f'powershell -Command "Stop-VM -Name {vm_name}"', hide=True)
        print(f"🛑 Stopped {vm_name} on {host}")


def start_vm(c, vm_name):
    """Start a VM on all hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        result = conn.run(f'powershell -Command "Start-VM -Name {vm_name}"', hide=True)
        print(f"▶️ Started {vm_name} on {host}")


status_map = {"Operating normally": "OK"}


def replace_status(line):
    # Replace status if any substring matches the status_map keys
    for status, repl in status_map.items():
        if status in line:
            line = line.replace(status, repl)
    return line


def parse_hyperv_output(data):
    lines = data.strip().split("\n")

    # Extract column headers by splitting on multiple spaces
    headers = lines[0].split()

    # Skip the headers and separator line
    data_lines = lines[2:]

    result = []
    for index, line in enumerate(data_lines, start=1):
        line = replace_status(line)
        values = line.split()
        # Ensure the number of extracted values matches the headers
        entry = {"Index": index, **{headers[i]: (values[i] if i < len(values) else "") for i in range(len(headers))}}
        result.append(entry)

    return result


def print_vm_table(vm_list):
    headers = vm_list[0].keys()  # Extract headers from the first dictionary
    table = [vm.values() for vm in vm_list]  # Extract values from each dictionary
    print(tabulate(table, headers=headers, tablefmt="simple"))


@task
def get_hyperlab(c):
    """Get all VMs with names starting with 'hyperlab' on Hyper-V hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        result = conn.run('powershell -Command "Get-VM | Where-Object { $_.Name -like \'hyperlab*\' }"', hide=True)
        print(f"🖥️ {host} HyperLab VMs:\n{result.stdout.strip()}")


@task
def stop_vm_i(c):
    """Interactively stop a VM on all hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        result = conn.run('powershell -Command "Get-VM"', hide=True)
        print(f"🖥️ {host} VMs:")
        print_vm_table(parse_hyperv_output(result.stdout.strip()))

    selected_index = int(input("Select VM (Index): "))

    # Stop
    selected_vm = None
    for host in VM_HOSTS:
        conn = get_connection(host)
        result = conn.run('powershell -Command "Get-VM"', hide=True)
        vm_list = parse_hyperv_output(result.stdout.strip())
        selected_vm = vm_list[selected_index - 1]["Name"]
        break  # Assuming the VM names are unique across hosts

    for host in VM_HOSTS:
        conn = get_connection(host)
        conn.run(f'powershell -Command "Stop-VM -Name {selected_vm}"', hide=True)
        print(f"🛑 Stopped {selected_vm} on {host}")


@task
def start_vm_i(c):
    """Interactively start a VM on all hosts."""
    for host in VM_HOSTS:
        conn = get_connection(host)
        result = conn.run('powershell -Command "Get-VM"', hide=True)
        print(f"🖥️ {host} VMs:")
        print_vm_table(parse_hyperv_output(result.stdout.strip()))

    selected_index = int(input("Select VM (Index): "))

    # Start
    selected_vm = None
    for host in VM_HOSTS:
        conn = get_connection(host)
        result = conn.run('powershell -Command "Get-VM"', hide=True)
        vm_list = parse_hyperv_output(result.stdout.strip())
        selected_vm = vm_list[selected_index - 1]["Name"]
        break  # Assuming the VM names are unique across hosts

    for host in VM_HOSTS:
        conn = get_connection(host)
        conn.run(f'powershell -Command "Start-VM -Name {selected_vm}"', hide=True)
        print(f"▶️ Started {selected_vm} on {host}")
