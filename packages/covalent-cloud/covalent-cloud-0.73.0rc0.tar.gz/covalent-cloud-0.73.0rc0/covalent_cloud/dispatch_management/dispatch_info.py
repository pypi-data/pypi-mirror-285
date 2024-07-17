# Copyright 2024 Agnostiq Inc.

from pydantic import BaseModel
from typing import List, Union


class DispatchInfo(BaseModel):
    tags: Union[List[str], None] = None
