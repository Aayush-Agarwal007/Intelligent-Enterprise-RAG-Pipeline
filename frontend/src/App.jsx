import { useCallback, useEffect, useRef, useState } from "react"

// ==================================================
// API CONFIG
// ==================================================

const API_BASE_URL = "http://127.0.0.1:8001"

// ==================================================
// API ERROR
// ==================================================

class ApiError extends Error {
  constructor(message, status = 0) {
    super(message)
    this.name = "ApiError"
    this.status = status
  }
}

// ==================================================
// API REQUEST
// ==================================================

async function apiRequest(path, options = {}) {
  let response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, options)
  } catch (error) {
    throw new ApiError(
      "Cannot reach the backend. Make sure the backend is running.",
      0
    )
  }

  const text = await response.text()

  let data = null

  if (text) {
    try {
      data = JSON.parse(text)
    } catch {
      data = null
    }
  }

  if (!response.ok) {
    const detail =
      (data && (data.detail || data.message)) ||
      `Request failed (${response.status})`

    throw new ApiError(
      typeof detail === "string"
        ? detail
        : JSON.stringify(detail),
      response.status
    )
  }

  return data
}

// ==================================================
// API
// ==================================================

const api = {
  health: () => apiRequest("/health"),

  getConversations: () =>
    apiRequest("/conversations"),

  createConversation: () =>
    apiRequest("/conversations", {
      method: "POST",
    }),

  deleteConversation: (id) =>
    apiRequest(`/conversations/${id}`, {
      method: "DELETE",
    }),

  getMessages: (id) =>
    apiRequest(`/conversations/${id}/messages`),

  askQuestion: (question, conversationId) =>
    apiRequest(
      `/ask?question=${encodeURIComponent(
        question
      )}&conversation_id=${conversationId}`
    ),

  getDocuments: () =>
    apiRequest("/documents/"),

  deleteDocument: (filename) =>
    apiRequest(
      `/documents/${encodeURIComponent(filename)}`,
      {
        method: "DELETE",
      }
    ),

  uploadDocument: (file) => {
    const formData = new FormData()

    formData.append("file", file)

    return apiRequest("/documents/upload", {
      method: "POST",
      body: formData,
    })
  },
}

// ==================================================
// HELPERS
// ==================================================

function formatScore(score) {
  const number = Number(score)

  return Number.isFinite(number)
    ? number.toFixed(2)
    : score
}

function formatBytes(bytes) {
  const number = Number(bytes)

  if (!Number.isFinite(number)) {
    return ""
  }

  if (number < 1024) {
    return `${number} B`
  }

  if (number < 1024 * 1024) {
    return `${(number / 1024).toFixed(1)} KB`
  }

  return `${(number / (1024 * 1024)).toFixed(1)} MB`
}

// ==================================================
// TOAST
// ==================================================

let toastCounter = 0

function ToastContainer({ toasts, onDismiss }) {
  return (
    <div className="fixed top-4 right-4 z-[100] w-[calc(100%-2rem)] max-w-sm space-y-2">
      {toasts.map((toast) => (
        <div
          key={toast.id}
          className={`rounded-lg px-4 py-3 text-sm shadow-lg border flex items-start gap-3 ${
            toast.type === "success"
              ? "bg-emerald-950 border-emerald-800 text-emerald-200"
              : toast.type === "error"
              ? "bg-red-950 border-red-800 text-red-200"
              : "bg-gray-800 border-gray-700 text-gray-200"
          }`}
        >
          <span className="mt-0.5">
            {toast.type === "success"
              ? "✓"
              : toast.type === "error"
              ? "✕"
              : "ℹ"}
          </span>

          <div className="flex-1 whitespace-pre-wrap">
            {toast.message}
          </div>

          <button
            onClick={() => onDismiss(toast.id)}
            className="text-gray-500 hover:text-gray-300 text-lg leading-none"
          >
            ×
          </button>
        </div>
      ))}
    </div>
  )
}

// ==================================================
// DOCUMENT PANEL
// ==================================================

