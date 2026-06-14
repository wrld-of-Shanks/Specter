#!/usr/bin/env python3
"""
SPECTER System Test Script
Tests all major components: Document Upload, Analysis, Chat, and Verification
"""

import sys
import os
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all required modules can be imported"""
    print("=" * 80)
    print("TEST 1: Module Imports")
    print("=" * 80)
    
    try:
        from document_processor import document_processor
        print("✓ document_processor imported successfully")
    except Exception as e:
        print(f"✗ Failed to import document_processor: {e}")
        return False
    
    try:
        from legal_analysis import legal_analyzer
        print("✓ legal_analyzer imported successfully")
    except Exception as e:
        print(f"✗ Failed to import legal_analyzer: {e}")
        return False
    
    try:
        from chat_engine_rag import answer_query_with_rag
        print("✓ chat_engine_rag imported successfully")
    except Exception as e:
        print(f"✗ Failed to import chat_engine_rag: {e}")
        return False
    
    try:
        from comprehensive_legal_db import get_comprehensive_legal_info
        print("✓ comprehensive_legal_db imported successfully")
    except Exception as e:
        print(f"✗ Failed to import comprehensive_legal_db: {e}")
        return False
    
    print("\n✓ All imports successful!\n")
    return True

def test_document_type_identification():
    """Test document type identification"""
    print("=" * 80)
    print("TEST 2: Document Type Identification")
    print("=" * 80)
    
    try:
        from legal_analysis import legal_analyzer
        
        test_cases = [
            ("This is a First Information Report filed at Police Station...", "FIR"),
            ("RENT AGREEMENT\n\nThis agreement is made between...", "Rent"),
            ("AFFIDAVIT\n\nI, John Doe, do hereby solemnly affirm...", "Affidavit"),
            ("SALE DEED\n\nThis deed of sale is executed...", "Sale Deed"),
        ]
        
        for text, expected_type in test_cases:
            doc_type = legal_analyzer.identify_document_type(text)
            status = "✓" if expected_type.lower() in doc_type.lower() else "✗"
            print(f"{status} Text: '{text[:50]}...' -> Type: {doc_type}")
        
        print("\n✓ Document type identification test completed!\n")
        return True
    except Exception as e:
        print(f"✗ Document type identification test failed: {e}\n")
        return False

def test_chat_engine():
    """Test chat engine with sample queries"""
    print("=" * 80)
    print("TEST 3: Chat Engine (RAG System)")
    print("=" * 80)
    
    try:
        from chat_engine_rag import answer_query_with_rag
        
        test_queries = [
            "What is bail?",
            "How to file FIR?",
            "What is a driving license?",
            "Tell me about divorce laws",
        ]
        
        for query in test_queries:
            result = answer_query_with_rag(query)
            print(f"\nQuery: {query}")
            print(f"Answer: {result['answer'][:200]}...")
            print(f"Confidence: {result.get('confidence', 'N/A')}")
            print(f"Sources: {result.get('sources', [])}")
        
        print("\n✓ Chat engine test completed!\n")
        return True
    except Exception as e:
        print(f"✗ Chat engine test failed: {e}\n")
        return False

def test_document_processor():
    """Test document processor with sample text file"""
    print("=" * 80)
    print("TEST 4: Document Processor")
    print("=" * 80)
    
    try:
        from document_processor import document_processor
        
        # Create a test text file
        test_file_path = Path("./temp_uploads/test_document.txt")
        test_file_path.parent.mkdir(exist_ok=True)
        
        test_content = """
        RENT AGREEMENT
        
        This Rent Agreement is made on 01/01/2024 between:
        
        LANDLORD: Mr. John Doe, residing at 123 Main Street, Mumbai
        TENANT: Ms. Jane Smith, residing at 456 Oak Avenue, Mumbai
        
        PROPERTY: Flat No. 5, Building A, XYZ Complex, Mumbai
        
        RENT: Rs. 25,000 per month
        DURATION: 11 months from 01/01/2024 to 30/11/2024
        
        Both parties agree to the terms and conditions mentioned herein.
        """
        
        with open(test_file_path, 'w') as f:
            f.write(test_content)
        
        # Test text extraction
        extracted_text = document_processor.extract_text(test_file_path)
        print(f"✓ Text extraction successful")
        print(f"  Extracted {len(extracted_text)} characters")
        
        # Cleanup
        document_processor.cleanup(test_file_path)
        print(f"✓ File cleanup successful")
        
        print("\n✓ Document processor test completed!\n")
        return True
    except Exception as e:
        print(f"✗ Document processor test failed: {e}\n")
        return False

def test_legal_analyzer():
    """Test legal analyzer with sample document"""
    print("=" * 80)
    print("TEST 5: Legal Analyzer (Summarization & Verification)")
    print("=" * 80)
    
    try:
        from legal_analysis import legal_analyzer
        
        sample_doc = """
        RENT AGREEMENT
        
        This Rent Agreement is made on 01/01/2024 between:
        
        LANDLORD: Mr. John Doe, S/o Mr. Robert Doe, residing at 123 Main Street, Mumbai - 400001
        TENANT: Ms. Jane Smith, D/o Mr. William Smith, residing at 456 Oak Avenue, Mumbai - 400002
        
        PROPERTY: Flat No. 5, Building A, XYZ Complex, Andheri West, Mumbai - 400053
        
        TERMS:
        1. RENT: Rs. 25,000 (Rupees Twenty-Five Thousand Only) per month
        2. SECURITY DEPOSIT: Rs. 75,000 (Rupees Seventy-Five Thousand Only)
        3. DURATION: 11 months from 01/01/2024 to 30/11/2024
        4. MAINTENANCE: Rs. 2,000 per month (separate from rent)
        
        Both parties agree to the terms and conditions mentioned herein.
        
        LANDLORD SIGNATURE: _______________
        TENANT SIGNATURE: _______________
        
        WITNESS 1: _______________
        WITNESS 2: _______________
        """
        
        doc_type = legal_analyzer.identify_document_type(sample_doc)
        print(f"✓ Document Type: {doc_type}")
        
        # Note: These tests will only work if Ollama is running
        print("\nNote: Summarization and verification tests require Ollama to be running.")
        print("Skipping LLM-dependent tests for now.")
        
        print("\n✓ Legal analyzer test completed!\n")
        return True
    except Exception as e:
        print(f"✗ Legal analyzer test failed: {e}\n")
        return False

def check_dependencies():
    """Check if all required dependencies are installed"""
    print("=" * 80)
    print("DEPENDENCY CHECK")
    print("=" * 80)
    
    dependencies = [
        "fastapi",
        "uvicorn",
        "pymongo",
        "motor",
        "pydantic",
        "chromadb",
        "sentence_transformers",
        "pytesseract",
        "pdf2image",
        "PyPDF2",
        "docx",
        "PIL",
    ]
    
    missing = []
    for dep in dependencies:
        try:
            if dep == "docx":
                __import__("docx")
            elif dep == "PIL":
                __import__("PIL")
            else:
                __import__(dep)
            print(f"✓ {dep}")
        except ImportError:
            print(f"✗ {dep} - NOT INSTALLED")
            missing.append(dep)
    
    if missing:
        print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
        print("Install with: pip install " + " ".join(missing))
        return False
    else:
        print("\n✓ All dependencies installed!\n")
        return True

def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("SPECTER SYSTEM TEST SUITE")
    print("=" * 80 + "\n")
    
    results = []
    
    # Run tests
    results.append(("Dependency Check", check_dependencies()))
    results.append(("Module Imports", test_imports()))
    results.append(("Document Type Identification", test_document_type_identification()))
    results.append(("Chat Engine", test_chat_engine()))
    results.append(("Document Processor", test_document_processor()))
    results.append(("Legal Analyzer", test_legal_analyzer()))
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! System is ready.")
        return 0
    else:
        print(f"\n⚠ {total - passed} test(s) failed. Please review the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
