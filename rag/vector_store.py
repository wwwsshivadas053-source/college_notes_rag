from langchain_community.vectorstores import FAISS

def create_vectorstore(
    chunks,
    embeddings
):

    db = FAISS.from_texts(
        chunks,
        embeddings
    )

    db.save_local(
        "vectors"
    )

    return db