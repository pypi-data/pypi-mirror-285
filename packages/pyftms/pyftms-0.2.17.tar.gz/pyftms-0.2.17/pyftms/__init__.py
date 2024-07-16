# Copyright 2024, Sergey Dudanov
# SPDX-License-Identifier: Apache-2.0

"""
.. include:: ../README.md
"""

from .client import (
    ControlEvent,
    DeviceInfo,
    FitnessMachine,
    FtmsCallback,
    MachineType,
    MovementDirection,
    NotFitnessMachineError,
    PropertiesManager,
    SettingRange,
    SetupEvent,
    SetupEventData,
    SpinDownEvent,
    SpinDownEventData,
    TrainingStatusEvent,
    TrainingStatusEventData,
    UpdateEvent,
    UpdateEventData,
    get_client,
    get_client_from_address,
    get_machine_type_from_service_data,
)
from .client.backends import FtmsEvents
from .client.machines import CrossTrainer, IndoorBike, Rower, Treadmill
from .models import (
    IndoorBikeSimulationParameters,
    ResultCode,
    SpinDownControlCode,
    SpinDownSpeedData,
    SpinDownStatusCode,
    TrainingStatusCode,
)

__all__ = [
    "get_client",
    "get_client_from_address",
    "get_machine_type_from_service_data",
    "FitnessMachine",
    "CrossTrainer",
    "IndoorBike",
    "Treadmill",
    "Rower",
    "FtmsCallback",
    "FtmsEvents",
    "MachineType",
    "UpdateEvent",
    "SetupEvent",
    "ControlEvent",
    "TrainingStatusEvent",
    "NotFitnessMachineError",
    "SetupEventData",
    "UpdateEventData",
    "TrainingStatusEventData",
    "MovementDirection",
    "IndoorBikeSimulationParameters",
    "DeviceInfo",
    "SettingRange",
    "ResultCode",
    "PropertiesManager",
    "TrainingStatusCode",
    # Spin-Down
    "SpinDownEvent",
    "SpinDownEventData",
    "SpinDownSpeedData",
    "SpinDownControlCode",
    "SpinDownStatusCode",
]
