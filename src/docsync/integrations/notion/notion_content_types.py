# notion_content_types.py
import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Union


@dataclass
class NotionBlock:
    '''Bloco base do Notion'''
    type: str
    content: str
    metadata: Dict = None

@dataclass
class NotionHeading(NotionBlock):
    '''Cabeçalho do Notion'''
    level: int = 1
    
    @classmethod
    def from_markdown(cls, content: str) -> 'NotionHeading':
        level = len(re.match(r'^#+', content).group())
        text = content.lstrip('#').strip()
        return cls(type='heading', content=text, level=level)
    
    def to_markdown(self) -> str:
        return f"{'#' * self.level} {self.content}"
    
    def to_notion_block(self) -> Dict:
        return {
            'type': f'heading_{self.level}',
            f'heading_{self.level}': {
                'rich_text': [{
                    'type': 'text',
                    'text': {'content': self.content}
                }]
            }
        }

@dataclass
class NotionCodeBlock(NotionBlock):
    '''Bloco de código do Notion'''
    language: str = 'plain_text'
    
    @classmethod
    def from_markdown(cls, content: str, language: str = None) -> 'NotionCodeBlock':
        if language and language.startswith('`'):
            language = language[3:]
        return cls(
            type='code',
            content=content,
            language=language or 'plain_text'
        )
    
    def to_markdown(self) -> str:
        return f'`{self.language}\\n{self.content}\\n`'
    
    def to_notion_block(self) -> Dict:
        return {
            'type': 'code',
            'code': {
                'rich_text': [{
                    'type': 'text',
                    'text': {'content': self.content}
                }],
                'language': self.language
            }
        }

@dataclass
class NotionCallout(NotionBlock):
    '''Bloco de destaque do Notion'''
    icon: str = '💡'
    
    def to_notion_block(self) -> Dict:
        return {
            'type': 'callout',
            'callout': {
                'rich_text': [{
                    'type': 'text',
                    'text': {'content': self.content}
                }],
                'icon': {'emoji': self.icon}
            }
        }

@dataclass
class NotionTable(NotionBlock):
    '''Tabela do Notion'''
    headers: List[str]
    rows: List[List[str]]
    
    @classmethod
    def from_markdown(cls, content: str) -> 'NotionTable':
        lines = content.strip().split('\\n')
        headers = [cell.strip() for cell in lines[0].split('|')[1:-1]]
        rows = [
            [cell.strip() for cell in line.split('|')[1:-1]]
            for line in lines[2:]  # Skip header and separator
        ]
        return cls(type='table', content='', headers=headers, rows=rows)
    
    def to_markdown(self) -> str:
        header = f"| {' | '.join(self.headers)} |"
        separator = f"|{'---|' * len(self.headers)}"
        rows = ['| ' + ' | '.join(row) + ' |' for row in self.rows]
        return '\n'.join([header, separator] + rows)
    
    def to_notion_block(self) -> Dict:
        return {
            'type': 'table',
            'table': {
                'table_width': len(self.headers),
                'has_column_header': True,
                'has_row_header': False,
                'rows': [
                    [{'type': 'text', 'text': {'content': cell}} for cell in row]
                    for row in [self.headers] + self.rows
                ]
            }
        }

class NotionContentConverter:
    '''Conversor de conteúdo entre Markdown e Notion'''
    
    @staticmethod
    def markdown_to_blocks(markdown: str) -> List[NotionBlock]:
        '''Converte markdown para blocos do Notion'''
        blocks = []
        lines = markdown.split('\\n')
        i = 0
        
        while i < len(lines):
            line = lines[i].strip()
            
            if not line:
                i += 1
                continue
                
            # Heading
            if line.startswith('#'):
                blocks.append(NotionHeading.from_markdown(line))
                i += 1
                
            # Code block
            elif line.startswith('`'):
                code_lines = []
                language = line[3:]
                i += 1
                while i < len(lines) and not lines[i].strip().startswith('`'):
                    code_lines.append(lines[i])
                    i += 1
                blocks.append(NotionCodeBlock.from_markdown(
                    '\\n'.join(code_lines),
                    language
                ))
                i += 1
                
            # Table
            elif line.startswith('|'):
                table_lines = []
                while i < len(lines) and lines[i].strip().startswith('|'):
                    table_lines.append(lines[i])
                    i += 1
                blocks.append(NotionTable.from_markdown('\\n'.join(table_lines)))
                
            # Regular paragraph
            else:
                paragraph = []
                while i < len(lines) and lines[i].strip() and not lines[i].strip().startswith(('#', '`', '|')):
                    paragraph.append(lines[i])
                    i += 1
                blocks.append(NotionBlock(
                    type='paragraph',
                    content='\\n'.join(paragraph)
                ))
                
        return blocks
    
    @staticmethod
    def blocks_to_markdown(blocks: List[NotionBlock]) -> str:
        '''Converte blocos do Notion para markdown'''
        markdown_parts = []
        
        for block in blocks:
            if isinstance(block, (NotionHeading, NotionCodeBlock, NotionTable)):
                markdown_parts.append(block.to_markdown())
            else:
                markdown_parts.append(block.content)
            markdown_parts.append('')  # Empty line between blocks
            
        return '\\n'.join(markdown_parts)
    
    @staticmethod
    def blocks_to_notion(blocks: List[NotionBlock]) -> List[Dict]:
        '''Converte blocos para formato da API do Notion'''
        notion_blocks = []
        
        for block in blocks:
            if isinstance(block, (NotionHeading, NotionCodeBlock, NotionTable, NotionCallout)):
                notion_blocks.append(block.to_notion_block())
            else:
                notion_blocks.append({
                    'type': 'paragraph',
                    'paragraph': {
                        'rich_text': [{
                            'type': 'text',
                            'text': {'content': block.content}
                        }]
                    }
                })
                
        return notion_blocks

# Exemplo de uso:
if __name__ == '__main__':
    markdown_example = '''# Título do Documento

Este é um parágrafo de exemplo com algumas informações importantes.

## Seção de Código

`python
def hello_world():
    print('Hello from DOCSYNC!')
`

## Tabela de Exemplo

| Nome | Idade | Profissão |
|------|-------|-----------|
| João | 30    | Dev       |
| Maria| 28    | Designer  |
'''

    # Converter markdown para blocos
    converter = NotionContentConverter()
    blocks = converter.markdown_to_blocks(markdown_example)
    
    # Converter blocos para formato do Notion
    notion_blocks = converter.blocks_to_notion(blocks)
    
    # Imprimir resultado
    print('Blocos do Notion:')
    print(json.dumps(notion_blocks, indent=2))
