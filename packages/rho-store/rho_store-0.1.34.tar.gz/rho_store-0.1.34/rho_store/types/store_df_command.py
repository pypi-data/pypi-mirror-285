from dataclasses import dataclass
from typing import Optional

import pandas as pd


@dataclass(frozen=True)
class StoreDfCommand:
    data: pd.DataFrame
    name: str = None
    table_id: str = None
    strategy: str = None
    merge_options: Optional[dict] = None
    run_async: bool = True


__all__ = ["StoreDfCommand"]
