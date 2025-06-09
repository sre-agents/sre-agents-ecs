data = [
    {
        "prompt": "Show all files including hidden files, do not display file detailed attributes",
        "expected_output": {
            "command": "ls -a",
            "explanation": "This command will show all files including hidden files.",
        },
    },
    {
        "prompt": "View the processes of all users and display information such as CPU usage, memory usage, and process status",
        "expected_output": {
            "command": "ps aux",
            "explanation": "This command lists all currently running processes along with details like user, PID, CPU and memory usage.",
        },
    },
    {
        "prompt": "Show me the disk usage of the current directory, Avoid redundant output",
        "expected_output": {
            "command": "du -sh .",
            "explanation": "The 'du' command with '-sh' options shows the total size of the current directory in a human-readable format.",
        },
    },
    {
        "prompt": "Find all files named 'example.txt' in the system",
        "expected_output": {
            "command": "find / -name example.txt 2>/dev/null",
            "explanation": "This command searches the entire file system for files named 'example.txt'. The '2>/dev/null' suppresses permission error messages.",
        },
    },
    {
        "prompt": "Write the command used to display the absolute path of the user's current working directory (the command should have no other functions, only output the path and no redundant information).",
        "expected_output": {
            "command": "pwd",
            "explanation": "The 'pwd' command can view the current working directory (i.e., the current path)",
        },
    },
    {
        "prompt": "Compress the folder 'my_folder' into a zip file",
        "expected_output": {
            "command": "zip -r my_folder.zip my_folder",
            "explanation": "This command compresses the 'my_folder' directory recursively into a zip archive named 'my_folder.zip'.",
        },
    },
    {
        "prompt": "Count the number of lines in 'data.txt'",
        "expected_output": {
            "command": "wc -l data.txt",
            "explanation": "The 'wc -l' command counts the number of lines in the specified file 'data.txt'.",
        },
    },
    {
        "prompt": "Rename file 'old_name.txt' to 'new_name.txt'",
        "expected_output": {
            "command": "mv old_name.txt new_name.txt",
            "explanation": "The 'mv' command is used to rename or move files. In this case, it renames 'old_name.txt' to 'new_name.txt'.",
        },
    },
    {
        "prompt": "Show me the last 10 lines of 'logfile.log'",
        "expected_output": {
            "command": "tail -n 10 logfile.log",
            "explanation": "The 'tail -n 10' command displays the last 10 lines of the specified file 'logfile.log'.",
        },
    },
    {
        "prompt": "Compress the directory 'project' into a tarball named 'project_backup.tar.gz'",
        "expected_output": {
            "command": "tar -czvf project_backup.tar.gz project",
            "explanation": "The 'tar' command creates an archive. The '-c' option creates a new archive, '-z' compresses it with gzip, '-v' shows verbose output, '-f' specifies the filename, and 'project' is the directory to compress."
        }
    }
]
