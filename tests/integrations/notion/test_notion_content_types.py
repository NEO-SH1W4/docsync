# test_notion_content_types.py
import pytest

from docsync.integrations.notion.notion_content_types import (
    NotionBlock,
    NotionCallout,
    NotionCodeBlock,
    NotionContentConverter,
    NotionHeading,
    NotionTable,
)


# Fixtures para testes
@pytest.fixture
def sample_markdown():
    return '''# Título Principal

Este é um parágrafo de exemplo com algumas informações importantes.

## Seção de Código

`python
def hello_world():
    print('Hello from DOCSYNC!')
`

### Subseção

| Nome  | Idade | Profissão |
|-------|-------|-----------|
| João  | 30    | Dev       |
| Maria | 28    | Designer  |
'''

@pytest.fixture
def sample_blocks():
    return [
        NotionHeading(type='heading', content='Título Principal', level=1),
        NotionBlock(
            type='paragraph',
            content='Este é um parágrafo de exemplo com algumas informações importantes.'
        ),
        NotionHeading(type='heading', content='Seção de Código', level=2),
        NotionCodeBlock(
            type='code',
            content='def hello_world():\\n    print(\\'Hello from DOCSYNC!\\')',
            language='python'
        ),
        NotionHeading(type='heading', content='Subseção', level=3),
        NotionTable(
            type='table',
            content='',
            headers=['Nome', 'Idade', 'Profissão'],
            rows=[
                ['João', '30', 'Dev'],
                ['Maria', '28', 'Designer']
            ]
        )
    ]

def test_heading_from_markdown():
    '''Testa conversão de cabeçalho markdown para NotionHeading'''
    markdown = '## Título de Teste'
    heading = NotionHeading.from_markdown(markdown)
    
    assert heading.type == 'heading'
    assert heading.content == 'Título de Teste'
    assert heading.level == 2

def test_heading_to_markdown():
    '''Testa conversão de NotionHeading para markdown'''
    heading = NotionHeading(type='heading', content='Título de Teste', level=2)
    markdown = heading.to_markdown()
    
    assert markdown == '## Título de Teste'

def test_code_block_from_markdown():
    '''Testa conversão de bloco de código markdown para NotionCodeBlock'''
    code = '''`python
def test():
    pass
`'''
    block = NotionCodeBlock.from_markdown('def test():\\n    pass', 'python')
    
    assert block.type == 'code'
    assert block.language == 'python'
    assert 'def test():' in block.content

def test_code_block_to_notion():
    '''Testa conversão de NotionCodeBlock para formato da API do Notion'''
    block = NotionCodeBlock(
        type='code',
        content='print(\\'test\\')',
        language='python'
    )
    notion_block = block.to_notion_block()
    
    assert notion_block['type'] == 'code'
    assert notion_block['code']['language'] == 'python'
    assert notion_block['code']['rich_text'][0]['text']['content'] == 'print(\\'test\\')'

def test_table_from_markdown():
    '''Testa conversão de tabela markdown para NotionTable'''
    markdown = '''| A | B |
|---|---|
| 1 | 2 |
| 3 | 4 |'''
    
    table = NotionTable.from_markdown(markdown)
    
    assert table.headers == ['A', 'B']
    assert table.rows == [['1', '2'], ['3', '4']]

def test_table_to_notion():
    '''Testa conversão de NotionTable para formato da API do Notion'''
    table = NotionTable(
        type='table',
        content='',
        headers=['A', 'B'],
        rows=[['1', '2'], ['3', '4']]
    )
    notion_block = table.to_notion_block()
    
    assert notion_block['type'] == 'table'
    assert notion_block['table']['table_width'] == 2
    assert notion_block['table']['has_column_header'] == True

def test_content_converter_markdown_to_blocks(sample_markdown):
    '''Testa conversão completa de markdown para blocos do Notion'''
    converter = NotionContentConverter()
    blocks = converter.markdown_to_blocks(sample_markdown)
    
    assert len(blocks) > 0
    assert isinstance(blocks[0], NotionHeading)
    assert blocks[0].level == 1
    assert isinstance(blocks[3], NotionCodeBlock)
    assert blocks[3].language == 'python'

def test_content_converter_blocks_to_notion(sample_blocks):
    '''Testa conversão de blocos para formato da API do Notion'''
    converter = NotionContentConverter()
    notion_blocks = converter.blocks_to_notion(sample_blocks)
    
    assert len(notion_blocks) == len(sample_blocks)
    assert notion_blocks[0]['type'] == 'heading_1'
    assert notion_blocks[3]['type'] == 'code'
    assert notion_blocks[5]['type'] == 'table'

def test_content_converter_roundtrip(sample_markdown):
    '''Testa conversão de ida e volta (markdown -> blocos -> markdown)'''
    converter = NotionContentConverter()
    blocks = converter.markdown_to_blocks(sample_markdown)
    markdown_result = converter.blocks_to_markdown(blocks)
    
    # Normalizar strings para comparação
    def normalize(s): return '\\n'.join(line.strip() for line in s.split('\\n') if line.strip())
    
    assert normalize(markdown_result) == normalize(sample_markdown)

def test_callout_block():
    '''Testa bloco de callout do Notion'''
    callout = NotionCallout(
        type='callout',
        content='Informação importante!',
        icon='💡'
    )
    notion_block = callout.to_notion_block()
    
    assert notion_block['type'] == 'callout'
    assert notion_block['callout']['icon']['emoji'] == '💡'
    assert notion_block['callout']['rich_text'][0]['text']['content'] == 'Informação importante!'

def test_complex_content_structure(sample_markdown):
    '''Testa estrutura complexa de conteúdo'''
    converter = NotionContentConverter()
    blocks = converter.markdown_to_blocks(sample_markdown)
    notion_blocks = converter.blocks_to_notion(blocks)
    
    # Verificar estrutura completa
    assert len(notion_blocks) > 0
    
    # Verificar hierarquia de cabeçalhos
    headers = [b for b in blocks if isinstance(b, NotionHeading)]
    assert headers[0].level == 1
    assert headers[1].level == 2
    assert headers[2].level == 3
    
    # Verificar código
    code_blocks = [b for b in blocks if isinstance(b, NotionCodeBlock)]
    assert len(code_blocks) == 1
    assert code_blocks[0].language == 'python'
    
    # Verificar tabela
    tables = [b for b in blocks if isinstance(b, NotionTable)]
    assert len(tables) == 1
    assert len(tables[0].headers) == 3
    assert len(tables[0].rows) == 2
