import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reviewer.pipeline import run_reviewer

if __name__ == "__main__":
    file_path = "files/one_line_test.java"
    
    with open(file_path, "r") as f:
        code = f.read()
    
    print("=" * 60)
    print("ONE LINE TEST")
    print("=" * 60)
    print(f"\nCode:\n{code}")
    print("\nRunning LLM review...")
    
    try:
        comments = run_reviewer(file_path, code, enable_llm=True)
        
        print("\n[RESULTS]")
        for c in comments:
            print(f"\n[{c.source.value}] {c.rule_id} (Line {c.line_number})")
            print(f"Severity: {c.severity.value}")
            print(f"Message: {c.message}")
    except Exception as e:
        print(f"Error: {e}")
