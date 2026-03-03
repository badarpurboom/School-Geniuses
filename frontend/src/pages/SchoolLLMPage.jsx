import { useMemo, useState } from "react";
import { Button, Card, Input, Space, Typography, message } from "antd";
import { RobotOutlined, SendOutlined, UserOutlined } from "@ant-design/icons";
import api from "../api/client";

const { Title, Paragraph, Text } = Typography;

function SchoolLLMPage() {
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content: "Namaste. School database se sawal puch sakte hain."
    }
  ]);
  const [prompt, setPrompt] = useState("");
  const [loading, setLoading] = useState(false);

  const chatView = useMemo(
    () =>
      messages.map((item, idx) => (
        <div
          key={`${item.role}-${idx}`}
          className={`chat-item ${item.role === "user" ? "chat-user" : "chat-ai"}`}
        >
          <Space align="start">
            {item.role === "user" ? <UserOutlined /> : <RobotOutlined />}
            <div>
              <Text strong>{item.role === "user" ? "You" : "Assistant"}</Text>
              <div style={{ marginTop: 4, whiteSpace: "pre-wrap" }}>{item.content}</div>
            </div>
          </Space>
        </div>
      )),
    [messages]
  );

  const sendMessage = async () => {
    const text = prompt.trim();
    if (!text) {
      return;
    }

    setMessages((prev) => [...prev, { role: "user", content: text }]);
    setPrompt("");
    setLoading(true);

    try {
      const { data } = await api.post("/ai-db-query/", { query: text });
      const answer = data?.answer || "No answer found.";
      setMessages((prev) => [...prev, { role: "assistant", content: answer }]);
    } catch (_err) {
      message.error("AI service unavailable");
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Backend error. Please try again." }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="page-card">
      <Title level={2} className="page-title">
        School LLM Assistant
      </Title>
      <Paragraph className="page-subtitle">
        Ask natural language questions from school database.
      </Paragraph>

      <div className="chat-box">{chatView}</div>

      <Space.Compact style={{ width: "100%", marginTop: 12 }}>
        <Input.TextArea
          autoSize={{ minRows: 2, maxRows: 5 }}
          placeholder="Example: Show students with low attendance"
          value={prompt}
          onChange={(e) => setPrompt(e.target.value)}
          onPressEnter={(event) => {
            if (!event.shiftKey) {
              event.preventDefault();
              sendMessage();
            }
          }}
        />
        <Button
          type="primary"
          icon={<SendOutlined />}
          onClick={sendMessage}
          loading={loading}
          style={{ height: "auto" }}
        >
          Send
        </Button>
      </Space.Compact>
    </Card>
  );
}

export default SchoolLLMPage;
