from typing import Union, List, Dict

# like sublime.Value
Value = Union[bool, str, int, float, List["Value"], Dict[str, "Value"], None]
ProjectId = Union[int, str]  # project id or name with namespace
