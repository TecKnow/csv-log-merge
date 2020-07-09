# cperkins-csv-log
A utility for combining all the CSV files in a directory.

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
1. At the command line enter **venv\scripts\activate**
1. Your prompt should now have something like _(venv)_ at the beginning of it.
1. Enter **python -m pip install --upgrade pip**
1. Enter **python -m pip install -r requirements.txt**
1. This will download the project's dependencies.
1. Enter "**python -m pip install -e .**"
    1. The (.) second argument is important here. 
1. Enter **python -m pytest**
1. Congratulations.  If there were no errors you should now be ready to work on the project.
1. When you're finished working in the virtual environment, enter **deactivate** to leave it.
