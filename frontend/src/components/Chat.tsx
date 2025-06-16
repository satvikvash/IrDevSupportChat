import type React from "react"
import { useState, useEffect, useRef } from "react"
import Sidebar from "./Sidebar"
import ChatInput from "./ChatInput"
import ChatMessage from "./ChatMessage"
import "../styles/Chat.css"
import { sendMessage as apicall } from "../api/chatApi"

interface ChatProps {
  user: string
  onLogout: () => void
}

export interface Message {
  id: string
  content: string
  sender: "user" | "assistant"
  timestamp: Date
}

export interface ChatHistory {
  id: string
  title: string
  messages: Message[]
  createdAt: Date
}

const Chat: React.FC<ChatProps> = ({ user, onLogout }) => {
  const [chatHistories, setChatHistories] = useState<ChatHistory[]>([])
  const [activeChatId, setActiveChatId] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  // Create a new chat
  const createNewChat = () => {
    const newChat: ChatHistory = {
      id: `chat-${Date.now()}`,
      title: `New Chat`,
      messages: [],
      createdAt: new Date(),
    }

    setChatHistories((prev) => [newChat, ...prev])
    setActiveChatId(newChat.id)
  }

  // Initialize with a default chat if none exists
  useEffect(() => {
    if (chatHistories.length === 0) {
      createNewChat()
    }
  }, [])

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [chatHistories, activeChatId])

  // Get current active chat
  const activeChat = chatHistories.find((chat) => chat.id === activeChatId) || null

  // Send a message
  const sendMessage = async (content: string) => {
    if (!activeChatId || !content.trim()) return

    // Create user message
    const userMessage: Message = {
      id: `msg-${Date.now()}`,
      content,
      sender: "user",
      timestamp: new Date(),
    }

    // Update chat history with user message
    const updatedHistories = chatHistories.map((chat) => {
      if (chat.id === activeChatId) {
        // Update chat title if it's the first message
        const title = chat.messages.length === 0 ? content.substring(0, 20) + "..." : chat.title
        return {
          ...chat,
          title,
          messages: [...chat.messages, userMessage],
        }
      }
      return chat
    })

    setChatHistories(updatedHistories)

    // Simulate API call
    setIsLoading(true)

    try {
      var history;
      // In a real app, this would be a fetch to your backend
      const res = await apicall(content, history);

      // Create assistant response
      const assistantMessage: Message = {
        id: `msg-${Date.now() + 1}`,
        content: res.message,
        sender: "assistant",
        timestamp: res.timestamp,
      }

      // Update chat history with assistant response
      const finalHistories = updatedHistories.map((chat) => {
        if (chat.id === activeChatId) {
          return {
            ...chat,
            messages: [...chat.messages, assistantMessage],
          }
        }
        return chat
      })

      setChatHistories(finalHistories)
    } catch (error) {
      console.error("Error sending message:", error)
    } finally {
      setIsLoading(false)
    }
  }

  // Select a chat
  const selectChat = (chatId: string) => {
    setActiveChatId(chatId)
  }

  // Delete a chat
  const deleteChat = (chatId: string) => {
    const newHistories = chatHistories.filter((chat) => chat.id !== chatId)
    setChatHistories(newHistories)

    // If active chat is deleted, select first available chat or create new one
    if (chatId === activeChatId) {
      if (newHistories.length > 0) {
        setActiveChatId(newHistories[0].id)
      } else {
        createNewChat()
      }
    }
  }

  return (
    <div className="chat-container">
      <Sidebar
        chatHistories={chatHistories}
        activeChatId={activeChatId}
        onSelectChat={selectChat}
        onCreateNewChat={createNewChat}
        onDeleteChat={deleteChat}
        onLogout={onLogout}
        username={user}
      />

      <div className="chat-main">
        <div className="chat-messages">
          {activeChat?.messages.map((message) => (
            <ChatMessage key={message.id} message={message} user={user} />
          ))}
          {isLoading && (
            <div className="loading-indicator">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <ChatInput onSendMessage={sendMessage} isLoading={isLoading} />
      </div>
    </div>
  )
}

export default Chat
