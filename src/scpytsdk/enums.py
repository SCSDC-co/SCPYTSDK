from enum import Enum

class Region(str, Enum):
    AWS_TOKYO    = "aws-ap-northeast-1"
    AWS_MUMBAI   = "aws-ap-south-1"
    AWS_IRELAND  = "aws-eu-west-1"
    AWS_VIRGINIA = "aws-us-east-1"
    AWS_OHIO     = "aws-us-east-2"
    AWS_OREGON   = "aws-us-west-1"

    @classmethod
    def _missing_(cls, value):
        unknown = str.__new__(cls, value)
        unknown._name_ = "UNKNOWN"
        unknown._value_ = value
        return unknown

