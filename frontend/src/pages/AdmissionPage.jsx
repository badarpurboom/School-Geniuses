import { useEffect, useState } from "react";
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

function AdmissionPage() {
  const [form] = Form.useForm();
  const [classes, setClasses] = useState([]);
  const [fileList, setFileList] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const loadClasses = async () => {
      try {
        const { data } = await api.get("/classes/");
        setClasses(data || []);
      } catch (_err) {
        message.error("Classes load nahi hui");
      }
    };
    loadClasses();
  }, []);

  const classOptions = classes.map((item) => ({
    label: `${item.name} - ${item.section}`,
    value: String(item.id)
  }));

  const handleClassChange = (classId) => {
    const selected = classes.find((item) => String(item.id) === String(classId));
    if (selected) {
      form.setFieldsValue({
        student_class: selected.name,
        section: selected.section
      });
    }
  };

  const handleSubmit = async (values) => {
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append("name", values.name);
      formData.append("gender", values.gender);
      formData.append("dob", values.dob.format("YYYY-MM-DD"));
      formData.append("admission_date", values.admission_date.format("YYYY-MM-DD"));
      formData.append("student_class", values.student_class);
      formData.append("section", values.section);
      formData.append("father_name", values.father_name);
      formData.append("father_phone", values.father_phone || "");
      formData.append("mother_name", values.mother_name);
      formData.append("mother_phone", values.mother_phone || "");
      formData.append("address", values.address || "");
      formData.append("remarks", values.remarks || "");

      const fileObj = fileList[0]?.originFileObj;
      if (fileObj) {
        formData.append("document", fileObj);
      }

      await api.post("/students/create/", formData, {
        headers: { "Content-Type": "multipart/form-data" }
      });

      message.success("Student admission saved successfully");
      form.resetFields();
      setFileList([]);
    } catch (_err) {
      message.error("Admission save failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card className="page-card">
      <Title level={2} className="page-title">
        Student Admission
      </Title>
      <Paragraph className="page-subtitle">
        Register new students with class, guardian and document details.
      </Paragraph>

      <Form form={form} layout="vertical" onFinish={handleSubmit} autoComplete="off">
        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item
              label="Student Name"
              name="name"
              rules={[{ required: true, message: "Name required" }]}
            >
              <Input placeholder="Enter student name" />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item
              label="Gender"
              name="gender"
              rules={[{ required: true, message: "Gender required" }]}
            >
              <Select options={["Male", "Female", "Other"].map((g) => ({ label: g, value: g }))} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item
              label="Date of Birth"
              name="dob"
              rules={[{ required: true, message: "DOB required" }]}
            >
              <DatePicker style={{ width: "100%" }} format="DD/MM/YYYY" />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item
              label="Admission Date"
              name="admission_date"
              rules={[{ required: true, message: "Admission date required" }]}
            >
              <DatePicker style={{ width: "100%" }} format="DD/MM/YYYY" />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item
              label="Class - Section"
              name="class_id"
              rules={[{ required: true, message: "Class required" }]}
            >
              <Select options={classOptions} onChange={handleClassChange} placeholder="Select class" />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Row gutter={12}>
              <Col span={12}>
                <Form.Item label="Class" name="student_class" rules={[{ required: true }]}>
                  <Input disabled />
                </Form.Item>
              </Col>
              <Col span={12}>
                <Form.Item label="Section" name="section" rules={[{ required: true }]}>
                  <Input disabled />
                </Form.Item>
              </Col>
            </Row>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item
              label="Father Name"
              name="father_name"
              rules={[{ required: true, message: "Father name required" }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item
              label="Father Phone"
              name="father_phone"
              rules={[{ pattern: /^\d{10}$/, message: "10 digit number" }]}
            >
              <Input maxLength={10} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item
              label="Mother Name"
              name="mother_name"
              rules={[{ required: true, message: "Mother name required" }]}
            >
              <Input />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item
              label="Mother Phone"
              name="mother_phone"
              rules={[{ pattern: /^\d{10}$/, message: "10 digit number" }]}
            >
              <Input maxLength={10} />
            </Form.Item>
          </Col>
        </Row>

        <Row gutter={16}>
          <Col xs={24} md={12}>
            <Form.Item label="Address" name="address">
              <Input.TextArea rows={3} />
            </Form.Item>
          </Col>
          <Col xs={24} md={12}>
            <Form.Item label="Remarks" name="remarks">
              <Input.TextArea rows={3} />
            </Form.Item>
          </Col>
        </Row>

        <Form.Item label="Student Document (PDF)">
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

        <Space>
          <Button type="primary" htmlType="submit" loading={loading}>
            Submit Admission
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

export default AdmissionPage;
