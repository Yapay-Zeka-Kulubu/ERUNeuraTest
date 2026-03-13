"""python -m src.preprocess komutuyla çalıştırma noktası."""

import warnings
warnings.filterwarnings("ignore", category=SyntaxWarning)

from .scanner import ProjectScanner

scanner = ProjectScanner()
scanner.run()