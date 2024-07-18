# Task Track

*A dead-simple command line tool to help you track your time*

## Quickstart
To get started, install task-track:
```
pip install task-track
```
Once installed, task-track will be available on the command line via the `track` command.
To see a quick overview run the help command: 
```
track -h
```
This will display all of the options:
```
usage: track [-h] [-s S] [-x X] [-l]

A dead simple time tracker

optional arguments:
  -h, --help  show this help message and exit
  -s S        start tracking a task: track -s <task_name>
  -x X        stop tracking a task: track -x <task_name>
  -l          list all tasks: track -l
```

For example, if one were to start tracking doing the dishes:
```
$ track -s do_dishes
Task do_dishes has been successfully started
```
and to stop the task:
```
$ track -x do_dishes
Task do_dishes successfully stopped. Session time: 1.2559911688168843 minutes.
To view time spent on tasks, use 'track -l'
```
and finally, to view time spent:
```
$ track -l
Task Name      Time Spent (min)
-----------  ------------------
do_dishes                     1
```

## Leveraging Python Environments
Since task-track saves data local to it's installation, task-track can be downloaded and used in different environments to organize tasks that might need to be tracked separately:
```
python3 -m venv work
python3 -m venv school
```
are a few examples of ways that environments could be used to track different task categories.
