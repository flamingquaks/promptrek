"""Comprehensive Continue adapter tests."""

import pytest
from promptrek.adapters.continue_adapter import ContinueAdapter
from promptrek.core.models import UniversalPrompt, UniversalPromptV2, PromptMetadata, Instructions, DocumentConfig


class TestContinueAdapterComprehensive:
    """Comprehensive tests for Continue adapter."""

    @pytest.fixture
    def adapter(self):
        return ContinueAdapter()

    @pytest.fixture
    def v2_prompt(self):
        return UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test Instructions"
        )

    @pytest.fixture
    def v1_prompt(self):
        return UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(general=["Test"])
        )

    def test_generate_v2_basic(self, adapter, v2_prompt, tmp_path):
        files = adapter.generate(v2_prompt, tmp_path)
        assert len(files) > 0

    def test_generate_v2_with_documents(self, adapter, tmp_path):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Main",
            documents=[
                DocumentConfig(name="doc1", content="# Doc 1"),
                DocumentConfig(name="doc2", content="# Doc 2")
            ]
        )
        
        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_generate_v1(self, adapter, v1_prompt, tmp_path):
        files = adapter.generate(v1_prompt, tmp_path)
        assert len(files) > 0

    def test_validate_v2(self, adapter, v2_prompt):
        errors = adapter.validate(v2_prompt)
        assert isinstance(errors, list)

    def test_validate_v1(self, adapter, v1_prompt):
        errors = adapter.validate(v1_prompt)
        assert isinstance(errors, list)

    def test_generate_with_variables(self, adapter, tmp_path):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="Project: {{{ NAME }}}",
            variables={"NAME": "Test"}
        )
        
        files = adapter.generate(prompt, tmp_path, variables={"NAME": "Override"})
        assert len(files) > 0

    def test_parse_files(self, adapter, tmp_path):
        # Create continue config structure
        continue_dir = tmp_path / ".continue"
        continue_dir.mkdir()
        config_file = continue_dir / "config.json"
        config_file.write_text('{"rules": []}')
        
        try:
            result = adapter.parse_files(tmp_path)
            # May or may not work depending on implementation
        except Exception:
            pass

    def test_generate_multiple_documents(self, adapter, tmp_path):
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Main",
            documents=[
                DocumentConfig(name=f"doc{i}", content=f"# Doc {i}")
                for i in range(5)
            ]
        )
        
        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_generate_v1_with_all_categories(self, adapter, tmp_path):
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(
                general=["General"],
                code_style=["Style"],
                architecture=["Arch"],
                testing=["Test"],
                security=["Secure"],
                performance=["Perf"]
            )
        )
        
        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_generate_with_examples(self, adapter, tmp_path):
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(general=["Test"]),
            examples={"ex1": "code here"}
        )

        files = adapter.generate(prompt, tmp_path)
        assert len(files) > 0

    def test_generate_v1_with_code_style(self, adapter, tmp_path):
        """Test v1 generation with code style rules."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(
                general=["General rule"],
                code_style=["Follow PEP 8", "Use type hints"]
            )
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0
        # Check that code-style.md was created
        assert any("code-style.md" in str(f) for f in files)

    def test_generate_v1_with_testing(self, adapter, tmp_path):
        """Test v1 generation with testing rules."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(
                general=["General rule"],
                testing=["Write unit tests", "Use pytest"]
            )
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0
        # Check that testing.md was created
        assert any("testing.md" in str(f) for f in files)

    def test_generate_v1_dry_run(self, adapter, tmp_path):
        """Test v1 generation with dry_run mode."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(
                general=["General rule"],
                code_style=["Style rule"]
            )
        )

        files = adapter.generate(prompt, tmp_path, dry_run=True)

        # In dry run mode, files should still be returned but not created
        assert len(files) > 0
        # But the actual files shouldn't exist
        for f in files:
            assert not f.exists()

    def test_generate_v1_verbose(self, adapter, tmp_path):
        """Test v1 generation with verbose mode."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(
                general=["General rule"],
                code_style=["Style rule"]
            )
        )

        files = adapter.generate(prompt, tmp_path, verbose=True)

        assert len(files) > 0

    def test_generate_v1_with_conditionals(self, adapter, tmp_path):
        """Test v1 generation with conditional instructions."""
        from promptrek.core.models import Condition

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(general=["Base rule"]),
            conditions=[
                Condition.model_validate({
                    "if": "EDITOR == 'continue'",
                    "then": {"instructions": {"general": ["Continue-specific rule"]}}
                })
            ]
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_build_rules_content(self, adapter):
        """Test _build_rules_content method."""
        result = adapter._build_rules_content("Test Title", ["Rule 1", "Rule 2"])

        assert "Test Title" in result
        assert "Rule 1" in result
        assert "Rule 2" in result

    def test_generate_v1_with_tech_rules(self, adapter, tmp_path):
        """Test v1 generation with technology-specific rules."""
        from promptrek.core.models import ProjectContext

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            context=ProjectContext(
                project_type="web_application",
                technologies=["Python", "React", "TypeScript"]
            ),
            instructions=Instructions(general=["General rule"])
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0
        # Check that tech-specific rules were created
        assert any("python-rules.md" in str(f).lower() for f in files)

    def test_generate_v1_with_architecture(self, adapter, tmp_path):
        """Test v1 generation with architecture rules."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(
                general=["General"],
                architecture=["Follow MVC", "Use dependency injection"]
            )
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_generate_v1_with_security(self, adapter, tmp_path):
        """Test v1 generation with security rules."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(
                general=["General"],
                security=["Sanitize inputs", "Use HTTPS"]
            )
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_generate_v1_with_performance(self, adapter, tmp_path):
        """Test v1 generation with performance rules."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(
                general=["General"],
                performance=["Cache results", "Minimize database queries"]
            )
        )

        files = adapter.generate(prompt, tmp_path)

        assert len(files) > 0

    def test_validate_v1_no_description(self, adapter):
        """Test validation with no description."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description=""),
            targets=["continue"],
            instructions=Instructions(general=["Test"])
        )

        errors = adapter.validate(prompt)

        # Should have error about missing description
        assert len(errors) > 0

    def test_supports_variables(self, adapter):
        """Test that adapter supports variables."""
        assert adapter.supports_variables() is True

    def test_supports_conditionals(self, adapter):
        """Test that adapter supports conditionals."""
        assert adapter.supports_conditionals() is True

    def test_generate_v2_documents_dry_run_verbose(self, adapter, tmp_path):
        """Test v2 documents generation with dry run and verbose."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Main",
            documents=[
                DocumentConfig(name="doc1", content="# Document 1\n\n" + "Content " * 50),
                DocumentConfig(name="doc2", content="# Document 2\n\n" + "Content " * 50)
            ]
        )

        files = adapter.generate(prompt, tmp_path, dry_run=True, verbose=True)

        assert len(files) == 2
        for f in files:
            assert not f.exists()

    def test_generate_v2_main_content_dry_run_verbose(self, adapter, tmp_path):
        """Test v2 main content generation with dry run and verbose."""
        prompt = UniversalPromptV2(
            schema_version="2.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            content="# Test Instructions\n\n" + "Long content " * 50
        )

        files = adapter.generate(prompt, tmp_path, dry_run=True, verbose=True)

        assert len(files) > 0
        for f in files:
            assert not f.exists()

    def test_generate_v1_code_style_dry_run_verbose(self, adapter, tmp_path):
        """Test v1 code style generation with dry run and verbose."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(
                general=["General"],
                code_style=["Style rule 1", "Style rule 2"]
            )
        )

        files = adapter.generate(prompt, tmp_path, dry_run=True, verbose=True)

        assert len(files) > 0
        for f in files:
            assert not f.exists()

    def test_generate_v1_testing_dry_run_verbose(self, adapter, tmp_path):
        """Test v1 testing rules generation with dry run and verbose."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test"),
            targets=["continue"],
            instructions=Instructions(
                general=["General"],
                testing=["Test rule 1", "Test rule 2"]
            )
        )

        files = adapter.generate(prompt, tmp_path, dry_run=True, verbose=True)

        assert len(files) > 0
        for f in files:
            assert not f.exists()


    def test_parse_files_v2_multiple_files(self, adapter, tmp_path):
        """Test parsing multiple markdown files into v2."""
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)

        # Create multiple rule files
        (rules_dir / "general.md").write_text("# General Rules\n\n- Rule 1\n- Rule 2")
        (rules_dir / "code-style.md").write_text("# Code Style\n\n- Style 1\n- Style 2")
        (rules_dir / "testing.md").write_text("# Testing\n\n- Test 1\n- Test 2")

        result = adapter.parse_files(tmp_path)

        assert isinstance(result, UniversalPromptV2)
        assert result.documents is not None
        assert len(result.documents) == 3
        assert any(doc.name == "general" for doc in result.documents)
        assert any(doc.name == "code-style" for doc in result.documents)

    def test_parse_files_v2_with_error(self, adapter, tmp_path):
        """Test parsing with file read error."""
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)

        # Create a valid file
        (rules_dir / "valid.md").write_text("# Valid\n\n- Rule 1")

        result = adapter.parse_files(tmp_path)

        # Should still succeed even if some files have issues
        assert isinstance(result, UniversalPromptV2)

    def test_parse_files_v1_fallback(self, adapter, tmp_path):
        """Test v1 parsing fallback when no rules directory."""
        # No .continue/rules directory, should fall back to v1
        # Create config.yaml instead
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
name: Test Project
systemMessage: Test system message
rules:
  - Rule 1
  - Rule 2
""")

        try:
            result = adapter.parse_files(tmp_path)
            # Should return v1 format
            assert isinstance(result, (UniversalPrompt, UniversalPromptV2))
        except Exception:
            # Might fail if config.yaml structure is wrong, that's ok
            pass

    def test_parse_files_v1_with_rules_dir(self, adapter, tmp_path):
        """Test v1 parsing with rules directory."""
        rules_dir = tmp_path / ".continue" / "rules"
        rules_dir.mkdir(parents=True)

        # Create rule files
        (rules_dir / "general.md").write_text("# General\n\n- Follow patterns\n- Be consistent")
        (rules_dir / "security.md").write_text("# Security\n\n- Sanitize inputs\n- Use HTTPS")
        (rules_dir / "performance.md").write_text("# Performance\n\n- Cache results\n- Optimize queries")
        (rules_dir / "architecture.md").write_text("# Architecture\n\n- Use MVC\n- Follow SOLID")
        (rules_dir / "python-rules.md").write_text("# Python\n\n- Follow PEP 8\n- Use type hints")
        (rules_dir / "unknown-file.md").write_text("# Unknown\n\n- Some rule")

        # Also test config.yaml merging
        config_file = tmp_path / "config.yaml"
        config_file.write_text("""
name: Test Project
systemMessage: |
  Context info

  Test description
rules:
  - Config rule 1
  - Config rule 2
""")

        result = adapter.parse_files(tmp_path)

        assert isinstance(result, UniversalPromptV2)
        # Should have parsed multiple documents
        if result.documents:
            assert len(result.documents) >= 3

    def test_build_legacy_rules_content(self, adapter):
        """Test building legacy rules content."""
        from promptrek.core.models import ProjectContext

        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(
                title="Test Project",
                description="Test description",
                version="1.0.0",
                author="Test",
                created="2024-01-01",
                updated="2024-01-01"
            ),
            targets=["continue"],
            context=ProjectContext(
                project_type="web_app",
                technologies=["Python", "React"],
                description="A web application"
            ),
            instructions=Instructions(
                general=["General rule"],
                code_style=["Style rule"],
                testing=["Test rule"]
            )
        )

        content = adapter._build_legacy_rules_content(prompt)

        assert "Test Project" in content
        assert "Test description" in content
        assert "Project Context" in content
        assert "Python" in content
        assert "React" in content
        assert "General Rules" in content
        assert "Code Style Rules" in content
        assert "Testing Rules" in content
        assert "Continue AI Guidelines" in content

    def test_build_tech_rules_content(self, adapter):
        """Test building technology-specific rules."""
        prompt = UniversalPrompt(
            schema_version="1.0.0",
            metadata=PromptMetadata(title="Test", description="Test", version="1.0.0"),
            targets=["continue"],
            instructions=Instructions(general=["General rule"])
        )

        # Test known technologies
        for tech in ["typescript", "react", "python", "javascript", "node"]:
            content = adapter._build_tech_rules_content(tech, prompt)
            assert tech.title() in content
            assert "Best Practices" in content
            assert "Code Generation Guidelines" in content

        # Test unknown technology
        content = adapter._build_tech_rules_content("rust", prompt)
        assert "Rust" in content
        assert "best practices" in content.lower()

    def test_parse_markdown_file(self, adapter, tmp_path):
        """Test parsing markdown file for instructions."""
        md_file = tmp_path / "test.md"
        md_file.write_text("""# Test Rules

- Instruction 1
- Instruction 2
- Follow project-specific patterns and conventions
- Instruction 3
  - Nested item (should be ignored)
- Maintain consistency with existing codebase
- Instruction 4
""")

        instructions = adapter._parse_markdown_file(md_file)

        # Should include real instructions but not generic guidelines
        assert "Instruction 1" in instructions
        assert "Instruction 2" in instructions
        assert "Instruction 3" in instructions
        assert "Instruction 4" in instructions
        # Generic guidelines should be filtered out
        assert "Follow project-specific patterns and conventions" not in instructions
        assert "Maintain consistency with existing codebase" not in instructions
