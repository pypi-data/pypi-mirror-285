"""
A place to store metamenus' custom types
"""
from typing import Dict
from typing import NewType

MenuName   = NewType('MenuName', str)
MethodName = NewType('MethodName', str)

CustomMethods = NewType('CustomMethods', Dict[MenuName, MethodName])
