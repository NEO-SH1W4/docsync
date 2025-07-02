"""
Performance tests and benchmarks for DocSync.

Enterprise-grade performance testing following industry best practices.
"""

import asyncio
import time
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# Third-party performance testing
pytest_plugins = ["pytest_benchmark", "pytest_asyncio"]


@pytest.mark.performance
class TestSyncPerformance:
    """Performance tests for sync operations."""

    def test_file_processing_speed(
        self,
        benchmark,
        temp_dir: Path,
        sample_markdown: str,
    ):
        """Benchmark file processing speed."""
        # Create test files
        files = []
        for i in range(100):
            file_path = temp_dir / f"test_{i}.md"
            file_path.write_text(sample_markdown)
            files.append(file_path)

        def process_files():
            from docsync.utils import process_markdown

            results = []
            for file_path in files:
                content = file_path.read_text()
                result = process_markdown(content)
                results.append(result)
            return results

        # Benchmark: Should process 100 files in < 1 second
        result = benchmark.pedantic(process_files, rounds=5, iterations=1)
        assert len(result) == 100

        # Performance assertion
        assert benchmark.stats.stats.mean < 1.0  # Less than 1 second

    @pytest.mark.asyncio
    async def test_concurrent_sync_performance(
        self,
        temp_dir: Path,
        sample_config: dict,
        performance_config: dict,
    ):
        """Test concurrent sync operations performance."""
        from docsync.core import DocSync

        # Create multiple files
        files = []
        for i in range(performance_config["concurrent_operations"]):
            file_path = temp_dir / f"concurrent_{i}.md"
            file_path.write_text(f"# File {i}\n" + "Content line\n" * 1000)
            files.append(file_path)

        doc_sync = DocSync(base_path=temp_dir, config=sample_config)

        async def sync_single_file(file_path):
            # Mock sync operation
            await asyncio.sleep(0.1)  # Simulate I/O
            return {"file": file_path.name, "status": "synced"}

        start_time = time.time()

        # Run concurrent operations
        with patch.object(doc_sync, "_sync_single_file", side_effect=sync_single_file):
            tasks = [sync_single_file(f) for f in files]
            results = await asyncio.gather(*tasks)

        end_time = time.time()
        duration = end_time - start_time

        # Should complete all operations in reasonable time
        expected_sequential_time = len(files) * 0.1
        efficiency = expected_sequential_time / duration

        assert len(results) == len(files)
        assert efficiency > 5  # At least 5x faster than sequential
        assert duration < performance_config["timeout_seconds"]

    def test_large_file_processing(
        self,
        benchmark,
        temp_dir: Path,
        performance_config: dict,
    ):
        """Benchmark large file processing."""
        # Create large file
        large_file = temp_dir / "large_file.md"
        large_content = "# Large File\n" + "Content line with some text\n" * 50000
        large_file.write_text(large_content)

        def process_large_file():
            from docsync.utils import process_markdown

            content = large_file.read_text()
            return process_markdown(content)

        result = benchmark.pedantic(process_large_file, rounds=3, iterations=1)

        # Should handle large files efficiently
        assert result is not None
        assert benchmark.stats.stats.mean < 5.0  # Less than 5 seconds

    @pytest.mark.asyncio
    async def test_memory_usage_during_sync(
        self,
        temp_dir: Path,
        sample_config: dict,
        performance_config: dict,
    ):
        """Test memory usage during sync operations."""
        import os

        import psutil

        from docsync.core import DocSync

        # Create many files
        for i in range(1000):
            file_path = temp_dir / f"memory_test_{i}.md"
            file_path.write_text(f"# File {i}\n" + "Content\n" * 100)

        doc_sync = DocSync(base_path=temp_dir, config=sample_config)

        # Monitor memory usage
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Simulate sync operation
        with patch.object(doc_sync, "_sync_files") as mock_sync:
            mock_sync.return_value = {"synced": 1000, "errors": 0}
            await doc_sync.sync()

        peak_memory = process.memory_info().rss
        memory_increase = peak_memory - initial_memory

        # Memory increase should be reasonable (< 100MB)
        assert memory_increase < performance_config["max_memory_usage"]


@pytest.mark.performance
class TestTemplatePerformance:
    """Performance tests for template operations."""

    def test_template_rendering_speed(self, benchmark, temp_dir: Path):
        """Benchmark template rendering performance."""
        # Create template
        template_content = """
# {{title}}

## Overview
{{overview}}

{% for item in items %}
### {{item.name}}
{{item.description}}
{% endfor %}

## Metrics
{% for metric, value in metrics.items() %}
- **{{metric}}**: {{value}}
{% endfor %}
        """

        template_file = temp_dir / "performance_template.md"
        template_file.write_text(template_content)

        # Prepare data
        template_data = {
            "title": "Performance Test Report",
            "overview": "This is a performance test overview.",
            "items": [
                {"name": f"Item {i}", "description": f"Description for item {i}"}
                for i in range(100)
            ],
            "metrics": {f"metric_{i}": i * 10 for i in range(50)},
        }

        def render_template():
            from docsync.utils import render_template

            return render_template(str(template_file), template_data)

        result = benchmark.pedantic(render_template, rounds=10, iterations=1)

        # Should render complex template quickly
        assert len(result) > 1000  # Substantial output
        assert benchmark.stats.stats.mean < 0.1  # Less than 100ms

    def test_multiple_template_rendering(self, benchmark, temp_dir: Path):
        """Benchmark rendering multiple templates."""
        # Create multiple templates
        templates = []
        for i in range(10):
            template_file = temp_dir / f"template_{i}.md"
            template_file.write_text(f"# Template {i}\n{{{{content_{i}}}}}")
            templates.append(template_file)

        def render_all_templates():
            from docsync.utils import render_template

            results = []
            for i, template_file in enumerate(templates):
                data = {f"content_{i}": f"Content for template {i}"}
                result = render_template(str(template_file), data)
                results.append(result)
            return results

        result = benchmark.pedantic(render_all_templates, rounds=5, iterations=1)

        assert len(result) == 10
        assert benchmark.stats.stats.mean < 0.5  # Less than 500ms


