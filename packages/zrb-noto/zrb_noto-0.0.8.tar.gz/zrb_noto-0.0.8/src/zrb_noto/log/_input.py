from typing import Any, Mapping
from zrb import StrInput, MultilineInput
from .._config import CURRENT_TIME
from ._helper import get_log_file_name

import datetime
import os


def _get_default_content(input_map: Mapping[str, Any]) -> str:
    date_str = input_map.get("date")
    current_time = datetime.strptime(date_str, "%Y-%m-%d")
    file_name = get_log_file_name(current_time)
    if not os.path.isfile(file_name):
        return ""
    with open(file_name, "r") as f:
        return f.read()


text_input = StrInput(
    name="text",
    shortcut="t",
    prompt="Text",
    default="",
)

date_input = StrInput(
    name="date",
    shortcut="d",
    prompt="Date (Y-m-d)",
    default=CURRENT_TIME.strftime("%Y-%m-%d"),
)

content_input = MultilineInput(
    name="content",
    shortcut="c",
    comment_prefix="<!--",
    comment_suffix="-->",
    extension="md",
    default=_get_default_content
)
