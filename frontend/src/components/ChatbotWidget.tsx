import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./css/ChatbotWidget.css";

const INACTIVITY_TIMEOUT = 5 * 60 * 1000; // 5 minutes
const LOCAL_STORAGE_KEY = 'chatbotSessionId';

const ChatbotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<{ text: string; sender: "user" | "bot" }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inactivityTimer = useRef<number | null>(null);

  // Load session ID from local storage on initial component mount
  useEffect(() => {
    const storedSessionId = localStorage.getItem(LOCAL_STORAGE_KEY);
    if (storedSessionId) {
      setSessionId(storedSessionId);
    }
  }, []);

  const resetInactivityTimer = () => {
    if (inactivityTimer.current) {
      clearTimeout(inactivityTimer.current);
    }
    inactivityTimer.current = window.setTimeout(() => {
      setMessages([]);
      setSessionId(null); // Clear session ID
      localStorage.removeItem(LOCAL_STORAGE_KEY); // Clear from storage
      setIsOpen(false);
    }, INACTIVITY_TIMEOUT);
  };

  useEffect(() => {
    if (isOpen) {
      resetInactivityTimer();
    }
    return () => {
      if (inactivityTimer.current) {
        clearTimeout(inactivityTimer.current);
      }
    };
  }, [isOpen, messages]);

  useEffect(() => {
    if (isOpen) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, isOpen]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMessage = { text: input, sender: "user" as const };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const res = await axios.post(
        `${import.meta.env.VITE_API_URL}chatbot/`,
        {
          query: userMessage.text,
          session_id: sessionId, // Send current session ID (or null if new)
        }
      );
      const botMessage = { text: res.data.answer, sender: "bot" as const };
      setMessages((prev) => [...prev, botMessage]);

      // If this was a new session, save the new session ID
      if (!sessionId && res.data.session_id) {
        const newSessionId = res.data.session_id;
        setSessionId(newSessionId);
        localStorage.setItem(LOCAL_STORAGE_KEY, newSessionId);
      }
    } catch (error) {
      console.error("Chatbot API error:", error);
      const errorMessage = {
        text: "Sorry, I encountered an error. Please try again later.",
        sender: "bot" as const,
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={`chatbot-widget ${isOpen ? "open" : ""}`}>
      {isOpen ? (
        <div className="chatbot-box">
          <div className="chatbot-header">
            <span>AI Assistant</span>
            <button onClick={() => setIsOpen(false)}>×</button>
          </div>
          <div className="chatbot-messages">
            {messages.length === 0 && (
              <div className="msg bot">
                Hello! Ask me about Mushfiqur's projects, experience, or skills.
              </div>
            )}
            {messages.map((msg, index) => (
              <div key={index} className={`msg ${msg.sender}`}>
                {msg.text}
              </div>
            ))}
            {loading && <div className="msg bot loading-dots"><span></span><span></span><span></span></div>}
            <div ref={messagesEndRef} />
          </div>
          <form className="chatbot-input-form" onSubmit={handleSendMessage}>
            <input
              value={input}
              onChange={(e) => {
                setInput(e.target.value);
                resetInactivityTimer();
              }}
              placeholder="Type a message..."
              disabled={loading}
              autoFocus
            />
            <button type="submit" disabled={loading || !input.trim()}>
              Send
            </button>
          </form>
        </div>
      ) : (
        <button className="chatbot-fab" onClick={() => setIsOpen(true)}>
          💬
        </button>
      )}
    </div>
  );
};

export default ChatbotWidget;
