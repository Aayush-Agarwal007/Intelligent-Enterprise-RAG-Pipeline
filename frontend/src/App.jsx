import { useEffect, useState } from "react"

function App() {
  // Input box
  const [inputValue, setInputValue] = useState("")

  // Currently displayed question/answer
  const [question, setQuestion] = useState("")
  const [answer, setAnswer] = useState("")

  const [loading, setLoading] = useState(false)

  // Current conversation
  const [conversationId, setConversationId] = useState(null)

  // Sidebar conversations
  const [conversations, setConversations] = useState([])

  // --------------------------------------------------
  // LOAD ALL CONVERSATIONS
  // --------------------------------------------------

  const loadConversations = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8001/conversations"
      )

      const data = await response.json()

      setConversations(data.conversations || [])

    } catch (error) {
      console.error("Failed to load conversations:", error)
    }
  }

  // --------------------------------------------------
  // LOAD MESSAGES OF A SELECTED CONVERSATION
  // --------------------------------------------------

  const loadMessages = async (id) => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8001/conversations/${id}/messages`
      )

      const data = await response.json()

      setConversationId(id)

      if (data.messages && data.messages.length > 0) {

        // Find the latest user question
        const userMessages = data.messages.filter(
          (message) => message.role === "user"
        )

        // Find the latest AI answer
        const assistantMessages = data.messages.filter(
          (message) => message.role === "assistant"
        )

        const latestUserMessage =
          userMessages[userMessages.length - 1]

        const latestAssistantMessage =
          assistantMessages[assistantMessages.length - 1]

        setQuestion(
          latestUserMessage?.content || ""
        )

        setAnswer(
          latestAssistantMessage?.content || ""
        )

      } else {

        // Empty conversation
        setQuestion("")
        setAnswer("")
      }

      setInputValue("")

    } catch (error) {
      console.error(
        "Failed to load conversation messages:",
        error
      )
    }
  }

  // --------------------------------------------------
  // CREATE NEW CONVERSATION
  // --------------------------------------------------

  const createConversation = async () => {
    try {
      const response = await fetch(
        "http://127.0.0.1:8001/conversations",
        {
          method: "POST",
        }
      )

      const data = await response.json()

      setConversationId(data.conversation_id)

      // Clear chat UI
      setInputValue("")
      setQuestion("")
      setAnswer("")

      // Refresh sidebar
      await loadConversations()

    } catch (error) {
      console.error(
        "Failed to create conversation:",
        error
      )
    }
  }

  // --------------------------------------------------
  // LOAD CONVERSATIONS WHEN APP STARTS
  // --------------------------------------------------

  useEffect(() => {
    loadConversations()
  }, [])

  // --------------------------------------------------
  // ASK QUESTION
  // --------------------------------------------------

  const askQuestion = async () => {

    if (!inputValue.trim()) return

    if (!conversationId) return

    setLoading(true)
    setAnswer("")

    // Store question before clearing input
    const queryToSubmit = inputValue

    setQuestion(queryToSubmit)

    // Clear input box
    setInputValue("")

    try {

      const response = await fetch(
        `http://127.0.0.1:8001/ask?question=${encodeURIComponent(
          queryToSubmit
        )}&conversation_id=${conversationId}`
      )

      const data = await response.json()

      setAnswer(data.answer)

      // Refresh conversation list
      await loadConversations()

    } catch (error) {

      console.error(error)

      setAnswer(
        "Something went wrong while contacting the backend."
      )

    } finally {

      setLoading(false)

    }
  }

  // --------------------------------------------------
  // UI
  // --------------------------------------------------

  return (
    <div className="h-screen bg-gray-900 text-white flex overflow-hidden">

      {/* SIDEBAR */}

      <aside className="w-64 bg-gray-950 border-r border-gray-800 p-4 flex flex-col">

        <h1 className="text-xl font-semibold mb-6">
          Enterprise AI
        </h1>

        {/* NEW CONVERSATION */}

        <button
          onClick={createConversation}
          className="w-full rounded-lg border border-gray-700 px-4 py-2 text-left hover:bg-gray-800 transition-colors"
        >
          + New Conversation
        </button>

        {/* CONVERSATIONS TITLE */}

        <div className="mt-6 text-sm text-gray-400 mb-2">
          Conversations
        </div>

        {/* CONVERSATION LIST */}

        <div className="flex-1 overflow-y-auto space-y-2 pr-2">

          {conversations.map((conversation) => (

            <button
              key={conversation.id}

              onClick={() =>
                loadMessages(conversation.id)
              }

              className={`w-full text-left rounded-lg px-3 py-2 text-sm transition-colors ${
                conversationId === conversation.id
                  ? "bg-gray-700 text-white"
                  : "hover:bg-gray-800 text-gray-300"
              }`}
            >
              {conversation.title || "New Conversation"}
            </button>

          ))}

        </div>

      </aside>

      {/* MAIN AREA */}

      <main className="flex-1 flex flex-col min-w-0">

        {/* HEADER */}

        <header className="h-16 border-b border-gray-800 flex items-center px-6 shrink-0">

          <h2 className="font-medium">
            Enterprise Knowledge Assistant
          </h2>

        </header>

        {/* CHAT AREA */}

        <section className="flex-1 overflow-y-auto p-6">

          {/* EMPTY STATE */}

          {!answer && !loading && !question && (

            <div className="h-full flex items-center justify-center">

              <div className="text-center">

                <h2 className="text-3xl font-semibold">
                  How can I help you?
                </h2>

                <p className="text-gray-400 mt-2">
                  Ask questions about your enterprise documents.
                </p>

              </div>

            </div>

          )}

          {/* LOADING */}

          {loading && (

            <div className="max-w-3xl mx-auto text-gray-400 animate-pulse">

              Thinking...

            </div>

          )}

          {/* QUESTION + ANSWER */}

          {(question || answer) && !loading && (

            <div className="max-w-3xl mx-auto">

              {/* USER */}

              <div className="mb-2 text-sm text-gray-400 font-medium">
                You
              </div>

              <div className="mb-6 bg-gray-800 rounded-xl p-4 text-gray-100">
                {question}
              </div>

              {/* AI */}

              {answer && (

                <>
                  <div className="mb-2 text-sm text-gray-400 font-medium">
                    Enterprise AI
                  </div>

                  <div className="bg-gray-800 rounded-xl p-4 whitespace-pre-wrap text-gray-100 leading-relaxed">
                    {answer}
                  </div>
                </>

              )}

            </div>

          )}

        </section>

        {/* INPUT */}

        <div className="p-4 bg-gray-900 shrink-0">

          <div className="max-w-3xl mx-auto flex gap-2">

            <input
              type="text"
              value={inputValue}

              onChange={(e) =>
                setInputValue(e.target.value)
              }

              onKeyDown={(e) => {

                if (e.key === "Enter") {
                  askQuestion()
                }

              }}

              disabled={!conversationId}

              placeholder={
                conversationId
                  ? "Ask something..."
                  : "Select or create a conversation to begin"
              }

              className="flex-1 rounded-xl bg-gray-800 border border-gray-700 px-4 py-3 outline-none focus:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
            />

            <button
              onClick={askQuestion}

              disabled={
                loading ||
                !conversationId ||
                !inputValue.trim()
              }

              className="rounded-xl bg-white text-black px-5 py-3 font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 transition-colors"
            >
              {loading ? "..." : "Send"}
            </button>

          </div>

        </div>

      </main>

    </div>
  )
}

export default App