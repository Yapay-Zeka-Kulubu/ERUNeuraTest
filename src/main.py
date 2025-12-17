# CLI entry point for unit test automation
import argparse
import json
from pathlib import Path
from .dataset_loader import DatasetLoader, list_available_benchmarks
from .test_generator import TestGenerator, run_generation_pipeline
from .metrics import evaluate_generated_tests
from .config import BENCHMARKS
from .framework import run_framework


def main():
    parser = argparse.ArgumentParser(
        description="ERUNeuraTest - Unit Test Automation Framework with LLM"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Test command (Framework mode) - NEW
    test_parser = subparsers.add_parser("test", help="Generate tests for your project files")
    test_parser.add_argument(
        "--file", "-f",
        type=str,
        required=True,
        help="Path to Python source file"
    )
    test_parser.add_argument(
        "--output", "-o",
        type=str,
        required=True,
        help="Directory for generated tests"
    )
    test_parser.add_argument(
        "--methods", "-m",
        type=str,
        nargs="*",
        help="Specific method names to test (optional, tests all if not specified)"
    )
    test_parser.add_argument(
        "--no-eval",
        action="store_true",
        help="Skip running and evaluating tests"
    )
    
    # Generate command (Benchmark mode)
    gen_parser = subparsers.add_parser("generate", help="Generate tests from benchmark datasets")
    gen_parser.add_argument(
        "--benchmark", "-b",
        choices=list_available_benchmarks(),
        required=True,
        help="Benchmark dataset to use"
    )
    gen_parser.add_argument(
        "--limit", "-l",
        type=int,
        default=10,
        help="Number of problems to process (default: 10)"
    )
    gen_parser.add_argument(
        "--samples", "-n",
        type=int,
        default=1,
        help="Number of samples per problem (default: 1)"
    )
    gen_parser.add_argument(
        "--output", "-o",
        type=str,
        default="output.jsonl",
        help="Output file path"
    )
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Evaluate generated tests")
    eval_parser.add_argument(
        "--input", "-i",
        type=str,
        required=True,
        help="Input file with generated tests"
    )
    eval_parser.add_argument(
        "--k",
        type=int,
        nargs="+",
        default=[1, 3, 5, 10],
        help="k values for Pass@k"
    )
    
    # Download command
    dl_parser = subparsers.add_parser("download", help="Download benchmark datasets")
    dl_parser.add_argument(
        "--benchmark", "-b",
        choices=list_available_benchmarks(),
        required=True,
        help="Benchmark to download"
    )
    
    # List command
    subparsers.add_parser("list", help="List available benchmarks")
    
    args = parser.parse_args()
    
    if args.command == "test":
        run_test(args)
    elif args.command == "generate":
        run_generate(args)
    elif args.command == "evaluate":
        run_evaluate(args)
    elif args.command == "download":
        run_download(args)
    elif args.command == "list":
        run_list()
    else:
        parser.print_help()


def run_test(args):
    """Run framework mode for custom project testing."""
    print(f"🧪 ERUNeuraTest Framework")
    print(f"   Source: {args.file}")
    print(f"   Output: {args.output}")
    if args.methods:
        print(f"   Methods: {', '.join(args.methods)}")
    
    result = run_framework(
        source_file=args.file,
        test_directory=args.output,
        method_names=args.methods,
        run_tests=not args.no_eval,
    )
    
    print("\n" + "=" * 50)
    print("📊 Results")
    print("=" * 50)
    print(f"   Methods tested: {result.methods_tested}")
    print(f"   Tests passed:   {result.tests_passed}")
    print(f"   Tests failed:   {result.tests_failed}")
    print(f"   Pass@1:         {result.pass_rate:.2%}")
    print(f"\n✅ Tests saved to: {result.test_directory}")
    
    # Show individual results
    if result.results:
        print("\n📝 Details:")
        for r in result.results:
            status = "✅" if r.passed else "❌"
            name = f"{r.class_name}.{r.method_name}" if r.class_name else r.method_name
            print(f"   {status} {name}")
            if r.error and not r.passed:
                print(f"      Error: {r.error[:100]}...")



def run_generate(args):
    """Run test generation pipeline."""
    print(f"🚀 Starting test generation for {args.benchmark}")
    print(f"   Limit: {args.limit} problems, {args.samples} samples each")
    
    results = run_generation_pipeline(
        benchmark=args.benchmark,
        limit=args.limit,
        n_samples=args.samples,
    )
    
    # Save results
    output_path = Path(args.output)
    with open(output_path, "w", encoding="utf-8") as f:
        for problem_results in results:
            for result in problem_results:
                data = {
                    "task_id": result.task_id,
                    "generated_tests": result.generated_tests,
                    "original_code": result.original_code,
                }
                f.write(json.dumps(data, ensure_ascii=False) + "\n")
    
    print(f"✅ Generated tests saved to {output_path}")
    print(f"   Total: {sum(len(p) for p in results)} samples")


def run_evaluate(args):
    """Run evaluation on generated tests."""
    print(f"📊 Evaluating tests from {args.input}")
    
    # Load generated tests
    results = []
    with open(args.input, "r", encoding="utf-8") as f:
        current_problem = []
        for line in f:
            data = json.loads(line)
            # Simple grouping - one sample per problem for now
            from .test_generator import GeneratedTest
            result = GeneratedTest(
                task_id=data["task_id"],
                original_code=data["original_code"],
                generated_tests=data["generated_tests"],
            )
            results.append([result])
    
    metrics = evaluate_generated_tests(results, k_values=args.k)
    
    print("\n" + "=" * 50)
    print("📈 Evaluation Results")
    print("=" * 50)
    
    for k in args.k:
        key = f"pass@{k}"
        if key in metrics:
            print(f"   Pass@{k}: {metrics[key]:.4f}")
    
    print(f"\n   Total problems: {metrics['total_problems']}")
    print(f"   Total samples: {metrics['total_samples']}")
    print(f"   Pass rate: {metrics['pass_rate']:.2%}")


def run_download(args):
    """Download benchmark dataset."""
    print(f"⬇️ Downloading {args.benchmark}...")
    
    loader = DatasetLoader(args.benchmark)
    try:
        output_path = loader.download_to_local()
        print(f"✅ Downloaded to {output_path}")
    except Exception as e:
        print(f"❌ Error: {e}")


def run_list():
    """List available benchmarks."""
    print("📚 Available Benchmarks:")
    print("-" * 40)
    
    for name, path in BENCHMARKS.items():
        status = "✅" if path.exists() else "❌"
        print(f"   {status} {name}: {path}")


if __name__ == "__main__":
    main()
