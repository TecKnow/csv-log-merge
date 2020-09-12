# csv-log-merge
This is a command line utility for combining CSV files with a parituclar header.  It supports recursive searches.  Default behavior is specified in a per-user configuration file and can be overriden with command line options.

This project is a useful demonstration of the following Python tools and packages:
*  Python package management using _venv_ and _requirements.txt_
*  Standalone executables using _pyinstaller_
*  Command line argument parsing using _argparse_
*  User-editable configuration files using _configparser_
*  Modern Python file system operations using _pathlib_

## Setting up for development
### Technologies used
To set this project up localy for development work you will need some familiarity with the following tools:
*  _git_ and github
*  _python_ virtual environments with _venv_
* _requirements.txt_ files and _pip_

### Procedure
This procedure assumes that you are working on a Windows machine
1. Make sure that you have _python_ installed and accessible from the command line.
1.  Make sure that you have _git_ installed and accessible from the command line.  You may need to type _python3_ or just _python_.  This procedure will just say _python_.
1.  On the upper right corner of the project's github page linked above there should be a button labeled _Clone_.  Press it and copy the URL provided.  We'll call that the _REPO_PATH_
1.  In a terminal on your local machine with _git_ installed, navigate to the directory where you would like the project to live.
Enter **git clone _REPO_PATH_**.
1.  This should download the repository to your local machine from github.
1.  Navigate into the top level of the repository, it should be a folder called _cperkins-csv-log_.
1. In this directory enter **python -m venv venv**.
1. There will be a short delay.
1. At the command line enter **venv\\scripts\\activate**
1. Your prompt should now have something like _(venv)_ at the beginning of it.
1. Enter **python -m pip install --upgrade pip**
1. Enter **python -m pip install -r requirements.txt**
1. This will download the project's dependencies.
1. Enter "**python -m pip install -e .**"
    1. The (.) second argument is important here. 
1. Enter **python -m pytest**
1. Congratulations.  If there were no errors you should now be ready to work on the project.
1. When you're finished working in the virtual environment, enter **deactivate** to leave it.

## Building the user application
1.  Follow the instructions above and make sure that you're still in the virtual environment.
   1.  Your prompt will have something like (venv) at the beginning of it.
1.  Enter the following command, where _program name_ is the name you would like the executable to have: **pyinstaller --onefile --name <_program_name_> src\\csvlog\\command_line.py**
1.  Quite a bit of output will go scrolling past your terminal.
1.  If the process is sucessful, you will see something like the following:
```
2517 INFO: Appending archive to EXE D:\Users\teckn\PycharmProjects\cperkins\cperkins-csv-log\dist\program_name.exe
2530 INFO: Building EXE from EXE-00.toc completed successfully.
```
1.  To The _EXE_ file in the _dist_ directory is the application.
1.  To see that it worked, enter the following command:  **dist\\<_program_name_>.exe --help**
   1.  You should see the program's help text.


