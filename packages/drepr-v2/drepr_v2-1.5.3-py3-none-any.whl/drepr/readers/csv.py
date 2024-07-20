from __future__ import annotations

from io import StringIO
from pathlib import Path

import serde.csv

from drepr.models.resource import ResourceDataString


def read_source_csv(infile: Path | str | ResourceDataString):
    if isinstance(infile, ResourceDataString):
        return serde.csv.deser(StringIO(infile.as_str()))
    return serde.csv.deser(infile)
