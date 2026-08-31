# SCPYTSDK

**Super Cool Python SDK for the [Turso](https://turso.tech) Platform API.**

SCPYTSDK is a lightweight, typed Python wrapper around the Turso Platform API. It handles authentication, and gives you simple methods and dataclasses for managing databases, groups, and database tokens — no raw HTTP calls or JSON wrangling required.

[![PyPI version](https://img.shields.io/pypi/v/scpytsdk.svg)](https://pypi.org/project/scpytsdk/)
[![PyPI Downloads](https://img.shields.io/pypi/dd/SCPYTSDK)](https://pypi.org/project/scpytsdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/SCSDC-co/SCPYTSDK/blob/main/LICENSE)


## Features

- Automatic API key and organization validation on client creation
- Full database lifecycle — create, list, retrieve, delete
- Database auth token creation and rotation, with configurable expiration and access level
- Group management — list, retrieve, delete
- Typed dataclasses (`Database`, `Group`, `DatabaseSeed`, `DatabaseEncryption`) with automatic enum/UUID conversion
- Fully typed, ships with `py.typed`

## Installation

```bash
pip install scpytsdk
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add scpytsdk
```

Requires Python 3.10+.

## Quick Start

```python
from scpytsdk import SCPYTSDK

# Creates and validates a client against the Turso Platform API
sdk = SCPYTSDK(apikey="your-turso-api-key", organization_slug="your-org-slug")

# Create a database
db = sdk.create_db(name="my-new-db", group="default")
print(db.Name, db.Hostname)

# List all databases in the organization
for database in sdk.list_dbs():
    print(database.Name, database.group)

# Create an auth token for a database
token = sdk.create_db_token(db, expiration="2d")
print(token)
```

## Usage

### Creating a client

```python
from scpytsdk import SCPYTSDK

sdk = SCPYTSDK(
    apikey="your-turso-api-key",
    organization_slug="your-org-slug",
    endpoint="https://api.turso.tech",  # optional, this is the default
)
```

On instantiation, the client validates the API key and confirms the organization exists, raising `InvalidApikey` or `InvalidOrganization` immediately if something's wrong — so you find out at startup, not on your first request.

### Databases

**List databases**, optionally filtered by group, schema, or parent database:

```python
sdk.list_dbs()
sdk.list_dbs(group_filter="default")
sdk.list_dbs(parent_filter="my-parent-db")  # accepts a name or a Database object
```

**Retrieve a single database** by name:

```python
db = sdk.retrieve_db("my-db")
```

**Create a database**, optionally as a branch/seed of another database, with a size limit or remote encryption:

```python
from scpytsdk import DatabaseSeed, DatabaseEncryption
from scpytsdk.enums import SeedType, DatabaseEncryptionCipher

db = sdk.create_db(
    name="my-db",
    group="default",
    seed=DatabaseSeed(type=SeedType.DATABASE, name="parent-db"),
    size_limit="1G",
    encryption=DatabaseEncryption(
        encryption_key="base64-encoded-key",
        encryption_cipher=DatabaseEncryptionCipher.AES_256_GCM,
    ),
)
```

**Delete a database** (accepts a name or a `Database` object):

```python
sdk.delete_db("my-db")
```

### Database tokens

**Create a token** for reading/writing to a database:

```python
from scpytsdk.enums import TokenAuthorization

token = sdk.create_db_token(
    "my-db",
    expiration="1w",                              # defaults to "never"
    authorization=TokenAuthorization.READ_ONLY,    # defaults to FULL_ACCESS
)
```

**Rotate (invalidate) all tokens** for a database:

```python
sdk.rotate_db_tokens("my-db")
```

### Groups

```python
groups = sdk.list_groups()
group = sdk.retrieve_group("default")
sdk.delete_group("default")  # accepts a name or a Group object
```

## Reference

### `SCPYTSDK` client methods

| Method | Description |
|---|---|
| `list_dbs(group_filter=None, schema_filter=None, parent_filter=None)` | List databases, optionally filtered |
| `retrieve_db(database)` | Get a single database by name |
| `create_db(name, group="default", seed=None, size_limit=None, encryption=None)` | Create a database |
| `delete_db(database)` | Delete a database |
| `create_db_token(database, expiration=None, authorization=None)` | Create a database auth token (returns a JWT string) |
| `rotate_db_tokens(database)` | Invalidate all tokens for a database |
| `list_groups()` | List all groups in the organization |
| `retrieve_group(group)` | Get a single group by name |
| `delete_group(group)` | Delete a group |

### Data classes (`scpytsdk.classes`)

- **`Database`** — `Name`, `DbId`, `Hostname`, `block_reads`, `block_writes`, `delete_protection`, `regions`, `primaryRegion`, `group`
- **`Group`** — `name`, `version`, `uuid`, `locations`, `primary`, `delete_protection`, `archived`
- **`DatabaseSeed`** — `type`, `name`, `timestamp` (used to branch a database or seed from an upload)
- **`DatabaseEncryption`** — `encryption_key`, `encryption_cipher` (for databases with remote encryption at rest)

### Enums (`scpytsdk.enums`)

- **`Region`** — AWS regions such as `AWS_TOKYO`, `AWS_VIRGINIA`, `AWS_OREGON`, etc.
- **`SeedType`** — `DATABASE`, `DATABASE_UPLOAD`
- **`TokenAuthorization`** — `FULL_ACCESS`, `READ_ONLY`
- **`DatabaseEncryptionCipher`** — `AES_256_GCM`, `AES_128_GCM`, `CHACHA20_POLY1305`, and AEGIS variants

### Exceptions (`scpytsdk.exceptions`)

| Exception | Raised when |
|---|---|
| `InvalidApikey` | The API key is empty or fails validation |
| `InvalidOrganization` | The organization slug is empty or doesn't exist |
| `DatabaseNotFound` | The requested database doesn't exist |
| `DatabaseExists` | Creating a database that already exists |
| `GroupNotFound` | The requested group doesn't exist, or a database's target group is invalid |

## Contributing

Issues and pull requests are welcome at [SCSDC-co/SCPYTSDK](https://github.com/SCSDC-co/SCPYTSDK). This project uses [pre-commit](https://pre-commit.com/) hooks and [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
git clone https://github.com/SCSDC-co/SCPYTSDK.git
cd SCPYTSDK
uv sync
pre-commit install
```

## License

MIT © Francesco Angeloni. See [LICENSE](LICENSE) for details.
