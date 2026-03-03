import { useMemo, useState } from "react";
import {
  Alert,
  Button,
  Card,
  Col,
  Divider,
  Form,
  Input,
  InputNumber,
  Row,
  Select,
  Space,
  Tabs,
  Typography,
  message
} from "antd";
import api from "../api/client";

const { Title, Paragraph, Text } = Typography;
const MONTHS = [
  "January",
  "February",
  "March",
  "April",
  "May",
  "June",
  "July",
  "August",
  "September",
  "October",
  "November",
  "December"
];

function AccountsPage() {
  const [lookupId, setLookupId] = useState("");
  const [student, setStudent] = useState(null);
  const [loadingLookup, setLoadingLookup] = useState(false);
  const [savingPayment, setSavingPayment] = useState(false);
  const [form] = Form.useForm();

  const amountPaid = Form.useWatch("amount_paid", form) || 0;
  const estimatedDue = useMemo(() => {
    const fee = Number(student?.monthly_fee || 0);
    return Math.max(0, fee - Number(amountPaid || 0));
  }, [amountPaid, student]);

  const fetchFeeDetails = async () => {
    if (!lookupId.trim()) {
      message.warning("Student ID enter karein");
      return;
    }

    setLoadingLookup(true);
    try {
      const { data } = await api.get(`/get-fee/${lookupId.trim()}/`);
      setStudent(data);
      form.setFieldsValue({
        month: MONTHS[new Date().getMonth()],
        year: new Date().getFullYear(),
        amount_paid: 0
      });
      message.success("Student fee details loaded");
    } catch (_err) {
      setStudent(null);
      message.error("Student fee details nahi mili");
    } finally {
      setLoadingLookup(false);
    }
  };

  const submitPayment = async (values) => {
    if (!student) {
      message.warning("Pehle student load karein");
      return;
    }

    setSavingPayment(true);
    try {
      const payload = {
        student_id: lookupId.trim(),
        amount_paid: Number(values.amount_paid || 0),
        month: values.month,
        year: Number(values.year),
        fixed_fee: Number(student.monthly_fee)
      };

      const { data } = await api.post("/save-fee/", payload);
      message.success(`Payment saved. Due amount: ${data.due}`);
      form.resetFields(["amount_paid"]);
    } catch (_err) {
      message.error("Payment save failed");
    } finally {
      setSavingPayment(false);
    }
  };

  return (
    <Card className="page-card">
      <Title level={2} className="page-title">
        Accounts Manager
      </Title>
      <Paragraph className="page-subtitle">Fee collection, expenses and summary tools.</Paragraph>

      <Tabs
        items={[
          {
            key: "fees",
            label: "Fees Collection",
            children: (
              <Space direction="vertical" size={16} style={{ width: "100%" }}>
                <Row gutter={12}>
                  <Col xs={24} md={10}>
                    <Input
                      placeholder="Student ID"
                      value={lookupId}
                      onChange={(e) => setLookupId(e.target.value)}
                      onPressEnter={fetchFeeDetails}
                    />
                  </Col>
                  <Col>
                    <Button type="primary" onClick={fetchFeeDetails} loading={loadingLookup}>
                      Load Student
                    </Button>
                  </Col>
                </Row>

                {student && (
                  <Card size="small" style={{ borderRadius: 12 }}>
                    <Space direction="vertical" size={2}>
                      <Text strong>
                        {student.name} | {student.class} - {student.section}
                      </Text>
                      <Text>Roll: {student.roll}</Text>
                      <Text>Monthly Fee: {student.monthly_fee}</Text>
                    </Space>
                  </Card>
                )}

                {student && (
                  <Form form={form} layout="vertical" onFinish={submitPayment}>
                    <Row gutter={16}>
                      <Col xs={24} md={8}>
                        <Form.Item
                          label="Month"
                          name="month"
                          rules={[{ required: true, message: "Month required" }]}
                        >
                          <Select options={MONTHS.map((m) => ({ label: m, value: m }))} />
                        </Form.Item>
                      </Col>
                      <Col xs={24} md={8}>
                        <Form.Item
                          label="Year"
                          name="year"
                          rules={[{ required: true, message: "Year required" }]}
                        >
                          <InputNumber style={{ width: "100%" }} min={2000} max={2100} />
                        </Form.Item>
                      </Col>
                      <Col xs={24} md={8}>
                        <Form.Item
                          label="Amount Paid"
                          name="amount_paid"
                          rules={[{ required: true, message: "Amount required" }]}
                        >
                          <InputNumber
                            style={{ width: "100%" }}
                            min={0}
                            formatter={(value) => `${value}`}
                          />
                        </Form.Item>
                      </Col>
                    </Row>

                    <Alert
                      type="info"
                      showIcon
                      message={`Estimated Due: ${estimatedDue}`}
                      style={{ marginBottom: 16 }}
                    />

                    <Button type="primary" htmlType="submit" loading={savingPayment}>
                      Submit Payment
                    </Button>
                  </Form>
                )}
              </Space>
            )
          },
          {
            key: "expenses",
            label: "Expense Tracker",
            children: <Alert type="warning" showIcon message="Expense Tracker coming soon" />
          },
          {
            key: "summary",
            label: "Summary",
            children: <Alert type="warning" showIcon message="Summary dashboard coming soon" />
          }
        ]}
      />

      <Divider />
      <Text type="secondary">Backend compatible with existing fee APIs.</Text>
    </Card>
  );
}

export default AccountsPage;
