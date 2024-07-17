from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import pandas


@dataclass
class RealtimeContext:
    request_timestamp: Optional[datetime] = None

    def to_pandas(self) -> pandas.DataFrame:
        return pandas.DataFrame({"request_timestamp": [self.request_timestamp]})
