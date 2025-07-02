---
layout: page
title: Documentation
permalink: /docs/
---

# Documentation

Welcome to DocSync documentation! Here you'll find everything you need to get started with our enterprise-grade documentation synchronization platform.

## Getting Started

### Installation

#### Via pip (Recommended)
```bash
pip install docsync
```

#### Development Installation
```bash
git clone https://github.com/NEO-SH1W4/docsync.git
cd docsync
pip install -e ".[dev]"
```

#### Docker Installation
```bash
docker pull neosh1w4/docsync:latest
```

### Quick Setup

1. **Configure your environment:**
   ```bash
   export NOTION_TOKEN="your_notion_integration_token"
   export DOCSYNC_BASE_PATH="./docs"
   ```

2. **Initialize DocSync:**
   ```python
   from docsync import DocSync
   
   sync = DocSync()
   sync.configure()
   ```

3. **Start synchronizing:**
   ```bash
   docsync sync ./docs --config config.yaml
   ```

## Core Concepts

### Synchronization Engine

DocSync's synchronization engine provides:

- **Bidirectional Sync**: Changes flow both ways between local files and Notion
- **Conflict Resolution**: Intelligent handling of simultaneous changes
- **Real-time Monitoring**: File system watching for instant updates
- **Selective Sync**: Choose which files and folders to synchronize

### Integration Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Local Files   │◄──►│    DocSync      │◄──►│     Notion      │
│                 │    │   Core Engine   │    │   Workspace     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         ▲                       ▲                       ▲
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Git Repo      │    │   AI Processor  │    │   Templates     │
│                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `NOTION_TOKEN` | Notion integration token | Yes |
| `DOCSYNC_BASE_PATH` | Default base path for documents | No |
| `DOCSYNC_LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | No |
| `DOCSYNC_BACKUP_ENABLED` | Enable automatic backups | No |

### Configuration File

Create a `config.yaml` file:

```yaml
# DocSync Configuration
version: "1.0"

# Notion Integration
notion:
  token: ${NOTION_TOKEN}
  workspace_id: "your-workspace-id"
  database_id: "your-database-id"  # Optional

# Synchronization Settings
sync:
  direction: "bidirectional"  # bidirectional, upload, download
  auto_backup: true
  conflict_resolution: "prompt"  # prompt, local_wins, remote_wins
  ignore_patterns:
    - "*.tmp"
    - ".git/*"
    - "node_modules/*"

# AI Processing
ai:
  enabled: true
  quality_check: true
  auto_improve: false

# Templates
templates:
  path: "./templates"
  default_language: "en"
  
# Logging
logging:
  level: "INFO"
  file: "./logs/docsync.log"
  max_size: "10MB"
  backup_count: 5
```

## Features

### File Synchronization

#### Supported File Types

- **Markdown** (`.md`, `.markdown`)
- **Plain Text** (`.txt`)
- **HTML** (`.html`, `.htm`)
- **JSON** (`.json`)
- **YAML** (`.yaml`, `.yml`)

#### Synchronization Modes

1. **Bidirectional**: Changes sync in both directions
2. **Upload Only**: Local files sync to Notion
3. **Download Only**: Notion pages sync to local

### AI-Enhanced Processing

DocSync includes AI capabilities for:

- **Quality Analysis**: Automatic documentation scoring
- **Content Optimization**: AI-powered improvement suggestions
- **Metadata Extraction**: Intelligent tagging and categorization
- **Link Validation**: Automated broken link detection

### Template System

#### Built-in Templates

- **ESG Report**: Environmental, Social, Governance compliance
- **API Documentation**: REST API documentation template
- **User Guide**: Software user guide template
- **Technical Specification**: Technical spec template

#### Custom Templates

Create custom templates using Jinja2 syntax:

```markdown
# {{ title }}

**Author**: {{ author }}
**Date**: {{ date }}

## Overview
{{ overview }}

## Details
{% for item in items %}
- {{ item.name }}: {{ item.description }}
{% endfor %}
```

### Backup and Versioning

DocSync automatically creates backups:

- **Git Integration**: Automatic commits for changes
- **Timestamped Backups**: Point-in-time recovery
- **Conflict Archives**: Preserve conflicted versions

## Advanced Usage

### Custom Filters

Extend DocSync with custom processing:

```python
from docsync.filters import BaseFilter

