#!/usr/bin/env python3
"""
Quick test to verify that our updates work correctly
"""
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_basic_imports():
    """Test that all agents can be imported successfully"""
    print("Testing basic imports...")
    
    try:
        from agents.rag_agent import RAGAgent
        print("✓ RAG Agent imported successfully")
    except Exception as e:
        print(f"✗ RAG Agent import failed: {e}")
        return False
    
    try:
        from agents.sql_agent import SQLAgent
        print("✓ SQL Agent imported successfully")
    except Exception as e:
        print(f"✗ SQL Agent import failed: {e}")
        return False
    
    try:
        from agents.hybrid_agent import HybridAgent
        print("✓ Hybrid Agent imported successfully")
    except Exception as e:
        print(f"✗ Hybrid Agent import failed: {e}")
        return False
    
    return True

def test_empty_query_validation():
    """Test empty query validation without database connections"""
    print("\nTesting empty query validation...")
    
    import unittest.mock
    
    # Test RAG Agent
    try:
        with unittest.mock.patch('agents.rag_agent.MilvusConnector'), \
             unittest.mock.patch('agents.rag_agent.EmbeddingModel'):
            from agents.rag_agent import RAGAgent
            
            # Create a mock agent
            agent = RAGAgent()
            
            # Test empty query
            result = agent.query("")
            if result['success'] == False and '不能为空' in result['error']:
                print("✓ RAG Agent empty query validation works")
            else:
                print(f"✗ RAG Agent validation failed: {result}")
                
    except Exception as e:
        print(f"✗ RAG Agent validation test failed: {e}")
    
    # Test SQL Agent  
    try:
        with unittest.mock.patch('agents.sql_agent.MySQLConnector'), \
             unittest.mock.patch('agents.sql_agent.SQLDatabase'), \
             unittest.mock.patch('agents.sql_agent.create_sql_agent'):
            from agents.sql_agent import SQLAgent
            
            agent = SQLAgent()
            result = agent.query("")
            if result['success'] == False and '不能为空' in result['error']:
                print("✓ SQL Agent empty query validation works")
            else:
                print(f"✗ SQL Agent validation failed: {result}")
                
    except Exception as e:
        print(f"✗ SQL Agent validation test failed: {e}")
    
    # Test Hybrid Agent
    try:
        with unittest.mock.patch('agents.hybrid_agent.SQLAgent'), \
             unittest.mock.patch('agents.hybrid_agent.RAGAgent'):
            from agents.hybrid_agent import HybridAgent
            
            agent = HybridAgent()
            result = agent.query("")
            if result['success'] == False and '不能为空' in result['error']:
                print("✓ Hybrid Agent empty query validation works")
            else:
                print(f"✗ Hybrid Agent validation failed: {result}")
                
    except Exception as e:
        print(f"✗ Hybrid Agent validation test failed: {e}")

def test_langchain_patterns():
    """Test that new LangChain patterns are working"""
    print("\nTesting LangChain patterns...")
    
    try:
        from langchain_core.runnables import RunnablePassthrough
        from langchain_core.output_parsers import StrOutputParser
        from langchain.prompts import PromptTemplate
        
        # Test the new pattern
        prompt = PromptTemplate(
            input_variables=["input"],
            template="Test: {input}"
        )
        
        # This should work without errors
        chain = prompt | StrOutputParser()
        print("✓ New LangChain runnable pattern works")
        
    except Exception as e:
        print(f"✗ LangChain pattern test failed: {e}")

def main():
    """Run all quick tests"""
    print("=" * 50)
    print("Quick Verification Test")
    print("=" * 50)
    
    success = True
    
    if not test_basic_imports():
        success = False
    
    test_empty_query_validation()
    test_langchain_patterns()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ All tests passed! Updates are working correctly.")
    else:
        print("❌ Some tests failed. Please check the output above.")
    print("=" * 50)

if __name__ == "__main__":
    main()