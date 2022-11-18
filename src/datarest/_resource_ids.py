# support for different resource IDs

import enum
from base64 import b64encode
from hashlib import md5, sha256
from uuid import uuid4


@enum.unique
class IdEnum(str, enum.Enum):
    """Enumeration of REST resource ID types.
    
    biz_key: Use an existing primary key as-is (must be a number type if a
        create endpoint is exposed, must not be a composite primary key)
    biz_key_composite: Add concatenated primary key fields as single field ID
    biz_hash_md5: Add md5-hashed concatenated primary key fields as single
        field ID
    biz_hash_sha256: Add sha256-hashed concatenated primary key fields as single
        field ID
    uuid4_base64: Add a URL-safe base64 encoded UUID v4 id
    """
    biz_key = 'biz_key'
    biz_key_composite = 'biz_key_composite'
    biz_hash_md5 = 'biz_hash_md5'
    biz_hash_sha256 = 'biz_hash_sha256'
    uuid4_base64 = 'uuid4_base64'
    # TODO:
    # uuid4_base58 = 'uuid4_base58'  # uuid4 base58 encoded
    # (see e.g. https://www.skitoy.com/p/base58-unique-ids/638/)
    #
    # base64 = 'base64'
    # base58 = 'base58'
    # (a random auto-generated number in base64/base58 number representation,
    # see e.g. https://henvic.dev/posts/uuid/)

    def __str__(self):
        # Avoid IdEnum.xxx output of Enum class, provide actual string value
        return self.value


# TODO: Refactor create_id_default, the *_id generation functions and the
# stuff in _dataresoure_tools into some class-base approach, i.e. a class that
# provices both the dispatch to the ID func implementations and the resource
# transform step(?)
#
# Or maybe better: Instead of the simple {id_type: id_func}-dict create a
# registry class that provides an @register(id_type) decorator to hook the
# *_id(...) functions for dispatching

def biz_key_composite_id(*fields, concat_sep='.'):
    """Return fields concatenated with separator concat_set.
    """
    return concat_sep.join(str(field) for field in fields)


def biz_hash_md5_id(*fields, concat_sep='.'):
    """Return md5 hash hexdigest of fields concatenated with separator
    concat_set.
    """
    return md5(
        concat_sep.join(str(field) for field in fields).encode('utf8')
        ).hexdigest()
 

def biz_hash_sha256_id(*fields, concat_sep='.'):
    """Return sha256 hash hexdigest of fields concatenated with separator
    concat_set.
    """
    return sha256(
        concat_sep.join(str(field).strip() for field in fields).encode('utf8')
        ).hexdigest()


def uuid4_base64_id(*fields, concat_sep='.'):
    """Return a str containing a URL-safe base64-encoded uuid4 representation, 
    without trailing '=='.
    """
    return b64encode(uuid4().bytes, altchars=b'_-').decode()[:-2]


# Map id types to id-generating functions
id_type_funcs = {
    IdEnum.biz_key: None,
    IdEnum.biz_key_composite: biz_key_composite_id,
    IdEnum.biz_hash_md5: biz_hash_md5_id,
    IdEnum.biz_hash_sha256: biz_hash_sha256_id,
    IdEnum.uuid4_base64: uuid4_base64_id,
    }


def create_id_default(
        id_type: IdEnum,
        primary_key=(),
        concat_sep='.'):
    """Return an SQLAlchemy column default function for a the primary key ID
    column.
    """
    id_func = id_type_funcs[id_type]
    if id_func is None:
        # let the database handle id creation
        id_ = None
        return id_
    else:
        def id_(context):
            # a function to create the resource id as a single field composite
            # biz key
            data = context.current_parameters
            fields = (data[pk_field_name] for pk_field_name in primary_key)
            return id_func(*fields, concat_sep=concat_sep)
        return id_

    raise ValueError(f'Id type {id_type} is not supported')
