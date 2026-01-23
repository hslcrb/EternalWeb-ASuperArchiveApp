"""UUID7 compatibility layer for Python 3.13+

Python 3.14+ has native uuid7 support. For Python 3.13, we use uuid_extensions.
"""

import sys

if sys.version_info >= (3, 14):
    from uuid import uuid7
else:
    try:
        from uuid_extensions import uuid7
    except ImportError:
        try:
            from uuid6 import uuid7
        except ImportError:
            raise ImportError(
                "uuid_extensions or uuid6 package is required for Python <3.14. "
                "Install it with: pip install uuid6"
            )

__all__ = ['uuid7']
