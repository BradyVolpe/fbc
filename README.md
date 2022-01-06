# FBC or Full Band Capture
This Python appliction configures enables a cable modem for Full Band Capture (FBC). FBC captures all RF signals on the input of a cable modem

## Overview
This document contains more than just documentation of FBC. Scripts the author has been writing in Perl are now being migrated to Python. Some work has been done to ensure continuity on constomer servers and miminmal impact. For that purpose, only virtual envirmonments will be used when deploying and testing with Python scripts moving forward. This will be required. As part of this, documementaiton for virtual environments (venv) will be part of the README.md files in each repo where such files are provided, such as this, along with theh respective requirements.txt file.

## Dependencies

### CentOS / RHEL 7

    sudo yum install net-snmp-devel
    sudo yum install python-devel
    sudo yum install python3-devel

### Mac OS:

Ensure you have the correct version of NET-SNMP:
    $ snmpget --version
    NET-SNMP version: 5.6.2.1
    EasySNMP requires (I believe) NET-SNMP v5.7 or higher.

After running brew install net-snmp, this updated the version to the following:

    snmpget --version
    NET-SNMP version: 5.9.1

Install Python3 for Mac:
    https://www.python.org/downloads/

Install requirements for Virtual environment:
    

## Virtual Environment and Running the Code
### Linux
    unset PYTHONPATH
    python3 -m venv .venv
    source .venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
        getAndPlotFbcData.py <IPv4 : 1, IPv6 2> <SNMP community string> <cable modem IP address> <filename>
 
 Example:
    python3 getAndPlotFbcData.py 1 public 10.2.4.100 spectra
    
### Mac OS:
    python3 -m venv .venv
	source .venv/bin/activate
    pip install -r requirements.txt
    getAndPlotFbcData.py <IPv4 : 1, IPv6 2> <SNMP community string> <cable modem IP address> <filename>
 
 Example:
    python3 getAndPlotFbcData.py 1 public 10.2.4.100 spectra

## Output
Two files are generated in the local directory if no errors are generated when the script is run. The first file has the same name as the "filename" and is located in the local directory. This is a text file with amplitude and frequency data. The second file has ".html" appended to the filename, such as "spectra.html" and can be opened in a web browser to visualize the FBC data. Examples of both files are included in the repository.

Example html FBC file:
![alt text](https://github.com/BradyVolpe/fbc/blob/main/spectra.html)

## Troubleshooting

### CentOS / RHEL 7 

Issues with Packages in Virtenv
Run:
    printenv

If PYTHONPATH=/usr/lib/python2.7/site-packages/ —> is there then run:
	unset PYTHONPATH

### Mac OS

If you don't have the correct version of NET-SNMP you will get the following error when trying to install easysnmp:

    from easysnmp import Session
    session = Session(hostname='localhost', community='public', version=2)

This results in an error message as follows:
  
    $ python test.py 
    Traceback (most recent call last):
    File "/Users/me/python_utsc/test.py", line 9, in <module>
    session = Session(hostname='localhost', community='public', version=2)
    File "/Users/me/python_utsc/.venv/lib/python3.9/site-packages/easysnmp/session.py", line 280, in   __init__
    self.sess_ptr = interface.session(
    NameError: name 'interface' is not defined

This occurs because easysnnmp requires NET-SNMP version 5.7 or higher. You can test as follows:

    $ snmpget --version
    NET-SNMP version: 5.6.2.1

To upgrade on Mac, just run:
    
    brew install net-snmp

Then your version of NET-SNMP should 5.7 or higher after checking:

    snmpget --version
    NET-SNMP version: 5.9.1