class CustomMarkdownFilter(BaseFilter):
    def process(self, content, metadata):
        # Add custom processing logic
        processed_content = self.add_table_of_contents(content)
        return processed_content, metadata
    
    def add_table_of_contents(self, content):
        # Implementation here
        return content

# Register the filter
sync.add_filter(CustomMarkdownFilter())
```

### Webhooks

Set up webhooks for external integrations:

```python
from docsync.webhooks import WebhookHandler

# Slack integration
slack_webhook = WebhookHandler(
    url="https://hooks.slack.com/services/...",
    events=["sync_complete", "conflict_detected"]
)

sync.add_webhook(slack_webhook)
```

### Batch Operations

Process multiple files efficiently:

```python
import asyncio
from docsync import DocSync

async def batch_sync():
    sync = DocSync()
    
    # Process all markdown files in parallel
    tasks = []
    for file_path in sync.find_files("*.md"):
        task = sync.process_file_async(file_path)
        tasks.append(task)
    
    results = await asyncio.gather(*tasks)
    return results

# Run batch operation
results = asyncio.run(batch_sync())
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Problem**: `NotionConnectionError: Invalid token`

**Solution**:
- Verify your Notion token is correct
- Ensure the integration has proper permissions
- Check token expiration

#### 2. Sync Conflicts

**Problem**: Files show conflicts during sync

**Solutions**:
- Use `--force` flag to override
- Set `conflict_resolution: "local_wins"` in config
- Manually resolve conflicts using the conflict editor

#### 3. Performance Issues

**Problem**: Slow synchronization for large repositories

**Solutions**:
- Use selective sync patterns
- Enable parallel processing
- Increase batch sizes in configuration

### Debug Mode

Enable debug logging:

```bash
export DOCSYNC_LOG_LEVEL=DEBUG
docsync sync ./docs --verbose
```

### Health Check

Verify your installation:

```bash
docsync health-check
```

## Integration Examples

### GitHub Actions

```yaml
name: DocSync CI/CD

on:
  push:
    branches: [main]
    paths: ['docs/**']

jobs:
  sync-docs:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Setup Python
      uses: actions/setup-python@v3
      with:
        python-version: '3.9'
    
    - name: Install DocSync
      run: pip install docsync
    
    - name: Sync Documentation
      env:
        NOTION_TOKEN: ${{ secrets.NOTION_TOKEN }}
      run: |
        docsync sync ./docs \
          --config .docsync/config.yaml \
          --log-level INFO
```

### Docker Compose

```yaml
version: '3.8'

services:
  docsync:
    image: neosh1w4/docsync:latest
    environment:
      - NOTION_TOKEN=${NOTION_TOKEN}
      - DOCSYNC_BASE_PATH=/app/docs
    volumes:
      - ./docs:/app/docs
      - ./config.yaml:/app/config.yaml
    command: ["docsync", "sync", "/app/docs", "--config", "/app/config.yaml"]
```

### VS Code Extension

Install the DocSync VS Code extension for:

- Syntax highlighting for DocSync configs
- Real-time sync status
- Conflict resolution interface
- Template insertion

## Best Practices

### File Organization

```
project/
├── docs/
│   ├── api/           # API documentation
│   ├── guides/        # User guides
│   ├── tutorials/     # Step-by-step tutorials
│   └── reference/     # Reference materials
├── templates/         # Custom templates
├── .docsync/
│   ├── config.yaml    # DocSync configuration
│   └── filters.py     # Custom filters
└── .gitignore         # Include DocSync cache files
```

### Configuration Management

- Use environment variables for secrets
- Version control your configuration files
- Separate configurations for different environments

### Performance Optimization

- Use `.docsyncignore` files to exclude unnecessary files
- Enable selective sync for large repositories
- Configure appropriate batch sizes

## Support and Community

### Getting Help

- **GitHub Issues**: [Report bugs and request features](https://github.com/NEO-SH1W4/docsync/issues)
- **Discussions**: [Community discussions and Q&A](https://github.com/NEO-SH1W4/docsync/discussions)
- **Documentation**: [Official documentation](https://neo-sh1w4.github.io/docsync)

### Contributing

We welcome contributions! See our [Contributing Guide](./CONTRIBUTING.md) for:

- Code of conduct
- Development setup
- Pull request process
- Coding standards

### Enterprise Support

For enterprise features and professional support:

- **Email**: enterprise@docsync.dev
- **Professional Services**: Custom implementations and training
- **SLA**: Service level agreements for critical deployments

---

*This documentation is automatically synchronized with our Notion workspace using DocSync itself!*

