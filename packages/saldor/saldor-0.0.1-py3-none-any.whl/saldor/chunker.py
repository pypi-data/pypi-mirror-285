import spacy


def chunk_text(text):
    # Load SpaCy model
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)

    # Extract chunks
    chunks = [chunk.text for chunk in doc.noun_chunks]
    return chunks
