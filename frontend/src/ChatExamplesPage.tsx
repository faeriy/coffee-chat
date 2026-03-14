import React, { useEffect, useState } from "react";
import { Button, Card, Typography, message } from "antd";

import { AUTH_TOKEN_KEY, apiClient, setAuthToken } from "./apiClient";

interface User {
  id: number;
  username: string;
  email: string;
  created_at: string;
}

/** Example chat messages for auth testing (static). */
const EXAMPLE_MESSAGES = [
  { id: 1, from: "coffee", text: "Welcome to Coffee Chat! Your auth is working.", time: "10:00" },
  { id: 2, from: "me", text: "Thanks! I logged in with JWT / Google.", time: "10:01" },
  { id: 3, from: "coffee", text: "Use the “Call /users/me” button to verify your token.", time: "10:02" },
];

const { Title, Paragraph, Text } = Typography;

interface ChatExamplesPageProps {
  onLogout: () => void;
}

/**
 * Simple page with chat examples for auth testing after successful login (JWT or Google).
 * Shows current user from GET /users/me and static example messages.
 */
export const ChatExamplesPage: React.FC<ChatExamplesPageProps> = ({ onLogout }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [meLoading, setMeLoading] = useState(false);

  const fetchMe = async () => {
    setMeLoading(true);
    try {
      const res = await apiClient.get<User>("/users/me");
      setUser(res.data);
      message.success("Token valid. Current user loaded.");
    } catch {
      message.error("Token invalid or expired. Please log in again.");
      onLogout();
    } finally {
      setMeLoading(false);
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMe();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    setAuthToken(null);
    onLogout();
  };

  return (
    <div
      style={{
        minHeight: "100vh",
        background: "linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)",
        padding: "24px 48px",
        boxSizing: "border-box",
      }}
    >
      {/* Desktop-first: wide content area */}
      <div style={{ maxWidth: 1000, margin: "0 auto", minWidth: 720 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 24 }}>
          <Title level={3} style={{ color: "#fff", margin: 0 }}>
            Coffee Chat ☕
          </Title>
          <Button type="default" onClick={handleLogout}>
            Log out
          </Button>
        </div>

        <Card title="Auth check" style={{ marginBottom: 16 }}>
          {loading && !user ? (
            <Paragraph>Loading...</Paragraph>
          ) : user ? (
            <>
              <Paragraph>
                <Text strong>Logged in as:</Text> {user.username} ({user.email})
              </Paragraph>
              <Button type="primary" loading={meLoading} onClick={fetchMe}>
                Call GET /users/me
              </Button>
            </>
          ) : (
            <Paragraph>Could not load user. Try “Call GET /users/me” or log in again.</Paragraph>
          )}
        </Card>

        <Card title="Chat examples (static)">
          {EXAMPLE_MESSAGES.map((msg) => (
            <div
              key={msg.id}
              style={{
                marginBottom: 12,
                padding: 12,
                borderRadius: 8,
                background: msg.from === "me" ? "#e6f4ff" : "#f5f5f5",
                marginLeft: msg.from === "me" ? 48 : 0,
                marginRight: msg.from === "me" ? 0 : 48,
                maxWidth: "85%",
              }}
            >
              <Text type="secondary" style={{ fontSize: 12 }}>
                {msg.from} · {msg.time}
              </Text>
              <div style={{ marginTop: 4 }}>{msg.text}</div>
            </div>
          ))}
        </Card>
      </div>
    </div>
  );
};

export default ChatExamplesPage;
