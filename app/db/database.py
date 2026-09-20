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
def create_conversations_table():
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    conn.commit()
    conn.close()
def create_messages_table():
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT fk_conversation
                    FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            )
            """
        )

    conn.commit()
    conn.close()
def create_conversation(title: str = "New Conversation"):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO conversations (title)
            VALUES (%s)
            RETURNING id
            """,
            (title,)
        )

        conversation_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return conversation_id
def add_message(conversation_id: int, role: str, content: str):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO messages (
                conversation_id,
                role,
                content
            )
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (
                conversation_id,
                role,
                content
            )
        )

        message_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return message_id
def get_messages(conversation_id: int):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                role,
                content,
                created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC, id ASC
            """,
            (conversation_id,)
        )

        messages = cursor.fetchall()

    conn.close()

    return messages
def delete_document(document_id: int):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM documents
            WHERE id = %s
            """,
            (document_id,)
        )

    conn.commit()
    conn.close()
def get_document_id(filename: str):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id
            FROM documents
            WHERE filename = %s
            """,
            (filename,)
        )

        result = cursor.fetchone()

    conn.close()

    if result is None:
        return None

    return result[0]
import psycopg


DATABASE_URL = (
    "host=enterprise-postgres "
    "port=5432 "
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
def create_conversations_table():
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id SERIAL PRIMARY KEY,
                title TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

    conn.commit()
    conn.close()
def update_conversation_title(conversation_id: int, title: str):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            UPDATE conversations
            SET title = %s
            WHERE id = %s
            """,
            (title, conversation_id)
        )

    conn.commit()
    conn.close()   
def create_messages_table():
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id SERIAL PRIMARY KEY,
                conversation_id INTEGER NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                CONSTRAINT fk_conversation
                    FOREIGN KEY (conversation_id)
                    REFERENCES conversations(id)
                    ON DELETE CASCADE
            )
            """
        )

    conn.commit()
    conn.close()
def create_conversation(title: str = "New Conversation"):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO conversations (title)
            VALUES (%s)
            RETURNING id
            """,
            (title,)
        )

        conversation_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return conversation_id
def add_message(conversation_id: int, role: str, content: str):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO messages (
                conversation_id,
                role,
                content
            )
            VALUES (%s, %s, %s)
            RETURNING id
            """,
            (
                conversation_id,
                role,
                content
            )
        )

        message_id = cursor.fetchone()[0]

    conn.commit()
    conn.close()

    return message_id
def get_messages(conversation_id: int):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                role,
                content,
                created_at
            FROM messages
            WHERE conversation_id = %s
            ORDER BY created_at ASC, id ASC
            """,
            (conversation_id,)
        )

        messages = cursor.fetchall()

    conn.close()

    return messages
def delete_document(document_id: int):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM documents
            WHERE id = %s
            """,
            (document_id,)
        )

    conn.commit()
    conn.close()
def get_document_id(filename: str):
    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id
            FROM documents
            WHERE filename = %s
            """,
            (filename,)
        )

        result = cursor.fetchone()

    conn.close()

    if result is None:
        return None

    return result[0]
def get_conversations():
    conn = get_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                id,
                title,
                created_at
            FROM conversations
            ORDER BY created_at DESC, id DESC
            """
        )
        conversations = cursor.fetchall()
    conn.close()
    return conversations
def delete_conversation(conversation_id: int):

    conn = get_connection()

    with conn.cursor() as cursor:
        cursor.execute(
            """
            DELETE FROM conversations
            WHERE id = %s
            """,
            (conversation_id,)
        )

        deleted = cursor.rowcount

    conn.commit()
    conn.close()

    return deleted

if __name__ == "__main__":
    create_documents_table()
    create_chunks_table()
    create_conversations_table()
    create_messages_table()

    print("All database tables created successfully")
    