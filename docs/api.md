---
layout: page
title: API Reference
permalink: /api/
---

# API Reference

## Core Classes

### DocSync

Main class for synchronization operations.

```python
from docsync import DocSync

sync = DocSync(base_path="./docs")
```

#### Methods

- `configure()`: Setup initial configuration
- `sync()`: Perform synchronization
- `backup()`: Create backup of documents

### NotionBridge

Integration with Notion workspace.

```python
from docsync.integrations.notion import NotionBridge, NotionConfig

config = NotionConfig(
    token='your_notion_token',
    workspace_id='your_workspace'
)

bridge = NotionBridge(config)
await bridge.sync()
```

#### Methods

- `sync()`: Bidirectional synchronization
- `upload()`: Upload local files to Notion
- `download()`: Download Notion pages to local

## Configuration

### Environment Variables

- `NOTION_TOKEN`: Your Notion integration token
- `DOCSYNC_BASE_PATH`: Default base path for documents
- `DOCSYNC_LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

### Configuration File

```yaml
# config.yaml
notion:
  token: ${NOTION_TOKEN}
  workspace_id: "your-workspace-id"

sync:
  auto_backup: true
  conflict_resolution: "local_wins"
  
templates:
  esg_report: "templates/esg.md"
```

## CLI Commands

### docsync sync

Synchronize documentation.

```bash
docsync sync [PATH] [OPTIONS]
```

**Options:**
- `--config`: Configuration file path
- `--dry-run`: Preview changes without applying
- `--force`: Force synchronization ignoring conflicts

### docsync generate

Generate documents from templates.

```bash
docsync generate --template [TEMPLATE] --output [PATH]
```

**Templates:**
- `esg-report`: ESG compliance report
- `api-docs`: API documentation
- `user-guide`: User guide template

## Error Handling

### Common Exceptions

```python
from docsync.exceptions import (
    SyncError,
    NotionConnectionError,
    ConfigurationError
)

try:
    await sync.sync()
except SyncError as e:
    print(f"Sync failed: {e}")
except NotionConnectionError as e:
    print(f"Notion connection failed: {e}")
```

## Advanced Usage

### Custom Filters

```python
from docsync.filters import MarkdownFilter

class CustomFilter(MarkdownFilter):
    def process(self, content):
        # Custom processing logic
        return content.upper()

sync.add_filter(CustomFilter())
```

### Webhooks

```python
from docsync.webhooks import WebhookHandler

handler = WebhookHandler('http://your-webhook-url.com')
sync.add_webhook(handler)
```

## Examples

### Basic Synchronization

```python
import asyncio
from docsync import DocSync
from docsync.integrations.notion import NotionBridge

async def main():
    sync = DocSync(base_path="./docs")
    bridge = NotionBridge.from_env()
    
    await sync.sync_with_notion(bridge)

asyncio.run(main())
```

### Batch Processing

```python
import os
from docsync import DocSync

sync = DocSync()

# Process all markdown files
for root, dirs, files in os.walk("./docs"):
    for file in files:
        if file.endswith('.md'):
            sync.process_file(os.path.join(root, file))
```

### Custom Template

```python
from docsync.templates import Template

template = Template.from_file("my-template.md")
result = template.render(
    title="My Document",
    author="John Doe",
    data={"key": "value"}
)

with open("output.md", "w") as f:
    f.write(result)
```

## Integration Examples

### GitHub Actions

```yaml
name: Sync Documentation

on:
  push:
    paths: ['docs/**']

jobs:
  sync:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Setup Python
        uses: actions/setup-python@v3
        with:
          python-version: '3.9'
      - name: Install DocSync
        run: pip install docsync
      - name: Sync to Notion
        env:
          NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
        run: docsync sync ./docs
```

### Docker

```dockerfile
FROM python:3.9-slim

RUN pip install docsync

COPY docs/ /app/docs/
WORKDIR /app

CMD ["docsync", "sync", "./docs"]
```

## Support

For additional help:

- [GitHub Issues](https://github.com/NEO-SH1W4/docsync/issues)
- [Discussions](https://github.com/NEO-SH1W4/docsync/discussions)
- [Contributing Guide](./CONTRIBUTING.md)

