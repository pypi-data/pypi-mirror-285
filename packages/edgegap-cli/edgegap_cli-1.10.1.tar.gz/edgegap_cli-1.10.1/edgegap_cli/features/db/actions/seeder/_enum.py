from enum import Enum


class OperationEnum(str, Enum):
    CREATE_OR_UPDATE = 'CREATE_OR_UPDATE'
    CREATE_ONLY = 'CREATE_ONLY'
