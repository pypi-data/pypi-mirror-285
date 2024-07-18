from __future__ import annotations

from io import StringIO
from pathlib import Path

import orjson
import serde.json

from drepr.models.resource import ResourceDataString


def read_source_json(infile: Path | str | ResourceDataString):
    if isinstance(infile, ResourceDataString):
        return orjson.loads(infile.as_str())
    return serde.json.deser(infile)
