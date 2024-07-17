# PyFTMS - Python Fitness Machine Service client library

**PyFTMS** is a Python client library for the **FTMS service**, which is a standard for fitness equipment with a Bluetooth interface. **Bleak** is used as the Bluetooth library. Currently four main types of fitness machines are supported:
 1. **Treadmill**
 2. **Cross Trainer** (Elliptical Trainer)
 3. **Rower** (Rowing Machine)
 4. **Indoor Bike** (Spin Bike)

**Step Climber** and **Stair Climber** machines are **not supported** due to incomplete protocol information and low popularity.

## Requirments

1. `python >= 3.11`
2. `bleak >= 0.21.0`
3. `bleak-retry-connector == 3.5.0`

## Install it from PyPI

```bash
pip install pyftms
```

## Usage

Please read API [documentation](https://dudanov.github.io/pyftms/pyftms.html).
