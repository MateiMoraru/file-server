# File Server

This project utilizes the **Socket** library in Python along with **MongoDB** to manage a public file system.

Before executing the code, ensure all required libraries are installed by running `pip install requirements.txt`. Subsequently, run **server.py** without encountering any issues.

Upon launching **server.py**, proceed to run **client.py**, prompting you to either create a new account or log into an existing one.

There are two user types:
- *Default users:* Can create/edit/read files marked as public or files with the user as a collaborator/reader.
- *Admins:* Have access to all files and can create/edit/read any.

After logging in, try the `help` command to view possible commands or refer below.

Commands:
- `echo <text>` - sends a text to all connected users.
- `echo <text> >> <file_name>` - creates a document and writes to it.
- `cd <path>` - checks if you have the necessary rights to navigate to that directory.
- `ls` - lists directories and files in the current working directory.
- `send-file <file_name/s>` - sends and saves files in your working directory.
- `get-file <file_name/s>` - downloads and saves files in a new directory "Downloads".
- `create <repo|file> <name>` - creates a repo/file in your desired destination.
- `set <repo> <collaborators|readers> <name|*>` - adds/removes collaborators/readers from your desired repo.
- `add-admin <user_name>` - creates a new admin account, activated upon specifying a password during login.
- `cat <file_name>` - reads a file.
- `cat-database` - reads the users and file-system database.
- `log-out` - logs in as a guest with limited rights.
- `kill` - quits the program.
