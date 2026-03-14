import React, { useEffect, useState } from "react";
import { Button, Card, Divider, Form, Input, Typography, message } from "antd";

import { AUTH_TOKEN_KEY, API_BASE_URL, apiClient, setAuthToken } from "./apiClient";


interface LoginFormValues {
  username: string;
  password: string;
}


interface LoginResponse {
  access_token: string;
  token_type?: string;
}

const { Title, Paragraph } = Typography;

interface LoginPageProps {
  onLoginSuccess?: () => void;
}

/**
 * Login page: username/password and Sign in with Google.
 * On success stores token and calls onLoginSuccess so the app shows the chat examples page.
 */
export const LoginPage: React.FC<LoginPageProps> = ({ onLoginSuccess }) => {
  const [loading, setLoading] = useState<boolean>(false);

  // Handle return from Google OAuth: URL may contain ?token=... or ?error=...
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");
    const error = params.get("error");
    if (token) {
      localStorage.setItem(AUTH_TOKEN_KEY, token);
      setAuthToken(token);
      message.success("Logged in with Google");
      window.history.replaceState({}, document.title, window.location.pathname);
      onLoginSuccess?.();
    }
    if (error) {
      message.error("Google sign-in was denied or failed.");
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, [onLoginSuccess]);

  const handleGoogleLogin = () => {
    window.location.href = `${API_BASE_URL}/auth/google`;
  };

  const handleFinish = async (values: LoginFormValues) => {
    setLoading(true);
    try {
      const body = new URLSearchParams();
      body.set("username", values.username);
      body.set("password", values.password);

      const response = await apiClient.post<LoginResponse>(
        "/auth/login",
        body,
        {
          headers: {
            "Content-Type": "application/x-www-form-urlencoded",
          },
        },
      );

      const token = response.data.access_token;

      localStorage.setItem(AUTH_TOKEN_KEY, token);
      setAuthToken(token);

      message.success("Logged in successfully");
      onLoginSuccess?.();
    } catch (err: unknown) {
      const detail =
        err && typeof err === "object" && "response" in err
          ? (err as { response?: { data?: { detail?: string } } }).response?.data?.detail
          : null;
      message.error(
        typeof detail === "string" ? detail : "Login failed. Please check your credentials."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        width: "100vw",
        height: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        background: "linear-gradient(135deg, #001529, #1677ff)",
        padding: 16,
        boxSizing: "border-box",
      }}
    >
      <Card
        style={{ width: 380, maxWidth: "100%", flexShrink: 0 }}
        bordered={false}
        bodyStyle={{ padding: 24 }}
      >
        <Title level={3} style={{ textAlign: "center", marginBottom: 8 }}>
          Coffee Chat ☕
        </Title>
        <Paragraph style={{ textAlign: "center", marginBottom: 24 }}>
          Sign in to continue
        </Paragraph>

        {/* Ant Design form, strongly typed with `LoginFormValues` */}
        <Form<LoginFormValues>
          layout="vertical"
          onFinish={handleFinish}
          initialValues={{ username: "", password: "" }}
        >
          <Form.Item
            label="Username"
            name="username"
            rules={[
              { required: true, message: "Please enter your username" },
            ]}
          >
            <Input placeholder="your-username" autoComplete="username" />
          </Form.Item>

          <Form.Item
            label="Password"
            name="password"
            rules={[
              { required: true, message: "Please enter your password" },
            ]}
          >
            <Input.Password
              placeholder="••••••••"
              autoComplete="current-password"
            />
          </Form.Item>

          <Form.Item style={{ marginTop: 16 }}>
            <Button
              type="primary"
              htmlType="submit"
              block
              loading={loading}
            >
              Log in
            </Button>
          </Form.Item>

          <Divider plain>or</Divider>

          <Form.Item>
            <Button block onClick={handleGoogleLogin}>
              Sign in with Google
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

export default LoginPage;
