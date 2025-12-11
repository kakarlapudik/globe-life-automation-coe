"""
Code Formatter Integration

Integrates with Python code formatters (Black, autopep8, isort) to format generated code.
"""

import subprocess
import tempfile
from typing import Optional, Dict, List
from pathlib import Path
from dataclasses import dataclass
from enum import Enum


class FormatterType(Enum):
    """Supported code formatters"""
    BLACK = "black"
    AUTOPEP8 = "autopep8"
    YAPF = "yapf"
    ISORT = "isort"  # For import sorting


@dataclass
class FormatterConfig:
    """Configuration for code formatter"""
    formatter_type: FormatterType
    line_length: int = 88
    skip_string_normalization: bool = False
    target_version: Optional[str] = None
    additional_args: Optional[List[str]] = None


@dataclass
class FormattingResult:
    """Result of code formatting"""
    success: bool
    formatted_code: str
    original_code: str
    changes_made: bool
    error_message: Optional[str] = None
    formatter_used: Optional[FormatterType] = None


class CodeFormatter:
    """
    Integrates with Python code formatters to format generated code.
    
    Features:
    - Supports multiple formatters (Black, autopep8, yapf)
    - Import sorting with isort
    - Configurable formatting options
    - Fallback to alternative formatters
    - Validation of formatted code
    """
    
    def __init__(self, config: Optional[FormatterConfig] = None):
        """
        Initialize the code formatter.
        
        Args:
            config: Optional formatter configuration
        """
        self.config = config or FormatterConfig(
            formatter_type=FormatterType.BLACK,
            line_length=88
        )
    
    def format_code(
        self,
        code: str,
        sort_imports: bool = True
    ) -> FormattingResult:
        """
        Format Python code using configured formatter.
        
        Args:
            code: Python code to format
            sort_imports: Whether to sort imports with isort
            
        Returns:
            FormattingResult with formatted code
        """
        original_code = code
        
        # Sort imports first if requested
        if sort_imports:
            code = self._sort_imports(code)
        
        # Format code with primary formatter
        result = self._format_with_formatter(code, self.config.formatter_type)
        
        # If primary formatter fails, try fallback
        if not result.success:
            fallback_formatter = self._get_fallback_formatter()
            if fallback_formatter:
                result = self._format_with_formatter(code, fallback_formatter)
        
        # If all formatters fail, return original code
        if not result.success:
            return FormattingResult(
                success=False,
                formatted_code=original_code,
                original_code=original_code,
                changes_made=False,
                error_message=result.error_message,
                formatter_used=None
            )
        
        return FormattingResult(
            success=True,
            formatted_code=result.formatted_code,
            original_code=original_code,
            changes_made=result.formatted_code != original_code,
            error_message=None,
            formatter_used=result.formatter_used
        )
    
    def format_file(
        self,
        file_path: Path,
        in_place: bool = True,
        sort_imports: bool = True
    ) -> FormattingResult:
        """
        Format a Python file.
        
        Args:
            file_path: Path to the Python file
            in_place: Whether to modify the file in place
            sort_imports: Whether to sort imports
            
        Returns:
            FormattingResult with formatted code
        """
        # Read file
        code = file_path.read_text()
        
        # Format code
        result = self.format_code(code, sort_imports=sort_imports)
        
        # Write back if in_place and successful
        if in_place and result.success and result.changes_made:
            file_path.write_text(result.formatted_code)
        
        return result
    
    def format_multiple_files(
        self,
        file_paths: List[Path],
        in_place: bool = True,
        sort_imports: bool = True
    ) -> Dict[Path, FormattingResult]:
        """
        Format multiple Python files.
        
        Args:
            file_paths: List of file paths to format
            in_place: Whether to modify files in place
            sort_imports: Whether to sort imports
            
        Returns:
            Dictionary mapping file paths to FormattingResults
        """
        results = {}
        
        for file_path in file_paths:
            result = self.format_file(file_path, in_place, sort_imports)
            results[file_path] = result
        
        return results
    
    def _format_with_formatter(
        self,
        code: str,
        formatter_type: FormatterType
    ) -> FormattingResult:
        """Format code with specific formatter"""
        if formatter_type == FormatterType.BLACK:
            return self._format_with_black(code)
        elif formatter_type == FormatterType.AUTOPEP8:
            return self._format_with_autopep8(code)
        elif formatter_type == FormatterType.YAPF:
            return self._format_with_yapf(code)
        else:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=False,
                error_message=f"Unsupported formatter: {formatter_type}",
                formatter_used=None
            )
    
    def _format_with_black(self, code: str) -> FormattingResult:
        """Format code with Black"""
        try:
            # Try to import black
            import black
            
            # Configure Black
            mode = black.Mode(
                line_length=self.config.line_length,
                string_normalization=not self.config.skip_string_normalization,
            )
            
            # Format code
            formatted_code = black.format_str(code, mode=mode)
            
            return FormattingResult(
                success=True,
                formatted_code=formatted_code,
                original_code=code,
                changes_made=formatted_code != code,
                error_message=None,
                formatter_used=FormatterType.BLACK
            )
        
        except ImportError:
            return self._format_with_subprocess(code, FormatterType.BLACK)
        
        except Exception as e:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=False,
                error_message=f"Black formatting failed: {str(e)}",
                formatter_used=FormatterType.BLACK
            )
    
    def _format_with_autopep8(self, code: str) -> FormattingResult:
        """Format code with autopep8"""
        try:
            # Try to import autopep8
            import autopep8
            
            # Configure autopep8
            options = {
                'max_line_length': self.config.line_length,
                'aggressive': 1,
            }
            
            # Format code
            formatted_code = autopep8.fix_code(code, options=options)
            
            return FormattingResult(
                success=True,
                formatted_code=formatted_code,
                original_code=code,
                changes_made=formatted_code != code,
                error_message=None,
                formatter_used=FormatterType.AUTOPEP8
            )
        
        except ImportError:
            return self._format_with_subprocess(code, FormatterType.AUTOPEP8)
        
        except Exception as e:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=False,
                error_message=f"autopep8 formatting failed: {str(e)}",
                formatter_used=FormatterType.AUTOPEP8
            )
    
    def _format_with_yapf(self, code: str) -> FormattingResult:
        """Format code with YAPF"""
        try:
            # Try to import yapf
            from yapf.yapflib.yapf_api import FormatCode
            
            # Format code
            formatted_code, changed = FormatCode(
                code,
                style_config={'column_limit': self.config.line_length}
            )
            
            return FormattingResult(
                success=True,
                formatted_code=formatted_code,
                original_code=code,
                changes_made=changed,
                error_message=None,
                formatter_used=FormatterType.YAPF
            )
        
        except ImportError:
            return self._format_with_subprocess(code, FormatterType.YAPF)
        
        except Exception as e:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=False,
                error_message=f"YAPF formatting failed: {str(e)}",
                formatter_used=FormatterType.YAPF
            )
    
    def _format_with_subprocess(
        self,
        code: str,
        formatter_type: FormatterType
    ) -> FormattingResult:
        """Format code using subprocess (fallback)"""
        try:
            # Create temporary file
            with tempfile.NamedTemporaryFile(
                mode='w',
                suffix='.py',
                delete=False
            ) as temp_file:
                temp_file.write(code)
                temp_path = temp_file.name
            
            # Build command
            if formatter_type == FormatterType.BLACK:
                cmd = [
                    'black',
                    '--line-length', str(self.config.line_length),
                    temp_path
                ]
            elif formatter_type == FormatterType.AUTOPEP8:
                cmd = [
                    'autopep8',
                    '--in-place',
                    '--max-line-length', str(self.config.line_length),
                    temp_path
                ]
            elif formatter_type == FormatterType.YAPF:
                cmd = [
                    'yapf',
                    '--in-place',
                    '--style', f'{{column_limit: {self.config.line_length}}}',
                    temp_path
                ]
            else:
                raise ValueError(f"Unsupported formatter: {formatter_type}")
            
            # Run formatter
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Read formatted code
            formatted_code = Path(temp_path).read_text()
            
            # Clean up
            Path(temp_path).unlink()
            
            if result.returncode == 0:
                return FormattingResult(
                    success=True,
                    formatted_code=formatted_code,
                    original_code=code,
                    changes_made=formatted_code != code,
                    error_message=None,
                    formatter_used=formatter_type
                )
            else:
                return FormattingResult(
                    success=False,
                    formatted_code=code,
                    original_code=code,
                    changes_made=False,
                    error_message=result.stderr,
                    formatter_used=formatter_type
                )
        
        except Exception as e:
            return FormattingResult(
                success=False,
                formatted_code=code,
                original_code=code,
                changes_made=False,
                error_message=f"Subprocess formatting failed: {str(e)}",
                formatter_used=formatter_type
            )
    
    def _sort_imports(self, code: str) -> str:
        """Sort imports using isort"""
        try:
            # Try to import isort
            import isort
            
            # Sort imports
            sorted_code = isort.code(code, line_length=self.config.line_length)
            return sorted_code
        
        except ImportError:
            # Try subprocess
            try:
                with tempfile.NamedTemporaryFile(
                    mode='w',
                    suffix='.py',
                    delete=False
                ) as temp_file:
                    temp_file.write(code)
                    temp_path = temp_file.name
                
                subprocess.run(
                    ['isort', temp_path],
                    capture_output=True,
                    timeout=30
                )
                
                sorted_code = Path(temp_path).read_text()
                Path(temp_path).unlink()
                
                return sorted_code
            
            except Exception:
                # If isort fails, return original code
                return code
        
        except Exception:
            # If sorting fails, return original code
            return code
    
    def _get_fallback_formatter(self) -> Optional[FormatterType]:
        """Get fallback formatter if primary fails"""
        if self.config.formatter_type == FormatterType.BLACK:
            return FormatterType.AUTOPEP8
        elif self.config.formatter_type == FormatterType.AUTOPEP8:
            return FormatterType.YAPF
        else:
            return None
    
    def is_formatter_available(self, formatter_type: FormatterType) -> bool:
        """Check if a formatter is available"""
        try:
            if formatter_type == FormatterType.BLACK:
                import black
                return True
            elif formatter_type == FormatterType.AUTOPEP8:
                import autopep8
                return True
            elif formatter_type == FormatterType.YAPF:
                from yapf.yapflib.yapf_api import FormatCode
                return True
            elif formatter_type == FormatterType.ISORT:
                import isort
                return True
        except ImportError:
            # Try subprocess
            try:
                result = subprocess.run(
                    [formatter_type.value, '--version'],
                    capture_output=True,
                    timeout=5
                )
                return result.returncode == 0
            except Exception:
                return False
        
        return False
    
    def get_available_formatters(self) -> List[FormatterType]:
        """Get list of available formatters"""
        available = []
        
        for formatter_type in FormatterType:
            if self.is_formatter_available(formatter_type):
                available.append(formatter_type)
        
        return available
