import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.engine.vi_grammar_rewriter import rewrite_vietnamese_grammar

test_cases = [
    ("Một người mặc màu đen áo gió nam tử quỳ gối lạng ghế ngồi bia mộ trước mặt", "Complex Reorder & Misc"),
    ("lạng ghế ngồi bia mộ", "Misc measure word"),
    ("người mặc màu đen áo gió thiếu niên", "Adj Noun Reorder 2"),
]

print("--- DEBUG RESULTS ---")
for text, label in test_cases:
    result = rewrite_vietnamese_grammar(text, genre="modern")
    print(f"[{label}]")
    print(f"  Source: {text}")
    print(f"  Result: {result}")
    print("-" * 20)