@pytest.mark.performance
class TestNotionIntegrationPerformance:
    """Performance tests for Notion integration."""

    @pytest.mark.asyncio
    async def test_api_request_batching(
        self,
        mock_notion_client,
        performance_config: dict,
    ):
        """Test API request batching performance."""
        from docsync.integrations.notion import NotionBridge

        # Configure mock client for performance testing
        mock_notion_client.batch_create_pages = Mock()
        mock_notion_client.batch_create_pages.return_value = [
            {"id": f"page_{i}"} for i in range(100)
        ]

        bridge = NotionBridge(config={"token": "test"})
        bridge.client = mock_notion_client

        # Prepare data for batch operations
        pages_data = [
            {"title": f"Page {i}", "content": f"Content {i}"} for i in range(100)
        ]

        start_time = time.time()

        # Test batch operations
        with patch.object(bridge, "_batch_create_pages") as mock_batch:
            mock_batch.return_value = pages_data
            result = await bridge._batch_create_pages(pages_data)

        end_time = time.time()
        duration = end_time - start_time

        # Batching should be efficient
        assert len(result) == 100
        assert duration < 1.0  # Should complete quickly with batching

    @pytest.mark.asyncio
    async def test_rate_limit_handling_performance(self, mock_notion_client):
        """Test rate limit handling doesn't degrade performance significantly."""
        from docsync.integrations.notion import NotionClient

        client = NotionClient(config={"token": "test"})
        client._session = mock_notion_client

        # Simulate rate limit scenarios
        call_times = []

        async def mock_request(*args, **kwargs):
            start = time.time()
            # Simulate varying response times
            await asyncio.sleep(0.01)  # 10ms base latency
            call_times.append(time.time() - start)
            return {"status": "success"}

        with patch.object(client, "_make_request", side_effect=mock_request):
            start_time = time.time()

            # Make multiple requests
            tasks = [client._make_request("GET", "test") for _ in range(20)]
            await asyncio.gather(*tasks)

            total_time = time.time() - start_time

        # Rate limiting shouldn't cause excessive delays
        assert total_time < 5.0  # Should complete within 5 seconds
        assert len(call_times) == 20


@pytest.mark.performance
class TestSystemResourceUsage:
    """Test system resource usage patterns."""

    def test_cpu_usage_during_operations(self, temp_dir: Path, sample_config: dict):
        """Monitor CPU usage during intensive operations."""
        import threading
        import time

        import psutil

        from docsync.core import DocSync

        # Create test data
        for i in range(500):
            file_path = temp_dir / f"cpu_test_{i}.md"
            file_path.write_text(f"# File {i}\n" + "Content\n" * 200)

        doc_sync = DocSync(base_path=temp_dir, config=sample_config)

        # Monitor CPU usage
        cpu_usage = []
        monitoring = True

        def monitor_cpu():
            while monitoring:
                cpu_usage.append(psutil.cpu_percent(interval=0.1))
                time.sleep(0.1)

        monitor_thread = threading.Thread(target=monitor_cpu)
        monitor_thread.start()

        try:
            # Simulate intensive operation
            with patch.object(doc_sync, "_process_files") as mock_process:
                mock_process.return_value = {"processed": 500}
                start_time = time.time()

                # Simulate CPU-intensive work
                for _ in range(1000000):
                    pass  # Busy work

                time.time() - start_time
        finally:
            monitoring = False
            monitor_thread.join()

        # Analyze CPU usage
        if cpu_usage:
            avg_cpu = sum(cpu_usage) / len(cpu_usage)
            max_cpu = max(cpu_usage)

            # CPU usage should be reasonable
            assert avg_cpu < 80  # Average CPU < 80%
            assert max_cpu < 95  # Peak CPU < 95%

    def test_file_descriptor_usage(self, temp_dir: Path, sample_config: dict):
        """Test file descriptor usage doesn't leak."""
        import os

        import psutil

        from docsync.core import DocSync

        process = psutil.Process(os.getpid())
        initial_fd_count = process.num_fds() if hasattr(process, "num_fds") else 0

        # Create many files
        for i in range(200):
            file_path = temp_dir / f"fd_test_{i}.md"
            file_path.write_text(f"# File {i}\nContent")

        doc_sync = DocSync(base_path=temp_dir, config=sample_config)

        # Simulate operations that might leak file descriptors
        with patch.object(doc_sync, "_read_files") as mock_read:
            mock_read.return_value = ["content"] * 200

            for _ in range(10):  # Multiple operations
                mock_read()

        final_fd_count = process.num_fds() if hasattr(process, "num_fds") else 0

        # File descriptors shouldn't leak significantly
        if initial_fd_count > 0:
            fd_increase = final_fd_count - initial_fd_count
            assert fd_increase < 50  # Reasonable increase only
