# Fourier_dhx.sdk

This repository provides a guidance for Fourier Dexterous Hand SDK python package. VERSION : "0.0.0.1".
We provide a sdk that can control Fourier Dexterous Hand and Inspire Hand.

### Getting Started
```
pip install fourier-dhx
```

### Use
```
from fourier_dhx.sdk.DexHand import *

if __name__ == "__main__":
    ip = "192.168.137.39"
    dexhand = DexHand(ip)
    dexhand.calibration()
    time.sleep(0.1)
    dexhand.set_angle(0, [10, 10, 10, 10, 5, 10]) # set hand close angles
    time.sleep(1)
    angle = dexhand.get_angle() # get hand angles
    print(angle)
    time.sleep(0.1)
    dexhand.set_angle(0, [0, 0, 0, 0, 0, 0]) # set hand open angles
```

