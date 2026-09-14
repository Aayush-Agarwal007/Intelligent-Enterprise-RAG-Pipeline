import json

from app.rag.retrieval import retrieve_with_reranking
from app.rag.generation import generate_answer


# Load evaluation questions
with open(
    "test/evaluation_questions.json",
    "r",
    encoding="utf-8"
) as file:
    questions = json.load(file)


total = len(questions)

retrieval_passed = 0
answer_passed = 0


for item in questions:

    question = item["question"]
    expected_document = item["expected_document"]

    # Some questions use expected_facts,
    # older questions may still use expected_answer.
    expected_answer = item.get("expected_answer")
    expected_facts = item.get("expected_facts")


    # --------------------------------
    # RETRIEVAL
    # --------------------------------

    results = retrieve_with_reranking(
        question,
        limit=5
    )

    retrieved_documents = [
        result["payload"]["document_name"]
        for result in results
    ]

    retrieval_ok = (
        expected_document in retrieved_documents
    )

    if retrieval_ok:
        retrieval_passed += 1


    # --------------------------------
    # BUILD CONTEXT
    # --------------------------------

    context_parts = []

    for result in results:

        payload = result["payload"]

        context_parts.append(
            f"""
Source: {payload["document_name"]}
Page: {payload["page"]}

{payload["text"]}
"""
        )

    context = "\n".join(context_parts)


    # --------------------------------
    # GENERATE ANSWER
    # --------------------------------

    answer = generate_answer(
        question,
        context
    )


    # --------------------------------
    # CHECK ANSWER
    # --------------------------------

    if expected_facts:

        found_facts = []

        for fact in expected_facts:

            if fact.lower() in answer.lower():
                found_facts.append(fact)

        answer_ok = (
            len(found_facts) == len(expected_facts)
        )

    else:

        answer_ok = (
            expected_answer.lower() in answer.lower()
        )


    if answer_ok:
        answer_passed += 1


    # --------------------------------
    # PRINT RESULT
    # --------------------------------

    print("\n================================")

    print(
        "Question:",
        question
    )

    print(
        "Expected document:",
        expected_document
    )

    print(
        "Retrieved:",
        retrieved_documents
    )

    print(
        "Retrieval:",
        "PASS" if retrieval_ok else "FAIL"
    )

    if expected_facts:

        print(
            "Expected facts:",
            expected_facts
        )

        print(
            "Found facts:",
            found_facts
        )

    else:

        print(
            "Expected answer:",
            expected_answer
        )

    print(
        "Generated answer:",
        answer
    )

    print(
        "Answer:",
        "PASS" if answer_ok else "FAIL"
    )


# --------------------------------
# FINAL ACCURACY
# --------------------------------

retrieval_accuracy = (
    retrieval_passed / total * 100
)

answer_accuracy = (
    answer_passed / total * 100
)


print("\n================================")
print(
    f"Retrieval Accuracy: "
    f"{retrieval_accuracy:.2f}%"
)

print(
    f"Answer Accuracy: "
    f"{answer_accuracy:.2f}%"
)

print(
    f"Retrieval Passed: "
    f"{retrieval_passed}/{total}"
)

print(
    f"Answer Passed: "
    f"{answer_passed}/{total}"
)

print("================================")