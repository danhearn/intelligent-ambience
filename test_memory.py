#!/usr/bin/env python3
"""
Test script to verify vector memory persistence
"""

from tools.vector_memory_tools import vector_memory_instance, add_to_vector_store, search_vector_store

def test_memory_persistence():
    print("Testing vector memory persistence...")
    
    # Test adding data
    print("1. Adding test data...")
    result = add_to_vector_store.invoke({"text": "This is a test memory entry for the intelligent ambience system"})
    print(f"   Result: {result}")
    
    # Test searching data
    print("2. Searching for similar data...")
    results = search_vector_store.invoke({"text": "test memory", "k": 3})
    print(f"   Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result}")
    
    # Check if database files exist
    import os
    db_path = "./chroma_langchain_db"
    if os.path.exists(db_path):
        print(f"3. Database directory exists: {os.path.abspath(db_path)}")
        files = os.listdir(db_path)
        print(f"   Files in database: {files}")
    else:
        print("3. Database directory does not exist!")
    
    print("Test completed!")

if __name__ == "__main__":
    test_memory_persistence()
