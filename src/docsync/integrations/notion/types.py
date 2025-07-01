"""
DOCSYNC Notion Types
===================

Definições de tipos e classes para integração com a API do Notion.

Classes
-------
NotionObject: Classe base para objetos Notion
NotionBlock: Representa um bloco de conteúdo
NotionPage: Representa uma página
NotionDatabase: Representa um banco de dados
NotionError: Classes de erro

Enums
-----
NotionObjectType: Tipos de objetos do Notion
BlockType: Tipos de blocos suportados
PropertyType: Tipos de propriedades
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class NotionObjectType(Enum):
    """Tipos de objetos do Notion"""

    PAGE = "page"
    DATABASE = "database"
    BLOCK = "block"
    USER = "user"
    COMMENT = "comment"


class BlockType(Enum):
    """Tipos de blocos suportados"""

    PARAGRAPH = "paragraph"
    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    BULLETED_LIST = "bulleted_list_item"
    NUMBERED_LIST = "numbered_list_item"
    TO_DO = "to_do"
    TOGGLE = "toggle"
    CODE = "code"
    QUOTE = "quote"
    CALLOUT = "callout"
    DIVIDER = "divider"
    IMAGE = "image"
    FILE = "file"
    BOOKMARK = "bookmark"
    CHILD_PAGE = "child_page"
    CHILD_DATABASE = "child_database"


class PropertyType(Enum):
    """Tipos de propriedades do Notion"""

    TITLE = "title"
    RICH_TEXT = "rich_text"
    NUMBER = "number"
    SELECT = "select"
    MULTI_SELECT = "multi_select"
    DATE = "date"
    FORMULA = "formula"
    RELATION = "relation"
    ROLLUP = "rollup"
    PEOPLE = "people"
    FILES = "files"
    CHECKBOX = "checkbox"
    URL = "url"
    EMAIL = "email"
    PHONE_NUMBER = "phone_number"
    CREATED_TIME = "created_time"
    CREATED_BY = "created_by"
    LAST_EDITED_TIME = "last_edited_time"
    LAST_EDITED_BY = "last_edited_by"


@dataclass
class RichText:
    """Representa texto rico do Notion"""

    content: str
    type: str = "text"
    annotations: Dict[str, bool] = field(
        default_factory=lambda: {
            "bold": False,
            "italic": False,
            "strikethrough": False,
            "underline": False,
            "code": False,
            "color": "default",
        }
    )
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário no formato da API"""
        return {
            "type": self.type,
            "text": {
                "content": self.content,
                **({"url": self.url} if self.url else {}),
            },
            "annotations": self.annotations,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RichText":
        """Cria objeto a partir de dicionário da API"""
        return cls(
            content=data["text"]["content"],
            type=data["type"],
            annotations=data.get("annotations", {}),
            url=data["text"].get("url"),
        )


class NotionObject:
    """Classe base para objetos Notion"""

    id: str
    type: NotionObjectType
    created_time: datetime
    last_edited_time: datetime
    created_by: Optional[Dict[str, Any]]
    last_edited_by: Optional[Dict[str, Any]]
    archived: bool

    def __init__(
        self,
        id: str,
        type: NotionObjectType = NotionObjectType.BLOCK,
        created_time: Optional[datetime] = None,
        last_edited_time: Optional[datetime] = None,
        created_by: Optional[Dict[str, Any]] = None,
        last_edited_by: Optional[Dict[str, Any]] = None,
        archived: bool = False,
    ):
        self.id = id
        self.type = type
        self.created_time = created_time or datetime.now()
        self.last_edited_time = last_edited_time or datetime.now()
        self.created_by = created_by
        self.last_edited_by = last_edited_by
        self.archived = archived

    def to_dict(self) -> Dict[str, Any]:
        """Converte objeto para dicionário"""
        return {
            "id": self.id,
            "type": self.type.value,
            "created_time": self.created_time.isoformat(),
            "last_edited_time": self.last_edited_time.isoformat(),
            "created_by": self.created_by,
            "last_edited_by": self.last_edited_by,
            "archived": self.archived,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NotionObject":
        """Cria objeto a partir de dicionário"""
        return cls(
            id=data["id"],
            type=NotionObjectType(data["type"]),
            created_time=datetime.fromisoformat(
                data["created_time"].replace("Z", "+00:00")
            ),
            last_edited_time=datetime.fromisoformat(
                data["last_edited_time"].replace("Z", "+00:00")
            ),
            created_by=data.get("created_by"),
            last_edited_by=data.get("last_edited_by"),
            archived=data.get("archived", False),
        )


class NotionBlock(NotionObject):
    """Representa um bloco de conteúdo"""

    block_type: BlockType
    content: Dict[str, Any]
    has_children: bool
    children: List["NotionBlock"]

    def __init__(
        self,
        id: str,
        block_type: BlockType,
        content: Dict[str, Any],
        type: NotionObjectType = NotionObjectType.BLOCK,
        created_time: Optional[datetime] = None,
        last_edited_time: Optional[datetime] = None,
        created_by: Optional[Dict[str, Any]] = None,
        last_edited_by: Optional[Dict[str, Any]] = None,
        archived: bool = False,
        has_children: bool = False,
        children: Optional[List["NotionBlock"]] = None,
    ):
        super().__init__(
            id=id,
            type=type,
            created_time=created_time,
            last_edited_time=last_edited_time,
            created_by=created_by,
            last_edited_by=last_edited_by,
            archived=archived,
        )
        self.block_type = block_type
        self.content = content
        self.has_children = has_children
        self.children = children or []

    def to_dict(self) -> Dict[str, Any]:
        """Converte bloco para dicionário"""
        data = super().to_dict()
        data.update(
            {
                "type": self.block_type.value,
                self.block_type.value: self.content,
                "has_children": self.has_children,
            }
        )
        if self.children:
            data["children"] = [child.to_dict() for child in self.children]
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "NotionBlock":
        """Cria bloco a partir de dicionário"""
        # Extrair campos específicos do bloco
        block_type = BlockType(data["type"])
        content = data[block_type.value]
        children = []
        if data.get("has_children") and data.get("children"):
            children = [cls.from_dict(child) for child in data["children"]]

        # Criar nova instância
        return cls(
            id=data["id"],
            type=NotionObjectType(data["type"]),
            created_time=datetime.fromisoformat(
                data["created_time"].replace("Z", "+00:00")
            ),
            last_edited_time=datetime.fromisoformat(
                data["last_edited_time"].replace("Z", "+00:00")
            ),
            created_by=data.get("created_by"),
            last_edited_by=data.get("last_edited_by"),
            archived=data.get("archived", False),
            block_type=block_type,
            content=content,
            has_children=data.get("has_children", False),
            children=children,
        )

    def to_markdown(self) -> str:
        """Converte bloco para markdown"""
        if self.block_type == BlockType.PARAGRAPH:
            return self._rich_text_to_markdown(self.content.get("rich_text", []))
        elif self.block_type == BlockType.HEADING_1:
            return (
                f"# {self._rich_text_to_markdown(self.content.get('rich_text', []))}\n"
            )
        elif self.block_type == BlockType.HEADING_2:
            return (
                f"## {self._rich_text_to_markdown(self.content.get('rich_text', []))}\n"
            )
        elif self.block_type == BlockType.HEADING_3:
            return f"### {self._rich_text_to_markdown(self.content.get('rich_text', []))}\n"
        elif self.block_type == BlockType.CODE:
            language = self.content.get("language", "")
            code = self._rich_text_to_markdown(self.content.get("rich_text", []))
            return f"```{language}\n{code}\n```\n"
        elif self.block_type == BlockType.BULLETED_LIST:
            return (
                f"- {self._rich_text_to_markdown(self.content.get('rich_text', []))}\n"
            )
        elif self.block_type == BlockType.NUMBERED_LIST:
            return (
                f"1. {self._rich_text_to_markdown(self.content.get('rich_text', []))}\n"
            )
        elif self.block_type == BlockType.QUOTE:
            return (
                f"> {self._rich_text_to_markdown(self.content.get('rich_text', []))}\n"
            )
        elif self.block_type == BlockType.DIVIDER:
            return "---\n"
        elif self.block_type == BlockType.TO_DO:
            checked = self.content.get("checked", False)
            mark = "x" if checked else " "
            return f"- [{mark}] {self._rich_text_to_markdown(self.content.get('rich_text', []))}\n"
        return ""

    @staticmethod
    def _rich_text_to_markdown(rich_text: List[Dict[str, Any]]) -> str:
        """Converte rich text para markdown"""
        result = ""
        for text in rich_text:
            content = text.get("text", {}).get("content", "")
            annotations = text.get("annotations", {})

            if annotations.get("bold"):
                content = f"**{content}**"
            if annotations.get("italic"):
                content = f"_{content}_"
            if annotations.get("strikethrough"):
                content = f"~~{content}~~"
            if annotations.get("code"):
                content = f"`{content}`"

            result += content

        return result


@dataclass
class NotionPage(NotionObject):
    """Representa uma página no Notion"""

    title: str
    parent: Dict[str, Any]
    properties: Dict[str, Any]
    blocks: List[NotionBlock] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converte página para dicionário"""
        data = super().to_dict()
        data.update({"parent": self.parent, "properties": self.properties})
        if self.blocks:
            data["children"] = [block.to_dict() for block in self.blocks]
        return data


@dataclass
class NotionDatabase(NotionObject):
    """Representa um banco de dados no Notion"""

    title: str
    description: Optional[str]
    properties: Dict[str, Any]
    pages: List[NotionPage] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Converte database para dicionário"""
        data = super().to_dict()
        data.update(
            {
                "title": self.title,
                "description": self.description,
                "properties": self.properties,
            }
        )
        return data


class NotionError(Exception):
    """Erro base para operações Notion"""

    def __init__(self, message: str, code: Optional[str] = None):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotionAuthError(NotionError):
    """Erro de autenticação"""


class NotionRateLimitError(NotionError):
    """Erro de limite de taxa"""

    def __init__(self, retry_after: int):
        self.retry_after = retry_after
        super().__init__(f"Rate limit exceeded. Retry after {retry_after} seconds")


class NotionValidationError(NotionError):
    """Erro de validação"""


class NotionSyncError(NotionError):
    """Erro de sincronização"""


# -----------------------------------------------------------------------------
# Constantes e Configurações
# -----------------------------------------------------------------------------

# Configurações de API
API_VERSION = "2022-06-28"
DEFAULT_CACHE_TTL = 3600  # 1 hora
DEFAULT_BATCH_SIZE = 100

# Ícones padrão
DEFAULT_PAGE_ICON = "📄"
DEFAULT_DATABASE_ICON = "📚"

# Configurações de formatação
ANNOTATION_DEFAULTS = {
    "bold": False,
    "italic": False,
    "strikethrough": False,
    "underline": False,
    "code": False,
    "color": "default",
}

# Tipos de propriedades padrão
DEFAULT_PROPERTIES = {
    "title": {"title": {}},
    "rich_text": {"rich_text": {}},
    "number": {"number": {"format": "number"}},
    "select": {"select": {"options": []}},
    "multi_select": {"multi_select": {"options": []}},
    "date": {"date": {}},
    "checkbox": {"checkbox": {}},
}

# Mapeamento de marcadores Markdown para tipos de bloco
MARKDOWN_BLOCK_MARKERS = {
    "#": BlockType.HEADING_1,
    "##": BlockType.HEADING_2,
    "###": BlockType.HEADING_3,
    "-": BlockType.BULLETED_LIST,
    "*": BlockType.BULLETED_LIST,
    "1.": BlockType.NUMBERED_LIST,
    ">": BlockType.QUOTE,
    "```": BlockType.CODE,
    "---": BlockType.DIVIDER,
    "- [ ]": BlockType.TO_DO,
    "- [x]": BlockType.TO_DO,
}
