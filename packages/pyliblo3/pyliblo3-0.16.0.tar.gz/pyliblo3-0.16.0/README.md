# pyliblo3 

This is a fork of the original bindings for liblo, making it pip installable.

As of version 0.16 it includes liblo itself within the python wheel for all
three desktop platforms. 

## Example


### Simple Server

```python

import pyliblo3 as liblo
server = liblo.Server(8080)

def test_handler(path, args, types, src):
    print(args)
    
server.add_method("/test", None, test_handler)

while True:
    server.recv(100)
```

## Installation


```bash

pip install pyliblo3

```



