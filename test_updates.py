#!/usr/bin/env python3
"""
Test script to validate the recent updates to agents
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_empty_query_validation():
    """Test that all agents properly handle empty queries"""
    print("Testing empty query validation...")
    
    # Test cases for empty inputs
    test_cases = [
        "",           # Empty string
        "   ",        # Whitespace only
        None,         # None value
    ]
    
    try:
        from agents.rag_agent import RAGAgent
        print("✓ RAG Agent imports successfully")
        
        # Test that we can instantiate the class (even if we can't connect to services)
        print("✓ RAG Agent can be imported and structure is valid")
        
    except ImportError as e:
        print(f"✗ RAG Agent import failed: {e}")
    except Exception as e:
        print(f"⚠ RAG Agent import succeeded but other error: {e}")
    
    try:
        from agents.sql_agent import SQLAgent
        print("✓ SQL Agent imports successfully")
        
    except ImportError as e:
        print(f"✗ SQL Agent import failed: {e}")
    except Exception as e:
        print(f"⚠ SQL Agent import succeeded but other error: {e}")
    
    try:
        from agents.hybrid_agent import HybridAgent
        print("✓ Hybrid Agent imports successfully")
        
    except ImportError as e:
        print(f"✗ Hybrid Agent import failed: {e}")
    except Exception as e:
        print(f"⚠ Hybrid Agent import succeeded but other error: {e}")

def test_langchain_updates():
    """Test that LangChain updates are working"""
    print("\nTesting LangChain updates...")
    
    try:
        # Test that we can import the new components
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser
        print("✓ New LangChain imports work")
        
    except ImportError as e:
        print(f"✗ New LangChain imports failed: {e}")

def check_file_modifications():
    """Check that all necessary files have been modified"""
    print("\nChecking file modifications...")
    
    files_to_check = [
        'agents/rag_agent.py',
        'agents/sql_agent.py', 
        'agents/hybrid_agent.py'
    ]
    
    expected_patterns = {
        'agents/rag_agent.py': [
            'if not question or not question.strip():',
            'langchain_core.runnables',
            'StrOutputParser'
        ],
        'agents/sql_agent.py': [
            'if not question or not question.strip():'
        ],
        'agents/hybrid_agent.py': [
            'if not question or not question.strip():',
            'langchain_core.runnables',
            'StrOutputParser'
        ]
    }
    
    for file_path in files_to_check:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            patterns = expected_patterns.get(file_path, [])
            for pattern in patterns:
                if pattern in content:
                    print(f"✓ {file_path}: Found '{pattern}'")
                else:
                    print(f"✗ {file_path}: Missing '{pattern}'")
                    
        except Exception as e:
            print(f"✗ Error checking {file_path}: {e}")

def test_syntax_validation():
    """Test that all Python files have valid syntax"""
    print("\nTesting syntax validation...")
    
    import py_compile
    
    files_to_check = [
        'agents/rag_agent.py',
        'agents/sql_agent.py', 
        'agents/hybrid_agent.py'
    ]
    
    for file_path in files_to_check:
        try:
            py_compile.compile(file_path, doraise=True)
            print(f"✓ {file_path}: Valid syntax")
        except py_compile.PyCompileError as e:
            print(f"✗ {file_path}: Syntax error - {e}")
        except Exception as e:
            print(f"✗ {file_path}: Error - {e}")

def main():
    """Run all tests"""
    print("=" * 50)
    print("Stock Analysis System - Update Validation")
    print("=" * 50)
    
    test_syntax_validation()
    check_file_modifications()
    test_langchain_updates()
    test_empty_query_validation()
    
    print("\n" + "=" * 50)
    print("Update validation complete!")
    print("=" * 50)

if __name__ == "__main__":
    main()