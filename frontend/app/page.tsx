"use client";

import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { useState, useRef, useEffect } from "react";

const API_URL = "http://localhost:8000";

type Message = {
  role: "user" | "assistant";
  content: string;
};

export default function Home() {
  const [url, setUrl] = useState("");
  const [videoId, setVideoId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [question, setQuestion] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  async function handleLoadVideo() {
    if (!url.trim()) return;
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/get_transcript`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url }),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Failed to load transcript");
      setVideoId(data.video_id);
      setMessages([]);
    } catch (err) {
      alert(err instanceof Error ? err.message : "Failed to load video");
    } finally {
      setLoading(false);
    }
  }

  async function handleSend() {
    if (!question.trim() || !videoId) return;
    const userMessage: Message = { role: "user", content: question };
    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    setQuestion("");
    setSending(true);
    try {
      const res = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          video_id: videoId,
          question: question,
          history: messages,
        }),
      });
      if (!res.ok) throw new Error("Failed to get response");
      const data = await res.json();
      setMessages([
        ...updatedMessages,
        { role: "assistant", content: data.response },
      ]);
    } catch (err) {
      setMessages([
        ...updatedMessages,
        { role: "assistant", content: "Sorry, something went wrong." },
      ]);
    } finally {
      setSending(false);
    }
  }

  return (
    <div className="flex flex-col items-center min-h-screen bg-background p-4">
      <div className="w-full max-w-2xl flex flex-col gap-4 flex-1">
        <h1 className="text-2xl font-bold text-center mt-4">YouTube Q&A</h1>

        <div className="flex gap-2">
          <Input
            placeholder="Paste a YouTube URL..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleLoadVideo()}
            disabled={loading}
          />
          <Button onClick={handleLoadVideo} disabled={loading}>
            {loading ? "Loading..." : "Load"}
          </Button>
        </div>

        {videoId && (
          <p className="text-sm text-muted-foreground text-center">
            Video loaded. Ask anything about it below.
          </p>
        )}

        <div className="flex-1 overflow-y-auto border rounded-lg p-4 min-h-[400px] max-h-[60vh] flex flex-col gap-3">
          {messages.length === 0 && (
            <p className="text-muted-foreground text-center m-auto">
              {videoId
                ? "Ask a question to get started"
                : "Load a YouTube video to begin"}
            </p>
          )}
          {messages.map((msg, i) => (
            <div
              key={i}
              className={`max-w-[80%] rounded-lg px-3 py-2 text-sm whitespace-pre-wrap ${
                msg.role === "user"
                  ? "self-end bg-primary text-primary-foreground"
                  : "self-start bg-muted text-foreground"
              }`}
            >
              {msg.content}
            </div>
          ))}
          {sending && (
            <div className="self-start bg-muted text-muted-foreground rounded-lg px-3 py-2 text-sm">
              Thinking...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        <div className="flex gap-2">
          <Input
            placeholder="Ask a question..."
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            disabled={!videoId || sending}
          />
          <Button onClick={handleSend} disabled={!videoId || sending}>
            Send
          </Button>
        </div>
      </div>
    </div>
  );
}
