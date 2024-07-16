import json
from dataclasses import asdict, dataclass
from typing import Dict, List, Optional, Union


@dataclass
class Folder():
    id: str
    name: str
    parentFolderId: str
    tags: Optional[Dict[str, Union[str, int, bool, None]]] = None


class FolderEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Folder):
            return asdict(obj)
        return super().default(obj)


@dataclass
class Error():
    message: str


@dataclass
class MaximFolderResponse():
    data: Folder
    error: Optional[Error] = None


@dataclass
class MaximFoldersResponse():
    data: List[Folder]
    error: Optional[Error] = None
