[![Build Status](https://travis-ci.org/athenian-robotics/distance-tracking.svg?branch=master)](https://travis-ci.org/athenian-robotics/distance-tracking)
[![Code Health](https://landscape.io/github/athenian-robotics/distance-tracking/master/landscape.svg?style=flat)](https://landscape.io/github/athenian-robotics/distance-tracking/master)
[![Code Climate](https://codeclimate.com/github/athenian-robotics/distance-tracking/badges/gpa.svg)](https://codeclimate.com/github/athenian-robotics/distance-tracking)

# Distance Tracking

## Setup

Install Python as described [here](http://docs.python-guide.org/en/latest/starting/install3/osx/).

Install the github repos with:
```bash
$ mkdir ~/git
$ cd ~/git
$ git clone https://github.com/athenian-robotics/common-robotics.git
$ git clone https://github.com/athenian-robotics/distance-tracking.git
```

Install the required python packages with:
```bash
$ cd ~/git/distance-tracking
$ sudo pip3 install -r pip/http-client-requirements.txt 
```

Verify your client is working with:
````bash
$ ./sample_data.py  --url distance_url
````

## Usage
```python
import http_distance_client

with HttpDistanceClient("localhost:8080") as client:
    for j in range(10):
        print(client.value())
```

```python
import http_distance_client

with HttpDistanceClient("localhost:8080") as client:
    for d, j in zip(client.values(), range(10)):
        print(d)
```

### OSX Notes

````bash
$ brew install swagger-codegen
````