function DocumentPanel({
  open,
  onClose,
  documents,
  loadingDocs,
  onUpload,
  onDelete,
  uploading,
}) {
  const fileInputRef = useRef(null)

  if (!open) {
    return null
  }

  const handleFileChange = (event) => {
    const file = event.target.files?.[0]

    if (!file) {
      return
    }

    const isPdf =
      file.type === "application/pdf" ||
      file.name.toLowerCase().endsWith(".pdf")

    if (!isPdf) {
      onUpload(
        null,
        "Only PDF files are supported."
      )

      event.target.value = ""
      return
    }

    onUpload(file)

    event.target.value = ""
  }

  return (
    <div className="fixed inset-0 z-40 flex justify-end bg-black/50">
      <div className="w-full sm:w-96 h-full bg-gray-950 border-l border-gray-800 flex flex-col">

        {/* HEADER */}

        <div className="h-16 border-b border-gray-800 flex items-center justify-between px-4 shrink-0">
          <h3 className="font-medium">
            Documents
          </h3>

          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white text-xl"
          >
            ×
          </button>
        </div>

        {/* UPLOAD */}

        <div className="p-4 border-b border-gray-800 shrink-0">

          <input
            ref={fileInputRef}
            type="file"
            accept="application/pdf,.pdf"
            className="hidden"
            onChange={handleFileChange}
          />

          <button
            onClick={() =>
              fileInputRef.current?.click()
            }
            disabled={uploading}
            className="w-full rounded-lg border border-gray-700 px-4 py-2 hover:bg-gray-800 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
          >
            {uploading ? (
              <>
                <span className="w-4 h-4 border-2 border-gray-500 border-t-white rounded-full animate-spin" />
                Uploading...
              </>
            ) : (
              "+ Upload Document"
            )}
          </button>

        </div>

        {/* DOCUMENT LIST */}

        <div className="flex-1 overflow-y-auto p-4 space-y-2">

          {loadingDocs && (
            <div className="text-sm text-gray-500">
              Loading documents...
            </div>
          )}

          {!loadingDocs &&
            documents.length === 0 && (
              <div className="text-sm text-gray-500">
                No documents uploaded yet.
              </div>
            )}

          {documents.map((document) => (
            <div
              key={document.filename}
              className="rounded-lg border border-gray-800 bg-gray-900 px-3 py-2 flex items-center justify-between gap-2"
            >
              <div className="min-w-0">
                <div className="text-sm text-gray-200 truncate">
                  {document.filename}
                </div>

                <div className="text-xs text-gray-500">
                  {formatBytes(
                    document.size_bytes
                  )}
                </div>
              </div>

              <button
                onClick={() =>
                  onDelete(document.filename)
                }
                className="text-xs text-red-400 hover:text-red-300 shrink-0"
              >
                Delete
              </button>
            </div>
          ))}

        </div>

      </div>
    </div>
  )
}

// ==================================================
// APP
// ==================================================

