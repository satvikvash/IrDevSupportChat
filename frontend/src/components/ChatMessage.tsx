import type React from "react"
import type { Message } from "./Chat"
import "../styles/ChatMessage.css"

interface ChatMessageProps {
  message: Message
  user: string
}

const ChatMessage: React.FC<ChatMessageProps> = ({ message, user }) => {
  return (
    <div className={`chat-message ${message.sender === "user" ? "user-message" : "assistant-message"}`}>
      <div className="message-avatar">
        {message.sender === "user" ? <div className="user-avatar">{user.charAt(0).toUpperCase()}</div> : <div className="assistant-avatar">AI</div>}
      </div>
      <div className="message-content">
        <div className="message-text">{message.content}</div>
        <div className="message-timestamp">
          {message.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
        </div>
      </div>
    </div>
  )
}

export default ChatMessage
