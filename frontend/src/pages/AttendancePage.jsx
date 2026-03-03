import { useCallback, useRef, useState } from "react";
import { Alert, Button, Card, Descriptions, Space, Typography, message } from "antd";
import QRScanner from "../components/QRScanner";
import api from "../api/client";

const { Title, Paragraph } = Typography;

function AttendancePage() {
  const [attendanceInfo, setAttendanceInfo] = useState(null);
  const [error, setError] = useState("");
  const [scannerKey, setScannerKey] = useState(0);
  const lastIdRef = useRef("");

  const onScan = useCallback(async (decodedText) => {
    const studentId = (decodedText || "").trim();
    if (!studentId || studentId === lastIdRef.current) {
      return;
    }

    lastIdRef.current = studentId;
    setError("");

    try {
      const { data } = await api.post("/mark-attendance/", { student_id: studentId });
      setAttendanceInfo(data);
      if (data?.message === "Already Marked Today") {
        message.info(`${data.name}: ${data.message}`);
      } else {
        message.success(`Attendance marked: ${data.name}`);
      }
    } catch (err) {
      const msg = err?.response?.data?.message || "Attendance mark failed";
      setAttendanceInfo(null);
      setError(msg);
      message.error(msg);
    }
  }, []);

  const resetForNext = () => {
    lastIdRef.current = "";
    setAttendanceInfo(null);
    setError("");
    setScannerKey((prev) => prev + 1);
  };

  return (
    <Space direction="vertical" size={16} style={{ width: "100%" }}>
      <Card className="page-card">
        <Title level={2} className="page-title">
          Smart QR Attendance
        </Title>
        <Paragraph className="page-subtitle">
          Scan student QR code to mark present attendance instantly.
        </Paragraph>

        <div className="qr-panel">
          <QRScanner
            key={scannerKey}
            elementId={`qr-reader-${scannerKey}`}
            onScan={onScan}
            onError={(msg) => setError(msg)}
          />
        </div>

        <Space style={{ marginTop: 12 }}>
          <Button type="primary" onClick={resetForNext}>
            Next Student
          </Button>
        </Space>
      </Card>

      {attendanceInfo && (
        <Card className="page-card">
          <Descriptions title="Attendance Marked" column={{ xs: 1, sm: 2, md: 3 }} bordered>
            <Descriptions.Item label="Name">{attendanceInfo.name}</Descriptions.Item>
            <Descriptions.Item label="Class">{attendanceInfo.class}</Descriptions.Item>
            <Descriptions.Item label="Section">{attendanceInfo.section}</Descriptions.Item>
            <Descriptions.Item label="Roll">{attendanceInfo.roll}</Descriptions.Item>
            <Descriptions.Item label="Date">{attendanceInfo.date}</Descriptions.Item>
            <Descriptions.Item label="Status">{attendanceInfo.message}</Descriptions.Item>
          </Descriptions>
        </Card>
      )}

      {error && <Alert type="error" showIcon message={error} />}
    </Space>
  );
}

export default AttendancePage;
