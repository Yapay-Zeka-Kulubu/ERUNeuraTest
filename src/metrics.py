# Metrics calculation: Pass@k, Coverage, Mutation Score
import math
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class EvaluationResult:
    task_id: str
    passed: bool
    error: Optional[str] = None
    coverage: Optional[float] = None
    mutation_score: Optional[float] = None


def pass_at_k(n: int, c: int, k: int) -> float:

    if n - c < k:
        return 1.0
    return 1.0 - math.prod((n - c - i) / (n - i) for i in range(k))


def calculate_pass_at_k(
    results: List[List[EvaluationResult]], 
    k_values: List[int] = [1, 3, 5, 10]
) -> Dict[str, float]:

    metrics = {}
    
    for k in k_values:
        pass_k_values = []
        
        for problem_results in results:
            n = len(problem_results)
            c = sum(1 for r in problem_results if r.passed)
            
            if n >= k:
                pass_k_values.append(pass_at_k(n, c, k))
        
        if pass_k_values:
            metrics[f"pass@{k}"] = np.mean(pass_k_values)
    
    return metrics


def execute_test(test_code: str, original_code: str, timeout: int = 10) -> EvaluationResult:

    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Write original code
        code_file = tmpdir / "solution.py"
        code_file.write_text(original_code, encoding="utf-8")
        
        # Write test code with import
        test_file = tmpdir / "test_solution.py"
        full_test = f"from solution import *\n\n{test_code}"
        test_file.write_text(full_test, encoding="utf-8")
        
        try:
            # Use sys.executable to ensure we use the same Python interpreter
            result = subprocess.run(
                [sys.executable, "-m", "pytest", str(test_file), "-v", "--tb=short"],
                cwd=tmpdir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            
            passed = result.returncode == 0
            error = None if passed else result.stdout + result.stderr
            
            return EvaluationResult(
                task_id="",
                passed=passed,
                error=error,
            )
        
        except subprocess.TimeoutExpired:
            return EvaluationResult(
                task_id="",
                passed=False,
                error="Timeout expired",
            )
        except Exception as e:
            return EvaluationResult(
                task_id="",
                passed=False,
                error=str(e),
            )


def evaluate_generated_tests(
    generated_results: List[Dict[str, Any]],
    k_values: List[int] = [1, 3, 5, 10],
) -> Dict[str, Any]:
    all_eval_results = []
    
    for problem_samples in generated_results:
        problem_evals = []
        for sample in problem_samples:
            eval_result = execute_test(
                sample.generated_tests,
                sample.original_code,
            )
            eval_result.task_id = sample.task_id
            problem_evals.append(eval_result)
        all_eval_results.append(problem_evals)
    
    # Calculate Pass@k
    metrics = calculate_pass_at_k(all_eval_results, k_values)
    
    # Add summary stats
    total_problems = len(all_eval_results)
    total_samples = sum(len(p) for p in all_eval_results)
    total_passed = sum(
        sum(1 for r in p if r.passed) 
        for p in all_eval_results
    )
    
    metrics["total_problems"] = total_problems
    metrics["total_samples"] = total_samples
    metrics["total_passed"] = total_passed
    metrics["pass_rate"] = total_passed / total_samples if total_samples > 0 else 0
    
    return metrics
