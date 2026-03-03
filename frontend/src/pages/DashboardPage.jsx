import { useCallback, useEffect, useMemo, useState } from "react";
import { Button, Card, Col, Empty, Row, Space, Statistic, Typography, message } from "antd";
import {
  TeamOutlined,
  UsergroupAddOutlined,
  CheckCircleOutlined,
  ReloadOutlined
} from "@ant-design/icons";
import ReactECharts from "echarts-for-react";
import api from "../api/client";

const { Title, Paragraph } = Typography;

function DashboardPage() {
  const [loading, setLoading] = useState(false);
  const [stats, setStats] = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [income, setIncome] = useState([]);

  const loadDashboard = useCallback(async () => {
    setLoading(true);
    try {
      const [statsRes, attendanceRes, incomeRes] = await Promise.all([
        api.get("/dashboard-stats/"),
        api.get("/dashboard/today-attendance/"),
        api.get("/dashboard/class-income/")
      ]);

      setStats(statsRes.data);
      setAttendance(attendanceRes.data || []);
      setIncome(incomeRes.data || []);
    } catch (_err) {
      message.error("Unable to load dashboard data");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadDashboard();
  }, [loadDashboard]);

  const attendanceOption = useMemo(() => {
    return {
      tooltip: { trigger: "axis" },
      grid: { left: 40, right: 20, top: 30, bottom: 40 },
      xAxis: {
        type: "category",
        data: attendance.map((item) => `${item.class}-${item.section}`),
        axisLabel: { interval: 0, rotate: 25 }
      },
      yAxis: { type: "value", name: "Present" },
      series: [
        {
          name: "Present",
          type: "bar",
          data: attendance.map((item) => item.present),
          itemStyle: { color: "#0f766e", borderRadius: [8, 8, 0, 0] }
        }
      ]
    };
  }, [attendance]);

  const incomeOption = useMemo(() => {
    return {
      tooltip: { trigger: "item" },
      legend: { bottom: 0 },
      series: [
        {
          type: "pie",
          radius: ["48%", "72%"],
          center: ["50%", "45%"],
          data: income.map((item) => ({ value: item.collected, name: item.class })),
          label: { formatter: "{b}" }
        }
      ]
    };
  }, [income]);

  return (
    <Space direction="vertical" size={16} style={{ width: "100%" }}>
      <Card className="page-card" bodyStyle={{ paddingBottom: 10 }}>
        <Row justify="space-between" align="middle" gutter={[12, 12]}>
          <Col>
            <Title className="page-title" level={2}>
              School Command Center
            </Title>
            <Paragraph className="page-subtitle">
              Real-time institutional metrics and operations snapshot.
            </Paragraph>
          </Col>
          <Col>
            <Button icon={<ReloadOutlined />} onClick={loadDashboard} loading={loading}>
              Refresh
            </Button>
          </Col>
        </Row>
      </Card>

      <Row gutter={[16, 16]}>
        <Col xs={24} md={8}>
          <Card className="metric-card" loading={loading}>
            <Statistic
              title="Total Students"
              value={stats?.total_students || 0}
              prefix={<TeamOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card className="metric-card" loading={loading}>
            <Statistic
              title="Present Today"
              value={stats?.present_today || 0}
              prefix={<CheckCircleOutlined />}
              suffix={`(${stats?.attendance_percent || 0}%)`}
            />
          </Card>
        </Col>
        <Col xs={24} md={8}>
          <Card className="metric-card" loading={loading}>
            <Statistic
              title="Total Staff"
              value={stats?.total_staff || 0}
              prefix={<UsergroupAddOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={[16, 16]}>
        <Col xs={24} xl={12}>
          <Card className="page-card" title="Section-wise Attendance" loading={loading}>
            {attendance.length ? (
              <ReactECharts option={attendanceOption} style={{ height: 360 }} />
            ) : (
              <Empty description="No attendance data" />
            )}
          </Card>
        </Col>
        <Col xs={24} xl={12}>
          <Card className="page-card" title="Class-wise Fee Collection" loading={loading}>
            {income.length ? (
              <ReactECharts option={incomeOption} style={{ height: 360 }} />
            ) : (
              <Empty description="No fee data" />
            )}
          </Card>
        </Col>
      </Row>
    </Space>
  );
}

export default DashboardPage;
