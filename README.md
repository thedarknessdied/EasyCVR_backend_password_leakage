# EasyCVR_backend_password_leakage
EasyCVR Intelligent Edge Gateway userlist Information Disclosure Vulnerability

<img width="527" alt="1697191016867" src="https://github.com/thedarknessdied/EasyCVR_backend_password_leakage/assets/56123966/10122467-45d7-45ac-85bb-df570cfe6ac7">

## Description
EasyCVR intelligent edge gateway is a device based on edge computing and artificial intelligence technology, which aims to provide efficient video monitoring and intelligent analysis solutions. It combines video surveillance cameras, computing power, and network connectivity, enabling on-site video data processing and analysis, reducing reliance on central servers. EasyCVR intelligent edge gateway has userlist information leakage, allowing attackers to directly log in to the backend and perform illegal operations.

## installation
> pip install -r requirements.txt

## Tools Usage
```python
python EasyCVR后台密码泄露.py -h
usage: EasyCVR后台密码泄露.py [-h] (-u URL | -f FILE) [--random-agent RANDOM_AGENT] [--time-out TIME_OUT] [-d DELAY]
                        [-t THREAD] [--proxy PROXY]

NUUO NVR Video Storage Management Device Remote Command Execution

optional arguments:
  -h, --help            show this help message and exit
  -u URL, --url URL     Enter target object
  -f FILE, --file FILE  Input target object file
  --random-agent RANDOM_AGENT
                        Using random user agents
  --time-out TIME_OUT   Set the HTTP access timeout range (setting range from 0 to 5)
  -d DELAY, --delay DELAY
                        Set multi threaded access latency (setting range from 0 to 5)
  -t THREAD, --thread THREAD
                        Set the number of program threads (setting range from 1 to 50)
  --proxy PROXY         Set up HTTP proxy
```
