import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.reviewer.pipeline import run_reviewer

if __name__ == "__main__":
    file_path = "files/minimal_test.java"
    
    print("=" * 80)
    print("MINIMAL TEST - LLM SEMANTIC REVIEW")
    print("=" * 80)
    print(f"\nFile: {file_path}")
    print(f"Size: {len(open(file_path).readlines())} lines")
    
    with open(file_path, "r") as f:
        code = f.read()
    
    print("\n[CODE]")
    print(code)
    
    print("\n[STATIC ANALYSIS]")
    static_comments = run_reviewer(file_path, code, enable_llm=False)
    for c in static_comments:
        if c.rule_id != "NO_ISSUES":
            print(f"  [{c.source.value}] Line {c.line_number}: {c.message}")
    
    print("\n[LLM SEMANTIC ANALYSIS]")
    print("Sending to LLM for review...")
    try:
        llm_comments = run_reviewer(file_path, code, enable_llm=True)
        llm_only = [c for c in llm_comments if c.rule_id.startswith("LLM_")]
        
        if llm_only:
            for c in llm_only:
                print(f"  [{c.source.value}] Line {c.line_number}: [{c.rule_id}]")
                print(f"    Message: {c.message}")
        else:
            print("  No LLM issues found")
    except Exception as e:
        print(f"  Error: {e}")
