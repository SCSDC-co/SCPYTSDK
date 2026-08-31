from enum import Enum


class Region(str, Enum):
    AWS_TOKYO = "aws-ap-northeast-1"
    AWS_MUMBAI = "aws-ap-south-1"
    AWS_IRELAND = "aws-eu-west-1"
    AWS_VIRGINIA = "aws-us-east-1"
    AWS_OHIO = "aws-us-east-2"
    AWS_OREGON = "aws-us-west-1"

    @classmethod
    def _missing_(cls, value):
        unknown = str.__new__(cls, value)
        unknown._name_ = "UNKNOWN"
        unknown._value_ = value
        return unknown


class SeedType(str, Enum):
    DATABASE = "database"
    DATABASE_UPLOAD = "database_upload"


class TokenAuthorization(str, Enum):
    FULL_ACCESS = "full-access"
    READ_ONLY = "read-only"


class DatabaseEncryptionCipher(str, Enum):
    AES_256_GCM = "aes256gcm"
    AES_128_GCM = "aes128gcm"
    CHACHA20_POLY1305 = "chacha20poly1305"
    AEGIS_128L = "aegis128l"
    AEGIS_128_X2 = "aegis128x2"
    AEGIS_128_X4 = "aegis128x4"
    AEGIS_256 = "aegis256"
    AEGIS_256_X2 = "aegis256x2"
    AEGIS_256_X4 = "aegis256x4"
