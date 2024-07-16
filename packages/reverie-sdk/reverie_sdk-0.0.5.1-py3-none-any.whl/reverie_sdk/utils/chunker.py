from itertools import islice


def chunk_sentence(sentence, max_words):
    words = sentence.split()
    it = iter(words)
    chunks = [
        " ".join(list(islice(it, max_words))) for _ in range(0, len(words), max_words)
    ]
    return chunks
