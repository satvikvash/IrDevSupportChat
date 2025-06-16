"use client"

import type React from "react"
import { useState } from "react"
import Login from "./components/Login"
import Chat from "./components/Chat"
import "./App.css"

const App: React.FC = () => {
  const [isLoggedIn, setIsLoggedIn] = useState<boolean>(false)
  const [user, setUser] = useState<string>("")

  const handleLogin = (username: string) => {
    setUser(username)
    setIsLoggedIn(true)
  }

  const handleLogout = () => {
    setIsLoggedIn(false)
    setUser("")
  }

  return (
    <div className="App">
      {!isLoggedIn ? <Login onLogin={handleLogin} /> : <Chat user={user} onLogout={handleLogout} />}
    </div>
  )
}

export default App
