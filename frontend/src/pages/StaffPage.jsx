import { useState } from "react";
import {
  Button,
  Card,
  Col,
  DatePicker,
  Form,
  Input,
  Row,
  Select,
  Space,
  Typography,
  Upload,
  message
} from "antd";
import { UploadOutlined } from "@ant-design/icons";
import api from "../api/client";

const { Title, Paragraph } = Typography;

function StaffPage() {
  const [form] = Form.useForm();
  const [fileList, setFileList] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("name", values.name);
      formData.append("father_name", values.father_name || "");
      formData.append("phone", values.phone || "");
      formData.append("gender", values.gender);
      formData.append("dob", values.dob.format("YYYY-MM-DD"));
      formData.append("aadhaar", values.aadhaar || "");
      formData.append("marital_status", values.marital_status || "");
      formData.append("role", values.role);
      formData.append("joining_date", values.joining_date.format("YYYY-MM-DD"));
      formData.append("remarks", values.remarks || "");

      const fileObj = fileList[0]?.originFileObj;
      if (fileObj) {
        formData.append("document", fileObj);
      }

      await api.post("/staff/create/", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      message.success("Staff registered successfully");
      form.resetFields();
      setFileList([]);
    } catch (_err) {
      message.error("Staff save failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="page-card">
      <Title level={2} className="page-title">
        Staff Registration
      </Title>
      <Paragraph className="page-subtitle">
        Add staff profiles, role assignments and supporting documents.
      </Paragraph>

      <Form form={form} layout="vertical" onFinish={handleSubmit} autoComplete="off">
        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item
              label="Staff Name"
              name="name"
              rules={[{ required: true, message: "Name required" }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item
              label="Phone"
              name="phone"
              rules={[{ pattern: /^\d{10}$/, message: "10 digit number" }]}
            >
              <Input maxLength={10} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item
              label="Gender"
              name="gender"
              rules={[{ required: true, message: "Gender required" }]}
            >
              <Select options={["Male", "Female", "Other"].map((item) => ({ label: item, value: item }))} />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item
              label="Date of Birth"
              name="dob"
              rules={[{ required: true, message: "DOB required" }]}
            >
              <DatePicker style={{ width: "100%" }} format="DD/MM/YYYY" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item label="Father Name" name="father_name">
              <Input />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item label="Aadhaar" name="aadhaar">
              <Input maxLength={12} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item label="Marital Status" name="marital_status">
              <Select
                options={["Single", "Married", "Other"].map((item) => ({ label: item, value: item }))}
              />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item
              label="Role"
              name="role"
              rules={[{ required: true, message: "Role required" }]}
            >
              <Select
                options={[
                  "Teacher",
                  "Principal",
                  "Security Guard",
                  "Cleaner",
                  "Other"
                ].map((item) => ({ label: item, value: item }))}
              />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item
              label="Joining Date"
              name="joining_date"
              rules={[{ required: true, message: "Joining date required" }]}
            >
              <DatePicker style={{ width: "100%" }} format="DD/MM/YYYY" />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item label="Staff Document (PDF)">
              <Upload
                fileList={fileList}
                maxCount={1}
                accept=".pdf"
                beforeUpload={() => false}
                onChange={({ fileList: nextFileList }) => setFileList(nextFileList)}
              >
                <Button icon={<UploadOutlined />}>Select PDF</Button>
              </Upload>
            </Form.Item>
          </Col>
        </Row>

        <Form.Item label="Remarks" name="remarks">
          <Input.TextArea rows={3} />
        </Form.Item>

        <Space>
          <Button type="primary" htmlType="submit" loading={loading}>
            Submit Staff
          </Button>
          <Button
            onClick={() => {
              form.resetFields();
              setFileList([]);
            }}
          >
            Reset
          </Button>
        </Space>
      </Form>
    </Card>
  );
}

export default StaffPage;
