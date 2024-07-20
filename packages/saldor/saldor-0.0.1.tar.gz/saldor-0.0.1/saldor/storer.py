import chromadb


def store_docs():
    client = chromadb.PersistentClient(path="~/chroma/ragscrape")

    collection = client.create_collection(name="test_collection")

    # hardcoded samples for now
    collection.add(
        documents=[
            "This is a document about pineapple",
            "This is a document about oranges",
        ],
        ids=["id1", "id2"],
    )

    results = collection.query(
        query_texts=[
            "This is a query document about florida"
        ],  # Chroma will embed this for you
        n_results=2,  # how many results to return
    )

    print(results)
