from fabric import Connection, task
import getpass

# Define multiple remote hosts
REMOTE_HOSTS = ["atlas"]


def get_connection(host):
    """Create a connection for the specified host."""
    user = getpass.getuser()  # Automatically use local username
    print(f"🔄 Connecting to {host} as {user}...")
    return Connection(host=host, user=user)

@task
def check_connectivity(c):
    """Check SSH connectivity on all hosts."""
    for host in REMOTE_HOSTS:
        conn = get_connection(host)
        result = conn.run('powershell -Command "whoami"', hide=True)
        print(f"✅ Connected to {host} as {result.stdout.strip()}")


@task
def check_disk_space(c):
    """Check disk space on all hosts."""
    for host in REMOTE_HOSTS:
        conn = get_connection(host)
        result = conn.run('powershell -Command "Get-PSDrive C | Select-Object Used, Free"', hide=True)
        print(f"📂 {host} Disk Space:\n{result.stdout.strip()}")


@task
def check_uptime(c):
    """Check system uptime on all hosts."""
    for host in REMOTE_HOSTS:
        conn = get_connection(host)
        result = conn.run('powershell -Command "(get-date) - (gcim Win32_OperatingSystem).LastBootUpTime"', hide=True)
        print(f"⏳ {host} System Uptime:\n{result.stdout.strip()}")


@task
def check_all(c):
    """Run all system checks on all hosts."""
    check_connectivity(c)
    check_disk_space(c)
    check_uptime(c)
