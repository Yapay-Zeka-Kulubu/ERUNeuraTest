# Configuration settings for the unit test automation system
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).parent.parent
BENCHMARK_DIR = BASE_DIR / "benchmark"

# Groq API Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

# Benchmark paths
BENCHMARKS = {
    "leetcode_contest": BENCHMARK_DIR / "leetcode_contest",
    "ult": BENCHMARK_DIR / "ult",
    "projecttest": BENCHMARK_DIR / "projecttest",
    "deveval": BENCHMARK_DIR / "deveval",
}

# HuggingFace dataset names
HF_DATASETS = {
    "leetcode_contest": "TechxGenus/LeetCode-Contest",
    "projecttest": "yibowang214/ProjectTest",
}

# Model generation settings
GENERATION_CONFIG = {
    "temperature": 0.2,
    "max_tokens": 2048,
    "top_p": 0.95,
}

# Metrics configuration
METRICS = {
    "pass_k": [1, 3, 5, 10],
    "recall_k": [1, 3, 5, 10],
}
