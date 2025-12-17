# Framework runner for project-based test generation
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict

from .code_analyzer import analyze_file, MethodInfo
from .llm_client import LLMClient
from .metrics import execute_test, calculate_pass_at_k, EvaluationResult


@dataclass
class TestResult:
    """Result of test generation and evaluation for a method."""
    method_name: str
    class_name: Optional[str]
    generated_test: str
    passed: bool
    error: Optional[str] = None


@dataclass 
class FrameworkResult:
    """Overall result from the framework."""
    source_file: str
    test_directory: str
    methods_tested: int
    tests_passed: int
    tests_failed: int
    pass_rate: float
    results: List[TestResult]


class TestFramework:
    """Framework for generating and evaluating tests for custom projects."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
    
    def generate_tests_for_file(
        self,
        source_file: str,
        test_directory: str,
        method_names: Optional[List[str]] = None,
        run_tests: bool = True,
    ) -> FrameworkResult:
        """
        Generate tests for methods in a Python file.
        
        Args:
            source_file: Path to the source Python file
            test_directory: Directory where tests will be saved
            method_names: Optional list of specific methods to test
            run_tests: Whether to run and evaluate the generated tests
            
        Returns:
            FrameworkResult with generation and evaluation results
        """
        source_path = Path(source_file)
        test_dir = Path(test_directory)
        
        # Create test directory if it doesn't exist
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # Analyze source file
        methods = analyze_file(str(source_path), method_names)
        
        if not methods:
            raise ValueError(f"No methods found in {source_file}")
        
        print(f"📝 Found {len(methods)} methods to test")
        
        results = []
        
        for method in methods:
            print(f"   Generating tests for: {method.name}")
            
            try:
                # Generate test using LLM
                test_code = self._generate_test_for_method(method, source_path)
                
                # Save test file
                test_file = self._save_test(method, test_code, test_dir, source_path)
                
                # Evaluate if requested
                passed = False
                error = None
                
                if run_tests:
                    eval_result = execute_test(test_code, method.source)
                    passed = eval_result.passed
                    error = eval_result.error
                
                results.append(TestResult(
                    method_name=method.name,
                    class_name=method.class_name,
                    generated_test=test_code,
                    passed=passed,
                    error=error,
                ))
                
            except Exception as e:
                results.append(TestResult(
                    method_name=method.name,
                    class_name=method.class_name,
                    generated_test="",
                    passed=False,
                    error=str(e),
                ))
        
        # Calculate statistics
        passed_count = sum(1 for r in results if r.passed)
        failed_count = len(results) - passed_count
        pass_rate = passed_count / len(results) if results else 0
        
        return FrameworkResult(
            source_file=str(source_path),
            test_directory=str(test_dir),
            methods_tested=len(results),
            tests_passed=passed_count,
            tests_failed=failed_count,
            pass_rate=pass_rate,
            results=results,
        )
    
    def _generate_test_for_method(self, method: MethodInfo, source_path: Path) -> str:
        """Generate test code for a specific method."""
        prompt = self._create_prompt(method, source_path)
        response = self.llm.generate_tests(method.source, prompt)
        return self.llm.extract_code(response)
    
    def _create_prompt(self, method: MethodInfo, source_path: Path) -> str:
        """Create a prompt for test generation."""
        context = f"File: {source_path.name}"
        if method.class_name:
            context += f"\nClass: {method.class_name}"
        if method.docstring:
            context += f"\nDocstring: {method.docstring}"
        
        return f"""Generate comprehensive pytest unit tests for the following Python method.

{context}

Requirements:
1. Use pytest framework
2. Test normal cases, edge cases, and error conditions
3. Use descriptive test names
4. Make tests self-contained and executable
5. Import the method from the source file

Code:
```python
{{code}}
```

Generate only the test code, no explanations."""

    def _save_test(
        self, 
        method: MethodInfo, 
        test_code: str, 
        test_dir: Path,
        source_path: Path,
    ) -> Path:
        """Save generated test to a file."""
        # Create test filename
        if method.class_name:
            test_filename = f"test_{method.class_name.lower()}_{method.name}.py"
        else:
            test_filename = f"test_{method.name}.py"
        
        test_file = test_dir / test_filename
        
        # Add import statement
        module_name = source_path.stem
        full_test = f"# Auto-generated test for {method.name}\n"
        full_test += f"import sys\n"
        full_test += f"sys.path.insert(0, '{source_path.parent.as_posix()}')\n"
        full_test += f"from {module_name} import *\n\n"
        full_test += test_code
        
        test_file.write_text(full_test, encoding="utf-8")
        return test_file


def run_framework(
    source_file: str,
    test_directory: str,
    method_names: Optional[List[str]] = None,
    run_tests: bool = True,
) -> FrameworkResult:
    """
    Run the test generation framework.
    
    Args:
        source_file: Path to source Python file
        test_directory: Directory for generated tests
        method_names: Optional specific methods to test
        run_tests: Whether to run tests after generation
        
    Returns:
        FrameworkResult with all results
    """
    framework = TestFramework()
    return framework.generate_tests_for_file(
        source_file=source_file,
        test_directory=test_directory,
        method_names=method_names,
        run_tests=run_tests,
    )
