from typing import Any, Dict, List, Optional, Union
import uuid


class BaseMessage:
    """Base abstract Message class."""

    content: Union[str, List[Union[str, Dict]]]
    type: str
    id: Optional[str] = None

    def __init__(
        self, content: Union[str, List[Union[str, Dict]]], **kwargs: Any
    ) -> None:
        """Pass in content as positional arg."""
        self.content = content
        self.id = str(uuid.uuid4())
