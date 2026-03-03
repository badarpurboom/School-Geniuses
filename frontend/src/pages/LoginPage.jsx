import { useState } from "react";
import { Button, Card, Col, Form, Input, Row, Typography, message } from "antd";
import { LockOutlined, UserOutlined } from "@ant-design/icons";
import api from "../api/client";

const { Title, Text } = Typography;

function LoginPage({ onLogin }) {
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const { data } = await api.post("/login/", values);
      onLogin(data);
      message.success("Login successful");
    } catch (_err) {
      message.error("Invalid credentials or backend unavailable");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Row align="middle" justify="center" style={{ minHeight: "100vh", padding: 16 }}>
      <Col xs={24} sm={18} md={12} lg={8}>
        <Card className="page-card">
          <Title level={2} style={{ marginBottom: 4 }}>
            School ERP Console
          </Title>
          <Text type="secondary">Secure access for school operations and analytics</Text>

          <Form
            layout="vertical"
            onFinish={handleSubmit}
            style={{ marginTop: 24 }}
            autoComplete="off"
          >
            <Form.Item
              name="username"
              label="Username"
              rules={[{ required: true, message: "Username required" }]}
            >
              <Input prefix={<UserOutlined />} placeholder="Enter username" />
            </Form.Item>

            <Form.Item
              name="password"
              label="Password"
              rules={[{ required: true, message: "Password required" }]}
            >
              <Input.Password prefix={<LockOutlined />} placeholder="Enter password" />
            </Form.Item>

            <Button type="primary" htmlType="submit" block loading={loading}>
              Sign In
            </Button>
          </Form>
        </Card>
      </Col>
    </Row>
  );
}

export default LoginPage;
