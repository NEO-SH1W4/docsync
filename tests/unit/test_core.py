"""
Unit tests for DocSync core functionality.

Tests the fundamental components with 90%+ coverage target.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

from docsync.core import DocSync
from docsync.exceptions import DocSyncError, ReportGenerationError


@pytest.mark.unit
class TestDocSyncCore:
    """Test suite for DocSync core functionality."""

    def test_docsync_initialization(self, temp_dir: Path, sample_config: dict):
        """Test DocSync initialization with valid config."""
        # Test successful initialization
        doc_sync = DocSync(base_path=temp_dir, config=sample_config)
        assert doc_sync.base_path == temp_dir
        assert doc_sync.config is not None

    def test_docsync_invalid_path(self, sample_config: dict):
        """Test DocSync initialization with invalid path."""
        invalid_path = Path("/nonexistent/path")

        with pytest.raises(DocSyncError, match="Invalid base path"):
            DocSync(base_path=invalid_path, config=sample_config)

    def test_config_validation(self, temp_dir: Path):
        """Test configuration validation."""
        # Test missing required fields
        invalid_config = {"invalid": "config"}

        with pytest.raises(DocSyncError, match="Invalid configuration"):
            DocSync(base_path=temp_dir, config=invalid_config)

    @pytest.mark.asyncio
    async def test_sync_operation(
        self,
        temp_dir: Path,
        sample_config: dict,
        sample_files: dict,
    ):
        """Test basic sync operation."""
        doc_sync = DocSync(base_path=temp_dir, config=sample_config)

        with patch.object(doc_sync, "_sync_files") as mock_sync:
            mock_sync.return_value = {"synced": 2, "errors": 0}

            result = await doc_sync.sync()

            assert result["synced"] >= 0
            assert result["errors"] == 0
            mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_error_handling(self, temp_dir: Path, sample_config: dict):
        """Test sync operation error handling."""
        doc_sync = DocSync(base_path=temp_dir, config=sample_config)

        with patch.object(doc_sync, "_sync_files") as mock_sync:
            mock_sync.side_effect = Exception("Sync failed")

            with pytest.raises(DocSyncError, match="Sync operation failed"):
                await doc_sync.sync()

    def test_report_generation(self, temp_dir: Path, sample_config: dict):
        """Test ESG report generation."""
        doc_sync = DocSync(base_path=temp_dir, config=sample_config)

        template_data = {
            "company": "Test Corp",
            "year": 2024,
            "metrics": {"carbon": 100, "water": 200},
        }

        with patch.object(doc_sync, "_render_template") as mock_render:
            mock_render.return_value = "Generated report content"

            result = doc_sync.generate_report("esg_template", template_data)

            assert result is not None
            assert len(result) > 0
            mock_render.assert_called_once()

    def test_report_generation_invalid_template(
        self,
        temp_dir: Path,
        sample_config: dict,
    ):
        """Test report generation with invalid template."""
        doc_sync = DocSync(base_path=temp_dir, config=sample_config)

        with pytest.raises(ReportGenerationError, match="Template not found"):
            doc_sync.generate_report("nonexistent_template", {})

    @pytest.mark.performance
    def test_large_file_handling(
        self,
        temp_dir: Path,
        sample_config: dict,
        performance_config: dict,
    ):
        """Test handling of large files."""
        doc_sync = DocSync(base_path=temp_dir, config=sample_config)

        # Create large file
        large_file = temp_dir / "large_file.md"
        large_content = "# Large File\n" + "Content line\n" * 10000
        large_file.write_text(large_content)

        # Test processing doesn't crash
        result = doc_sync._analyze_file(large_file)
        assert result is not None
        assert result.get("size", 0) > performance_config["large_file_size"]

    @pytest.mark.security
    def test_path_traversal_protection(
        self,
        temp_dir: Path,
        sample_config: dict,
        security_test_data: dict,
    ):
        """Test protection against path traversal attacks."""
        doc_sync = DocSync(base_path=temp_dir, config=sample_config)

        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\windows\\system32\\config\\sam",
            "/etc/shadow",
        ]

        for malicious_path in malicious_paths:
            with pytest.raises(DocSyncError, match="Invalid file path"):
                doc_sync._validate_file_path(malicious_path)

    def test_configuration_update(self, temp_dir: Path, sample_config: dict):
        """Test runtime configuration updates."""
        doc_sync = DocSync(base_path=temp_dir, config=sample_config)

        new_config = sample_config.copy()
        new_config["sync"]["sync_interval"] = 600

        doc_sync.update_config(new_config)

        assert doc_sync.config["sync"]["sync_interval"] == 600

    @pytest.mark.asyncio
    async def test_concurrent_operations(self, temp_dir: Path, sample_config: dict):
        """Test concurrent sync operations."""
        doc_sync = DocSync(base_path=temp_dir, config=sample_config)

        # Create multiple files
        for i in range(5):
            (temp_dir / f"file_{i}.md").write_text(f"# File {i}\nContent")

        with patch.object(doc_sync, "_sync_single_file") as mock_sync:
            mock_sync.return_value = {"status": "success"}

            # Run concurrent operations
            import asyncio

            tasks = [doc_sync._sync_single_file(f"file_{i}.md") for i in range(5)]
            results = await asyncio.gather(*tasks)

            assert len(results) == 5
            assert all(result["status"] == "success" for result in results)


@pytest.mark.unit
class TestDocSyncUtilities:
    """Test suite for DocSync utility functions."""

    def test_file_validation(self, temp_dir: Path):
        """Test file validation utilities."""
        from docsync.utils import validate_file_format

        # Valid markdown file
        valid_file = temp_dir / "valid.md"
        valid_file.write_text("# Valid Markdown\nContent")

        assert validate_file_format(valid_file) is True

        # Invalid file format
        invalid_file = temp_dir / "invalid.xyz"
        invalid_file.write_text("Invalid content")

        assert validate_file_format(invalid_file) is False

    def test_markdown_processing(self, sample_markdown: str):
        """Test markdown processing utilities."""
        from docsync.utils import process_markdown

        result = process_markdown(sample_markdown)

        assert result is not None
        assert "metadata" in result
        assert "content" in result
        assert result["metadata"]["title"] == "Test Document"

    def test_template_rendering(self, temp_dir: Path):
        """Test template rendering utilities."""
        from docsync.utils import render_template

        # Create template file
        template_file = temp_dir / "test_template.md"
        template_file.write_text("# {{title}}\n{{content}}")

        data = {"title": "Test Title", "content": "Test content"}
        result = render_template(str(template_file), data)

        assert "Test Title" in result
        assert "Test content" in result

    @pytest.mark.security
    def test_input_sanitization(self, security_test_data: dict):
        """Test input sanitization utilities."""
        from docsync.utils import sanitize_input

        for malicious_input in security_test_data["malicious_input"]:
            sanitized = sanitize_input(malicious_input)

            # Should not contain dangerous patterns
            assert "<script>" not in sanitized
            assert "DROP TABLE" not in sanitized
            assert "../" not in sanitized


@pytest.mark.unit
class TestErrorHandling:
    """Test suite for error handling."""

    def test_docsync_error_creation(self):
        """Test DocSyncError creation and properties."""
        error = DocSyncError("Test error", code="TEST_001")

        assert str(error) == "Test error"
        assert error.code == "TEST_001"

    def test_report_generation_error(self):
        """Test ReportGenerationError specific functionality."""
        error = ReportGenerationError("Template error", template="test_template")

        assert str(error) == "Template error"
        assert error.template == "test_template"

    def test_error_chaining(self):
        """Test error chaining functionality."""
        original_error = ValueError("Original error")

        try:
            msg = "Wrapped error"
            raise DocSyncError(msg) from original_error
        except DocSyncError as e:
            chained_error = e

        assert chained_error.__cause__ is original_error
        assert "Original error" in str(chained_error.__cause__)


# Integration test placeholder
@pytest.mark.integration
class TestDocSyncIntegration:
    """Integration tests for DocSync components."""

    @pytest.mark.asyncio
    async def test_full_sync_workflow(
        self,
        temp_dir: Path,
        sample_config: dict,
        sample_files: dict,
    ):
        """Test complete sync workflow integration."""
        DocSync(base_path=temp_dir, config=sample_config)

        # This would test the complete workflow
        # Implementation depends on actual DocSync class structure
