# File Server

This project uses the **Socket** library in python as well as **MongoDB** in order to manage a public file system.

Before running the actual code, make sure you have all the libraries installed by running `pip install requirements.txt`. Now you should be able to run **server.py** with no issues.

After launching **server.py**, you can go ahead and run **client.py** which will make you choose wheather you wish to create a new account or log into an existing one.

There are two types of users:
- *default users* - can create/edit/read the files that are marked as public or the files that specifically have the user as one of the collaborators/readers;
- *admins* - have access to any files and can create/edit/read every.

After logging in, try running `help` in order to take a look at the possible commands you can run, or take a look below!

Commands:
- `echo <text>` - sends a text to all the users that are connected to the network;
- `echo <text> >> <file_name>` - creates a document and writes to it;
- `cd <path>` - checks weather you have the necessary rights in order to navigate to that directory;
- `create <repo|file> <name>` - creates a repo/file in your desired destination;
- `set <repo> <collaborators|readers> <name|*>` - adds/removes collaborators/readers from your desired repo;
- `add-admin <user_name>` - creates a new admin account, that will be activated when that user logs in, as it requires them to specify their password;
- `cat <file_name>` - reads a file;
- `cat-database` - reads the users and file-system database;
- `log-out` - makes you be logged in as a guest with virtually no rights;
- `kill` - quits the program.