import psycopg


DATABASE_URL = (
    "host=127.0.0.1 "
    "port=5540 "
    "dbname=enterprise_ai "
    "user=enterprise "
    "password=enterprise123"
)


def get_connection():
    return psycopg.connect(DATABASE_URL)


def create_documents_table():
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                filename TEXT NOT NULL,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    conn.commit()
    conn.close()

def add_document(filename: str):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO documents (filename)
            VALUES (%s)
            RETURNING id
            """,
            (filename,)
        )

        document_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()
    return document_id
def add_chunks(document_id: int, chunks: list):
    conn = get_connection()

    with conn.cursor() as cursor:
        for index, chunk in enumerate(chunks):
            cursor.execute(
                """
                INSERT INTO chunks (
                    document_id,
                    chunk_id,
                    page,
                    text
                )
                VALUES (%s, %s, %s, %s)
                """,
                (
                    document_id,
                    index + 1,
                    chunk["page"],
                    chunk["text"]
                )
            )

    conn.commit()
    conn.close()

def create_chunks_table():
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                document_id INTEGER NOT NULL,
                chunk_id INTEGER NOT NULL,
                page INTEGER NOT NULL,
                text TEXT NOT NULL,

                CONSTRAINT fk_document
                    FOREIGN KEY (document_id)
                    REFERENCES documents(id)
                    ON DELETE CASCADE
            )
            """
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    create_documents_table()
    create_chunks_table()

    print("Documents and chunks tables created successfully")