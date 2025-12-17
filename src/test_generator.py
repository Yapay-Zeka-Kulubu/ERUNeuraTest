# Test generator pipeline
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from .llm_client import LLMClient
from .dataset_loader import DatasetLoader


@dataclass
class GeneratedTest:
    """Container for generated test results."""
    task_id: str
    original_code: str
    generated_tests: str
    prompt: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class TestGenerator:
    """Main test generation pipeline."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm = llm_client or LLMClient()
    
    def generate_for_problem(self, problem: Dict[str, Any]) -> GeneratedTest:
        """Generate tests for a single problem."""
        # Extract code from problem (handle different dataset formats)
        code = self._extract_code(problem)
        task_id = self._extract_task_id(problem)
        
        # Generate tests using LLM
        response = self.llm.generate_tests(code)
        test_code = self.llm.extract_code(response)
        
        return GeneratedTest(
            task_id=task_id,
            original_code=code,
            generated_tests=test_code,
            prompt=problem.get("prompt"),
            metadata=problem,
        )
    
    def generate_batch(
        self, 
        problems: List[Dict[str, Any]], 
        n_samples: int = 1
    ) -> List[List[GeneratedTest]]:
        """Generate tests for multiple problems with n samples each."""
        results = []
        
        for problem in problems:
            samples = []
            for _ in range(n_samples):
                try:
                    result = self.generate_for_problem(problem)
                    samples.append(result)
                except Exception as e:
                    print(f"Error generating for {self._extract_task_id(problem)}: {e}")
            results.append(samples)
        
        return results
    
    def _extract_code(self, problem: Dict[str, Any]) -> str:
        """Extract code from problem based on dataset format."""
        # LeetCode-Contest format
        if "prompt" in problem:
            return problem["prompt"]
        # DevEval format
        if "canonical_solution" in problem:
            return problem.get("prompt", "") + problem["canonical_solution"]
        # ProjectTest format
        if "code" in problem:
            return problem["code"]
        # Fallback
        return problem.get("content", str(problem))
    
    def _extract_task_id(self, problem: Dict[str, Any]) -> str:
        """Extract task ID from problem."""
        for key in ["task_id", "id", "namespace", "problem_id"]:
            if key in problem:
                return str(problem[key])
        return "unknown"


def run_generation_pipeline(
    benchmark: str,
    limit: Optional[int] = None,
    n_samples: int = 1,
) -> List[List[GeneratedTest]]:
    """Run the full generation pipeline for a benchmark."""
    loader = DatasetLoader(benchmark)
    generator = TestGenerator()
    
    problems = loader.load(limit=limit)
    print(f"Loaded {len(problems)} problems from {benchmark}")
    
    results = generator.generate_batch(problems, n_samples=n_samples)
    return results
