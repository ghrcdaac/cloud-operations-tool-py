[![Coverage Status](https://coveralls.io/repos/github/ghrcdaac/cloud-operations-tool-py/badge.svg?branch=main)](https://coveralls.io/github/ghrcdaac/cloud-operations-tool-py?branch=main)
![Build Status](https://github.com/ghrcdaac/cloud-operations-tool-py/actions/workflows/build.yml/badge.svg?branch=main)
![Code Quality Workflow](https://github.com/ghrcdaac/cloud-operations-tool-py/actions/workflows/code-quality.yml/badge.svg?branch=main)
![Code Quality](https://api.codiga.io/project/00000/score/svg)
![Code Grade](https://api.codiga.io/project/00000/status/svg)

<img src="img/pilot.png"
     alt="Markdown Monster icon"
     style="width: 25%; float: left; margin-right: 10px" />
```
 ____        _     ___ _____
|  _ \ _   _| |   / _ \_   _|
| |_) | | | | |  | | | || |
|  __/| |_| | |__| |_| || |
|_|    \__, |_____\___/ |_|
       |___/
```



# Overview 
Python cLoud Operations Tool (PyLOT) is a python command line tool designed to help DAAC operators solve the operations edge cases that can't be solved (or which are difficult/time consuming) using [Cumulus Dashboard](https://github.com/nasa/cumulus-dashboard). 
<br>
Since it is powered by Cumulus-API it will allow the operators to interact with [Cumulus stack](https://github.com/nasa/cumulus), for example to monitor the granules status, run rules, and create and update Cumulus records (collections and/or granules).
In some cases interacting with Cumulus-API via the dashboard is sufficient, but there are some edge cases that require the operator to have a tool that provides more flexibility than a Web-Based application.
<br>
PyLOT can run as a command line tool in your local machine and accept options and respond with JSON. It can also be used as a library for AWS lambda and AWS ECS tasks.
<br>
PyLOT can overcome the limitation of Cumulus-API by monitoring the status of AWS resources (Cloudwatch, SFN, S3...).
<br>
This tool will prevent reinventing the wheel, since a solution for a common problem can be easily shared among all the DAACs (sharing is caring).

## 📖 Documentation

- Release note [v1.0.0](https://ghrcdaac.github.io/cloud-operations-tool-py/#v100).
