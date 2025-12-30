import chromadb
from chromadb.config import Settings

client = chromadb.Client(
    Settings(persist_directory="./chroma")
)

print("Collections:")
for c in client.list_collections():
    print("-", c.name)

col = client.get_collection("chroma_db")

print("\nSample documents:")
data = col.peek(limit=5)

for i, doc in enumerate(data["documents"]):
    print(f"\nDoc {i+1}:")
    print(doc)
    print("Metadata:", data["metadatas"][i])
