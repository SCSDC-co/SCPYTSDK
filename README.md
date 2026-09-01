# SCPYTSDK

**Super Cool Python SDK for the [Turso](https://turso.tech) Platform API.**

SCPYTSDK is a lightweight, typed Python wrapper around the Turso Platform API. It handles authentication, and gives you simple methods and dataclasses for managing databases, groups, and database tokens — no raw HTTP calls or JSON wrangling required.

[![PyPI version](https://img.shields.io/pypi/v/scpytsdk.svg)](https://pypi.org/project/scpytsdk/)
[![Python versions](https://img.shields.io/pypi/pyversions/scpytsdk.svg)](https://pypi.org/project/scpytsdk/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/SCSDC-co/SCPYTSDK/blob/main/LICENSE)

## Features

- Automatic API key and organization validation on client creation
- Full database lifecycle — create, list, retrieve, delete
- Upload an existing SQLite database from a file path or a live `sqlite3.Connection` (in-memory or WAL) to seed a new database
- Database auth token creation and rotation, with configurable expiration and access level
- Group management — list, retrieve, delete
- Typed dataclasses (`Database`, `Group`, `DatabaseSeed`, `DatabaseEncryption`) with automatic enum/UUID conversion
- Fully typed

## Installation

```bash
pip install scpytsdk
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add scpytsdk
```

Requires Python 3.11+.

## Quick Start

```python
from scpytsdk import SCPYTSDK

# Creates and validates a client against the Turso Platform API
sdk = SCPYTSDK(apikey="your-turso-api-key", organization_slug="your-org-slug")

# Create a database
db = sdk.db.create(name="my-new-db", group="default")
print(db.Name, db.Hostname)

# List all databases in the organization
for database in sdk.db.list():
    print(database.Name, database.group)

# Create an auth token for a database
token = sdk.db.create_token(db, expiration="2d")
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

Access database methods through `sdk.db`.

**List databases**, optionally filtered by group, schema, or parent database:

```python
sdk.db.list()
sdk.db.list(group_filter="default")
sdk.db.list(parent_filter="my-parent-db")  # accepts a name or a Database object
```

**Retrieve a single database** by name:

```python
db = sdk.db.retrieve("my-db")
```

**Create a database**, optionally as a branch/seed of another database, with a size limit or remote encryption:

```python
from scpytsdk import DatabaseSeed, DatabaseEncryption
from scpytsdk.enums import SeedType, DatabaseEncryptionCipher

db = sdk.db.create(
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
sdk.db.delete("my-db")
```

**Upload a SQLite database.** Create a database with `SeedType.DATABASE_UPLOAD`, then push data into it from a local file or a live `sqlite3.Connection`:

```python
import sqlite3
from scpytsdk import DatabaseSeed
from scpytsdk.enums import SeedType

db = sdk.db.create("my-db", seed=DatabaseSeed(type=SeedType.DATABASE_UPLOAD))

# From a file on disk
sdk.db.upload(db, "local.db")

# From a file-backed connection already in WAL mode
con = sqlite3.connect("local.db")
con.execute("PRAGMA journal_mode=WAL")
sdk.db.upload(db, con)

# From an in-memory connection — converted to a WAL-mode file behind the scenes,
# since Turso's upload endpoint requires journal_mode=WAL and :memory: databases
# can never report WAL mode
mem_con = sqlite3.connect(":memory:")
mem_con.execute("CREATE TABLE t (x)")
sdk.db.upload(db, mem_con)
```

`origin` accepts a path (`str` or `PathLike`) or a `sqlite3.Connection`. Connections are inspected automatically: a WAL-mode connection is serialized directly, an in-memory connection is copied into a temporary WAL-mode file first, and anything else raises `InvalidOriginDatabase`. Pass an `encryption` `DatabaseEncryption` object if the source database uses encryption at rest.

### Database tokens

Access token methods through `sdk.db`.

**Create a token** for reading/writing to a database:

```python
from scpytsdk.enums import TokenAuthorization

token = sdk.db.create_token(
    "my-db",
    expiration="1w",                              # defaults to "never"
    authorization=TokenAuthorization.READ_ONLY,    # defaults to FULL_ACCESS
)
```

**Rotate (invalidate) all tokens** for a database:

```python
sdk.db.rotate_tokens("my-db")
```

### Groups

Access group methods through `sdk.group`.

```python
groups = sdk.group.list()
group = sdk.group.retrieve("default")
sdk.group.delete("default")  # accepts a name or a Group object
```

## Reference

### `sdk.db` methods

| Method | Description |
|---|---|
| `list(group_filter=None, schema_filter=None, parent_filter=None)` | List databases, optionally filtered |
| `retrieve(database)` | Get a single database by name |
| `create(name, group="default", seed=None, size_limit=None, encryption=None)` | Create a database |
| `upload(database, origin, encryption=None)` | Upload a SQLite file or `sqlite3.Connection` to a database seeded with `SeedType.DATABASE_UPLOAD` |
| `delete(database)` | Delete a database |
| `create_token(database, expiration=None, authorization=None)` | Create a database auth token (returns a JWT string) |
| `rotate_tokens(database)` | Invalidate all tokens for a database |

### `sdk.group` methods

| Method | Description |
|---|---|
| `list()` | List all groups in the organization |
| `retrieve(group)` | Get a single group by name |
| `delete(group)` | Delete a group |

### Data classes (`scpytsdk.models`)

- **`Database`** — `Name`, `DbId`, `Hostname`, `block_reads`, `block_writes`, `delete_protection`, `regions`, `primaryRegion`, `group`
- **`Group`** — `name`, `version`, `uuid`, `locations`, `primary`, `delete_protection`, `archived`
- **`DatabaseSeed`** — `type`, `name`, `timestamp` (used to branch a database or seed from an upload)
- **`DatabaseEncryption`** — `encryption_key`, `encryption_cipher` (for databases with remote encryption at rest)

### Enums (`scpytsdk.enums`)

- **`Region`** — AWS regions such as `AWS_TOKYO`, `AWS_VIRGINIA`, `AWS_OREGON`, etc.
- **`SeedType`** — `DATABASE`, `DATABASE_UPLOAD`
- **`TokenAuthorization`** — `FULL_ACCESS`, `READ_ONLY`
- **`DatabaseEncryptionCipher`** — `AES_256_GCM`, `AES_128_GCM`, `CHACHA20_POLY1305`, `AEGIS_128L`, `AEGIS_128_X2`, `AEGIS_128_X4`, `AEGIS_256`, `AEGIS_256_X2`, `AEGIS_256_X4`

### Exceptions (`scpytsdk.exceptions`)

| Exception | Raised when |
|---|---|
| `InvalidApikey` | The API key is empty or fails validation |
| `InvalidOrganization` | The organization slug is empty or doesn't exist |
| `DatabaseNotFound` | The requested database doesn't exist |
| `DatabaseExists` | Creating a database that already exists |
| `GroupNotFound` | The requested group doesn't exist, or a database's target group is invalid |
| `InvalidOriginDatabase` | `upload` was given a connection that's neither WAL nor in-memory, or Turso rejected the upload |

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
