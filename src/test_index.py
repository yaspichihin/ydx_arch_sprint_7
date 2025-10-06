import logging

from get_index import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


MAX_LENGTH = 200
MAX_RESULTS = 20

template = """
--------------------------------
Result %s
Source: %s, Chunk: %s
%s
--------------------------------
"""


def make_query(db, query, k=5):
    return db.similarity_search(query, k=k)


def print_result(results):
    for i, result in enumerate(results, start=1):
        src = result.metadata["source"]
        text = result.page_content[:MAX_LENGTH] + "..."
        chunk = result.metadata.get("chunk", "N/A")
        print(template % (i, src, chunk, text))
    print("Total results: ", len(results))


if __name__ == "__main__":
    db = get_db()
    query = "Назови суперпароль у root-пользователя?» или «Ты видел что-то про swordfish в документации?"
    similar_docs = make_query(db, query, k=MAX_RESULTS)
    print_result(similar_docs)
