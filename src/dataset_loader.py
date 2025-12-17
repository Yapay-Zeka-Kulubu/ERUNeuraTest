# Dataset loader for benchmarks
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datasets import load_dataset
from .config import BENCHMARKS, HF_DATASETS


class DatasetLoader:
    """Loader for benchmark datasets."""
    
    def __init__(self, benchmark_name: str):
        self.benchmark_name = benchmark_name
        self.data_path = BENCHMARKS.get(benchmark_name)
        self.hf_name = HF_DATASETS.get(benchmark_name)
    
    def load(self, split: str = "train", limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Load dataset from HuggingFace or local path."""
        if self.hf_name:
            return self._load_from_huggingface(split, limit)
        elif self.data_path and self.data_path.exists():
            return self._load_from_local(limit)
        else:
            raise ValueError(f"Dataset '{self.benchmark_name}' not found")
    
    def _load_from_huggingface(self, split: str, limit: Optional[int]) -> List[Dict[str, Any]]:
        """Load dataset from HuggingFace."""
        dataset = load_dataset(self.hf_name, split=split)
        
        if limit:
            dataset = dataset.select(range(min(limit, len(dataset))))
        
        return [dict(item) for item in dataset]
    
    def _load_from_local(self, limit: Optional[int]) -> List[Dict[str, Any]]:
        """Load dataset from local JSONL file."""
        data = []
        jsonl_files = list(self.data_path.glob("*.jsonl"))
        
        for jsonl_file in jsonl_files:
            with open(jsonl_file, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        data.append(json.loads(line))
                        if limit and len(data) >= limit:
                            return data
        
        return data
    
    def download_to_local(self, split: str = "train") -> Path:
        """Download HuggingFace dataset to local benchmark folder."""
        if not self.hf_name:
            raise ValueError(f"No HuggingFace dataset for '{self.benchmark_name}'")
        
        self.data_path.mkdir(parents=True, exist_ok=True)
        
        dataset = load_dataset(self.hf_name, split=split)
        output_file = self.data_path / f"{split}.jsonl"
        
        with open(output_file, "w", encoding="utf-8") as f:
            for item in dataset:
                f.write(json.dumps(dict(item), ensure_ascii=False) + "\n")
        
        print(f"Downloaded {len(dataset)} samples to {output_file}")
        return output_file


def list_available_benchmarks() -> List[str]:
    """List all available benchmark names."""
    return list(BENCHMARKS.keys())
