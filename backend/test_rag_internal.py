import asyncio
import os
import pymongo
from dotenv import load_dotenv
load_dotenv()

# We need to run this async
async def test_rag():
    print("Testing internal RAG context retrieval...")
    from teacher_chat import _get_curriculum_context
    
    query = "Vis meg en video om bremselengde og reaksjonstid"
    print(f"Query: '{query}'")
    context = await _get_curriculum_context(query, "no")
    print("\n--- RETRIEVED CONTEXT ---")
    print(context)
    print("-------------------------")
    
    if "Learning Video:" in context:
        print("✅ SUCCESS: Found 'Learning Video:' in RAG context!")
    else:
        print("❌ FAILURE: 'Learning Video:' not found in RAG context.")
        
    if "https://youtu.be/19Vb9deAq1o" in context:
        print("✅ SUCCESS: Found correct YouTube URL in RAG context!")
    else:
        print("❌ FAILURE: Correct YouTube URL not found in RAG context.")

if __name__ == "__main__":
    asyncio.run(test_rag())
