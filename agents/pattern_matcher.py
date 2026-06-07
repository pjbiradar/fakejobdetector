import pysqlite3
import sys
sys.modules['sqlite3'] = sys.modules.pop('pysqlite3')

import json
import os
from sentence_transformers import SentenceTransformer
import chromadb
from dotenv import load_dotenv

load_dotenv()

# Load embedding model — converts text to vectors
# This is what makes semantic search work
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

# Setup ChromaDB — local vector database
chroma_client = chromadb.PersistentClient(path="./chroma_db")

def load_scam_patterns():
    """Load scam patterns from JSON and store in ChromaDB"""
    
    # Delete existing collection and recreate fresh
    try:
        chroma_client.delete_collection("scam_patterns")
    except:
        pass
    
    collection = chroma_client.create_collection("scam_patterns")
    
    # Load patterns from JSON file
    with open("data/scam_patterns.json", "r") as f:
        patterns = json.load(f)
    
    # Convert each pattern to embedding and store in ChromaDB
    for pattern in patterns:
        embedding = embedding_model.encode(pattern["text"]).tolist()
        collection.add(
            ids=[pattern["id"]],
            embeddings=[embedding],
            documents=[pattern["text"]],
            metadatas=[{
                "category": pattern["category"],
                "severity": pattern["severity"]
            }]
        )
    
    print(f"Loaded {len(patterns)} scam patterns into ChromaDB")
    return collection


def match_patterns(job_text: str) -> dict:
    """
    Agent 3 — Pattern Matcher
    Converts job posting to embedding and finds similar scam patterns
    """
    
    # Get or create collection
    try:
        collection = chroma_client.get_collection("scam_patterns")
    except:
        collection = load_scam_patterns()
    
    # Convert job posting to embedding vector
    job_embedding = embedding_model.encode(job_text).tolist()
    
    # Search ChromaDB for similar scam patterns
    results = collection.query(
        query_embeddings=[job_embedding],
        n_results=3  # Get top 3 most similar patterns
    )
    
    # Process results
    matches = []
    for i in range(len(results["documents"][0])):
        matches.append({
            "matched_pattern": results["documents"][0][i],
            "category": results["metadatas"][0][i]["category"],
            "severity": results["metadatas"][0][i]["severity"],
            # "similarity": round(1 - results["distances"][0][i], 2)
            "similarity": round((1 - results["distances"][0][i] / 2), 2)
        })
    
    # Calculate overall similarity score
    top_similarity = matches[0]["similarity"] if matches else 0
    similarity_score = round(top_similarity * 100, 1)
    
    return {
        "top_matches": matches,
        "similarity_score": similarity_score,
        "suspicious": similarity_score > 30,
        "dominant_category": matches[0]["category"] if matches else "unknown"
    }


if __name__ == "__main__":
    # First load patterns into database
    print("Loading scam patterns into ChromaDB...")
    load_scam_patterns()
    
    # Test with a fake job posting
    test_job = """
    Earn 50000 per month working from home. No experience needed.
    Pay small registration fee to secure your position.
    WhatsApp us immediately. Limited slots available.
    """
    
    print("\nTesting Pattern Matcher...")
    result = match_patterns(test_job)
    print(f"Similarity score: {result['similarity_score']}/100")
    print(f"Suspicious: {result['suspicious']}")
    print(f"Dominant category: {result['dominant_category']}")
    print(f"\nTop matches:")
    for match in result["top_matches"]:
        print(f"  - {match['matched_pattern'][:60]}...")
        print(f"    Similarity: {match['similarity']} | Category: {match['category']}")