function App() {
  // --------------------------------------------------
  // STATE
  // --------------------------------------------------

  const [inputValue, setInputValue] = useState("")
  const [messages, setMessages] = useState([])

  const [loading, setLoading] = useState(false)

  const [conversationId, setConversationId] =
    useState(null)

  const [conversations, setConversations] =
    useState([])

  const [
    conversationsLoading,
    setConversationsLoading,
  ] = useState(false)

  const [sidebarOpen, setSidebarOpen] =
    useState(true)

  const [docPanelOpen, setDocPanelOpen] =
    useState(false)

  const [documents, setDocuments] =
    useState([])

  const [documentsLoading, setDocumentsLoading] =
    useState(false)

  const [uploading, setUploading] =
    useState(false)

  const [backendOnline, setBackendOnline] =
    useState(true)

  const [toasts, setToasts] =
    useState([])

  const messagesEndRef = useRef(null)

  // This tracks which conversation is currently active.
  const activeConversationRef = useRef(null)

  // --------------------------------------------------
  // KEEP ACTIVE CONVERSATION REF UPDATED
  // --------------------------------------------------

  useEffect(() => {
    activeConversationRef.current =
      conversationId
  }, [conversationId])

  // --------------------------------------------------
  // TOAST FUNCTIONS
  // --------------------------------------------------

  const dismissToast = useCallback((id) => {
    setToasts((previous) =>
      previous.filter(
        (toast) => toast.id !== id
      )
    )
  }, [])

  const pushToast = useCallback(
    (message, type = "info") => {
      const id = ++toastCounter

      setToasts((previous) => [
        ...previous,
        {
          id,
          message,
          type,
        },
      ])

      setTimeout(() => {
        dismissToast(id)
      }, 4000)
    },
    [dismissToast]
  )

  // --------------------------------------------------
  // AUTO SCROLL
  // --------------------------------------------------

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({
      behavior: "smooth",
    })
  }, [messages, loading])

  // --------------------------------------------------
  // HEALTH CHECK
  // --------------------------------------------------

  useEffect(() => {
    let mounted = true

    api
      .health()
      .then(() => {
        if (mounted) {
          setBackendOnline(true)
        }
      })
      .catch(() => {
        if (mounted) {
          setBackendOnline(false)

          pushToast(
            `Backend is unreachable at ${API_BASE_URL}`,
            "error"
          )
        }
      })

    return () => {
      mounted = false
    }
  }, [pushToast])

  // --------------------------------------------------
  // LOAD CONVERSATIONS
  // --------------------------------------------------

  const loadConversations = useCallback(
    async () => {
      setConversationsLoading(true)

      try {
        const data =
          await api.getConversations()

        setConversations(
          data.conversations || []
        )

        setBackendOnline(true)
      } catch (error) {
        setBackendOnline(false)

        pushToast(
          error.message ||
            "Failed to load conversations",
          "error"
        )
      } finally {
        setConversationsLoading(false)
      }
    },
    [pushToast]
  )

  // --------------------------------------------------
  // INITIAL LOAD
  // --------------------------------------------------

  useEffect(() => {
    loadConversations()
  }, [loadConversations])

  // --------------------------------------------------
  // LOAD MESSAGES
  // --------------------------------------------------

  const loadMessages = async (id) => {
    // IMPORTANT:
    // Set active conversation BEFORE loading.
    // This prevents an old /ask request from
    // writing into the newly selected conversation.

    setConversationId(id)
    activeConversationRef.current = id

    setInputValue("")
    setMessages([])

    try {
      const data =
        await api.getMessages(id)

      // Make sure user hasn't switched again
      // while this request was running.

      if (
        activeConversationRef.current !== id
      ) {
        return
      }

      setMessages(data.messages || [])
      setBackendOnline(true)
    } catch (error) {
      if (
        activeConversationRef.current !== id
      ) {
        return
      }

      setMessages([])

      pushToast(
        error.message ||
          "Failed to load conversation",
        "error"
      )
    }
  }

  // --------------------------------------------------
  // CREATE NEW CONVERSATION
  // --------------------------------------------------

  const createConversation = async () => {
    /*
      IMPORTANT BEHAVIOR:

      If the currently selected conversation
      has no messages, DO NOT create another
      empty conversation.

      Simply keep the current conversation
      selected and clear the input.

      This prevents:

      New Conversation
      New Conversation
      New Conversation
      New Conversation

      when the user repeatedly clicks the button
      without actually starting a conversation.
    */

    if (
      conversationId !== null &&
      messages.length === 0
    ) {
      setInputValue("")

      pushToast(
        "You already have an empty conversation open.",
        "info"
      )

      return
    }

    try {
      const data =
        await api.createConversation()

      const newConversationId =
        data.conversation_id

      setConversationId(newConversationId)

      activeConversationRef.current =
        newConversationId

      setInputValue("")
      setMessages([])

      await loadConversations()

      setSidebarOpen(true)
    } catch (error) {
      pushToast(
        error.message ||
          "Failed to create conversation",
        "error"
      )
    }
  }

  // --------------------------------------------------
  // DELETE CONVERSATION
  // --------------------------------------------------

  const deleteConversation = async (
    id,
    event
  ) => {
    event.stopPropagation()

    const confirmed = window.confirm(
      "Delete this conversation? This cannot be undone."
    )

    if (!confirmed) {
      return
    }

    try {
      await api.deleteConversation(id)

      setConversations((previous) =>
        previous.filter(
          (conversation) =>
            conversation.id !== id
        )
      )

      if (conversationId === id) {
        setConversationId(null)

        activeConversationRef.current = null

        setMessages([])
        setInputValue("")
      }

      pushToast(
        "Conversation deleted.",
        "success"
      )
    } catch (error) {
      pushToast(
        error.message ||
          "Failed to delete conversation",
        "error"
      )
    }
  }

  // --------------------------------------------------
  // ASK QUESTION
  // --------------------------------------------------

  const askQuestion = async () => {
    const question = inputValue.trim()

    if (!question) {
      return
    }

    if (!conversationId) {
      return
    }

    if (loading) {
      return
    }

    // Capture the conversation at the exact
    // moment the request starts.

    const askedInConversation =
      conversationId

    setLoading(true)
    setInputValue("")

    // Optimistic user message

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: question,
      },
    ])

    try {
      const data =
        await api.askQuestion(
          question,
          askedInConversation
        )

      /*
        IMPORTANT:

        User may have clicked another conversation
        while Ollama was generating.

        If that happened, DO NOT append this answer
        to the newly selected conversation.
      */

      if (
        activeConversationRef.current !==
        askedInConversation
      ) {
        return
      }

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content: data.answer,
          sources: data.sources || [],
        },
      ])

      await loadConversations()

      setBackendOnline(true)
    } catch (error) {
      if (
        activeConversationRef.current !==
        askedInConversation
      ) {
        return
      }

      pushToast(
        error.message ||
          "Failed to get a response",
        "error"
      )

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Something went wrong while contacting the backend.",
          sources: [],
        },
      ])
    } finally {
      if (
        activeConversationRef.current ===
        askedInConversation
      ) {
        setLoading(false)
      }
    }
  }

  // --------------------------------------------------
  // INPUT KEYBOARD HANDLER
  // --------------------------------------------------

  const handleInputKeyDown = (event) => {
    /*
      Prevent Enter from submitting while the
      user is using an IME.

      Shift + Enter can also be reserved for
      future multiline input behavior.
    */

    if (
      event.key === "Enter" &&
      !event.nativeEvent.isComposing &&
      !event.shiftKey
    ) {
      event.preventDefault()

      askQuestion()
    }
  }

  // --------------------------------------------------
  // LOAD DOCUMENTS
  // --------------------------------------------------

  const loadDocuments = useCallback(
    async () => {
      setDocumentsLoading(true)

      try {
        const data =
          await api.getDocuments()

        setDocuments(
          data.documents || []
        )

        setBackendOnline(true)
      } catch (error) {
        pushToast(
          error.message ||
            "Failed to load documents",
          "error"
        )
      } finally {
        setDocumentsLoading(false)
      }
    },
    [pushToast]
  )

  // --------------------------------------------------
  // OPEN DOCUMENT PANEL
  // --------------------------------------------------

  const openDocPanel = () => {
    setDocPanelOpen(true)

    loadDocuments()
  }

  // --------------------------------------------------
  // UPLOAD DOCUMENT
  // --------------------------------------------------

  const handleUpload = async (
    file,
    validationError
  ) => {
    if (validationError) {
      pushToast(
        validationError,
        "error"
      )

      return
    }

    if (!file) {
      return
    }

    setUploading(true)

    try {
      const data =
        await api.uploadDocument(file)

      pushToast(
        `Document uploaded successfully\n${data.filename}\nPages: ${data.pages} · Chunks: ${data.chunks}`,
        "success"
      )

      await loadDocuments()

      setBackendOnline(true)
    } catch (error) {
      pushToast(
        error.message ||
          "Failed to upload document",
        "error"
      )
    } finally {
      setUploading(false)
    }
  }

  // --------------------------------------------------
  // DELETE DOCUMENT
  // --------------------------------------------------

  const handleDeleteDocument = async (
    filename
  ) => {
    const confirmed = window.confirm(
      `Delete "${filename}"? This cannot be undone.`
    )

    if (!confirmed) {
      return
    }

    try {
      await api.deleteDocument(filename)

      setDocuments((previous) =>
        previous.filter(
          (document) =>
            document.filename !== filename
        )
      )

      pushToast(
        "Document deleted.",
        "success"
      )
    } catch (error) {
      pushToast(
        error.message ||
          "Failed to delete document",
        "error"
      )
    }
  }

  // ==================================================
  // UI
  // ==================================================

  return (
    <div className="h-screen bg-gray-900 text-white flex overflow-hidden">

      {/* ==================================================
          TOASTS
      ================================================== */}

      <ToastContainer
        toasts={toasts}
        onDismiss={dismissToast}
      />

      {/* ==================================================
          DOCUMENT PANEL
      ================================================== */}

      <DocumentPanel
        open={docPanelOpen}
        onClose={() =>
          setDocPanelOpen(false)
        }
        documents={documents}
        loadingDocs={documentsLoading}
        onUpload={handleUpload}
        onDelete={handleDeleteDocument}
        uploading={uploading}
      />

      {/* ==================================================
          BACKEND OFFLINE
      ================================================== */}

      {!backendOnline && (
        <div className="fixed bottom-4 left-1/2 -translate-x-1/2 z-50 bg-red-950 border border-red-800 text-red-200 text-sm px-4 py-2 rounded-lg shadow-lg">
          Backend unavailable — check that it is
          running at {API_BASE_URL}
        </div>
      )}

      {/* ==================================================
          SIDEBAR
      ================================================== */}

      <aside
        className={`bg-gray-950 border-r border-gray-800 flex flex-col shrink-0 transition-all duration-200 overflow-hidden ${
          sidebarOpen
            ? "w-64 p-4"
            : "w-0 p-0"
        }`}
      >

        <div className="flex items-center justify-between mb-6 min-w-[14rem]">

          <h1 className="text-xl font-semibold">
            Enterprise AI
          </h1>

          <button
            onClick={() =>
              setSidebarOpen(false)
            }
            className="text-gray-500 hover:text-gray-300 text-sm sm:hidden"
          >
            ×
          </button>

        </div>

        {/* SIDEBAR ACTIONS */}

        <div className="space-y-2 min-w-[14rem]">

          <button
            onClick={createConversation}
            className="w-full rounded-lg border border-gray-700 px-4 py-2 text-left hover:bg-gray-800 transition-colors"
          >
            + New Conversation
          </button>

          <button
            onClick={openDocPanel}
            className="w-full rounded-lg border border-gray-700 px-4 py-2 text-left hover:bg-gray-800 transition-colors"
          >
            + Upload Document
          </button>

        </div>

        {/* CONVERSATIONS */}

        <div className="mt-6 text-sm text-gray-400 mb-2 min-w-[14rem]">
          Conversations
        </div>

        <div className="flex-1 overflow-y-auto space-y-1 pr-2 min-w-[14rem]">

          {conversationsLoading &&
            conversations.length === 0 && (
              <div className="text-sm text-gray-600 px-3 py-2">
                Loading...
              </div>
            )}

          {!conversationsLoading &&
            conversations.length === 0 && (
              <div className="text-sm text-gray-600 px-3 py-2">
                No conversations yet.
              </div>
            )}

          {conversations.map(
            (conversation) => (
              <div
                key={conversation.id}
                onClick={() =>
                  loadMessages(
                    conversation.id
                  )
                }
                className={`group w-full rounded-lg px-3 py-2 text-sm transition-colors cursor-pointer flex items-center justify-between gap-2 ${
                  conversationId ===
                  conversation.id
                    ? "bg-gray-700 text-white"
                    : "hover:bg-gray-800 text-gray-300"
                }`}
              >

                <span className="truncate">
                  {conversation.title ||
                    "New Conversation"}
                </span>

                <button
                  onClick={(event) =>
                    deleteConversation(
                      conversation.id,
                      event
                    )
                  }
                  className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-red-400 text-xs shrink-0 transition-opacity"
                  title="Delete conversation"
                >
                  ✕
                </button>

              </div>
            )
          )}

        </div>

      </aside>

      {/* ==================================================
          MAIN
      ================================================== */}

      <main className="flex-1 flex flex-col min-w-0">

        {/* HEADER */}

        <header className="h-16 border-b border-gray-800 flex items-center px-6 shrink-0 gap-3">

          <button
            onClick={() =>
              setSidebarOpen(
                (previous) => !previous
              )
            }
            className="text-gray-400 hover:text-white"
            title="Toggle sidebar"
          >
            ☰
          </button>

          <h2 className="font-medium">
            Enterprise Knowledge Assistant
          </h2>

        </header>

        {/* CHAT AREA */}

        <section className="flex-1 overflow-y-auto p-6">

          {/* EMPTY STATE */}

          {messages.length === 0 &&
            !loading && (
              <div className="h-full flex items-center justify-center">

                <div className="text-center px-4">

                  <h2 className="text-3xl font-semibold">
                    How can I help you?
                  </h2>

                  <p className="text-gray-400 mt-2">
                    Ask questions about your
                    enterprise documents.
                  </p>

                </div>

              </div>
            )}

          {/* MESSAGES */}

          {messages.length > 0 && (
            <div className="max-w-3xl mx-auto space-y-6">

              {messages.map(
                (message, index) => {
                  const isUser =
                    message.role ===
                    "user"

                  return (
                    <div
                      key={`${index}-${message.role}`}
                      className={`flex ${
                        isUser
                          ? "justify-end"
                          : "justify-start"
                      }`}
                    >

                      <div
                        className={`max-w-[85%] ${
                          isUser
                            ? "items-end"
                            : "items-start"
                        } flex flex-col`}
                      >

                        {/* NAME */}

                        <div className="mb-2 text-xs text-gray-500 font-medium">
                          {isUser
                            ? "You"
                            : "Enterprise AI"}
                        </div>

                        {/* MESSAGE */}

                        <div
                          className={`rounded-2xl px-4 py-3 whitespace-pre-wrap leading-relaxed ${
                            isUser
                              ? "bg-white text-black"
                              : "bg-gray-800 text-gray-100"
                          }`}
                        >
                          {message.content}
                        </div>

                        {/* SOURCES */}

                        {!isUser &&
                          (
                            message.sources ||
                            []
                          ).length > 0 && (
                            <div className="mt-3 w-full">

                              <div className="text-xs text-gray-500 mb-2">
                                Sources
                              </div>

                              <div className="space-y-2">

                                {message.sources.map(
                                  (
                                    source,
                                    sourceIndex
                                  ) => (
                                    <div
                                      key={
                                        sourceIndex
                                      }
                                      className="text-xs bg-gray-900 border border-gray-800 rounded-lg px-3 py-2 text-gray-400"
                                    >

                                      <span className="text-gray-300">
                                        {
                                          source.document
                                        }
                                      </span>

                                      <span className="mx-2">
                                        •
                                      </span>

                                      Page{" "}
                                      {
                                        source.page
                                      }

                                      <span className="mx-2">
                                        •
                                      </span>

                                      Score:{" "}
                                      {formatScore(
                                        source.score
                                      )}

                                    </div>
                                  )
                                )}

                              </div>

                            </div>
                          )}

                      </div>

                    </div>
                  )
                }
              )}

              {/* THINKING */}

              {loading && (
                <div className="flex items-center gap-2 text-gray-400">

                  <span className="w-4 h-4 border-2 border-gray-500 border-t-white rounded-full animate-spin" />

                  <span className="animate-pulse">
                    Thinking...
                  </span>

                </div>
              )}

              {/* AUTO SCROLL */}

              <div ref={messagesEndRef} />

            </div>
          )}

          {/* THINKING WHEN CHAT IS EMPTY */}

          {loading &&
            messages.length === 0 && (
              <div className="max-w-3xl mx-auto mt-4 flex items-center gap-2 text-gray-400">

                <span className="w-4 h-4 border-2 border-gray-500 border-t-white rounded-full animate-spin" />

                <span className="animate-pulse">
                  Thinking...
                </span>

              </div>
            )}

        </section>

        {/* ==================================================
            INPUT
        ================================================== */}

        <div className="p-4 bg-gray-900 shrink-0">

          <div className="max-w-3xl mx-auto flex gap-2">

            <input
              type="text"
              value={inputValue}
              onChange={(event) =>
                setInputValue(
                  event.target.value
                )
              }
              onKeyDown={
                handleInputKeyDown
              }
              disabled={
                !conversationId ||
                loading
              }
              placeholder={
                conversationId
                  ? "Ask something..."
                  : "Select or create a conversation to begin"
              }
              className="flex-1 rounded-xl bg-gray-800 border border-gray-700 px-4 py-3 outline-none focus:border-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
            />

            {/* SEND */}

            <button
              onClick={askQuestion}
              disabled={
                loading ||
                !conversationId ||
                !inputValue.trim()
              }
              className="group rounded-xl bg-white text-black px-5 py-3 font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-200 transition-all duration-200 flex items-center gap-2"
            >

              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-gray-400 border-t-black rounded-full animate-spin" />

                  Thinking
                </>
              ) : (
                <>
                  Send

                  <span className="inline-block transition-transform duration-200 group-hover:translate-x-1 group-hover:-translate-y-1">
                    ↑
                  </span>
                </>
              )}

            </button>

          </div>

        </div>

      </main>

    </div>
  )
}

export default App