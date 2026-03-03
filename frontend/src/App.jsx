import { useMemo, useState } from "react";
import {
  App as AntdApp,
  Avatar,
  Button,
  ConfigProvider,
  Layout,
  Menu,
  Space,
  Typography
} from "antd";
import {
  BookOutlined,
  DashboardOutlined,
  DollarCircleOutlined,
  FileTextOutlined,
  LogoutOutlined,
  MessageOutlined,
  TeamOutlined,
  UserOutlined,
  UsergroupAddOutlined
} from "@ant-design/icons";
import LoginPage from "./pages/LoginPage";
import DashboardPage from "./pages/DashboardPage";
import AdmissionPage from "./pages/AdmissionPage";
import StaffPage from "./pages/StaffPage";
import AcademicsPage from "./pages/AcademicsPage";
import AttendancePage from "./pages/AttendancePage";
import AccountsPage from "./pages/AccountsPage";
import ExaminationPage from "./pages/ExaminationPage";
import SchoolLLMPage from "./pages/SchoolLLMPage";

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

const STORAGE_KEY = "school_erp_auth";

const MENU_ITEMS = [
  { key: "dashboard", icon: <DashboardOutlined />, label: "Dashboard" },
  { key: "admission", icon: <UserOutlined />, label: "Admission" },
  { key: "staff", icon: <UsergroupAddOutlined />, label: "Staff" },
  { key: "academics", icon: <BookOutlined />, label: "Academics" },
  { key: "attendance", icon: <TeamOutlined />, label: "Attendance" },
  { key: "accounts", icon: <DollarCircleOutlined />, label: "Accounts" },
  { key: "examination", icon: <FileTextOutlined />, label: "Examination" },
  { key: "llm", icon: <MessageOutlined />, label: "School LLM" }
];

function readSavedAuth() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) {
      return null;
    }
    const parsed = JSON.parse(raw);
    return parsed?.token ? parsed : null;
  } catch (_err) {
    return null;
  }
}

function AppShell({ auth, onLogout }) {
  const [activeMenu, setActiveMenu] = useState("dashboard");

  const content = useMemo(() => {
    switch (activeMenu) {
      case "dashboard":
        return <DashboardPage />;
      case "admission":
        return <AdmissionPage />;
      case "staff":
        return <StaffPage />;
      case "academics":
        return <AcademicsPage />;
      case "attendance":
        return <AttendancePage />;
      case "accounts":
        return <AccountsPage />;
      case "examination":
        return <ExaminationPage />;
      case "llm":
        return <SchoolLLMPage />;
      default:
        return <DashboardPage />;
    }
  }, [activeMenu]);

  return (
    <Layout className="shell-layout">
      <Sider breakpoint="lg" collapsedWidth={0} width={250} className="shell-sider">
        <div className="brand">
          <p className="brand-title">School ERP Console</p>
          <p className="brand-sub">React + Ant Design</p>
        </div>
        <Menu
          theme="dark"
          mode="inline"
          selectedKeys={[activeMenu]}
          items={MENU_ITEMS}
          onClick={(event) => setActiveMenu(event.key)}
          style={{ borderInlineEnd: "none", marginTop: 8 }}
        />
      </Sider>

      <Layout>
        <Header className="shell-header">
          <Text strong>{MENU_ITEMS.find((item) => item.key === activeMenu)?.label}</Text>
          <Space>
            <Avatar style={{ backgroundColor: "#0f766e" }}>
              {(auth?.username || "A").slice(0, 1).toUpperCase()}
            </Avatar>
            <Text>{auth?.username || "Admin"}</Text>
            <Button danger icon={<LogoutOutlined />} onClick={onLogout}>
              Logout
            </Button>
          </Space>
        </Header>
        <Content className="shell-content">{content}</Content>
      </Layout>
    </Layout>
  );
}

function App() {
  const [auth, setAuth] = useState(readSavedAuth());

  const handleLogin = (payload) => {
    const nextAuth = {
      token: payload.token,
      username: payload.username || "admin"
    };
    localStorage.setItem(STORAGE_KEY, JSON.stringify(nextAuth));
    setAuth(nextAuth);
  };

  const handleLogout = () => {
    localStorage.removeItem(STORAGE_KEY);
    setAuth(null);
  };

  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: "#0f766e",
          borderRadius: 10,
          fontSize: 14,
          colorLink: "#0b4d90"
        }
      }}
    >
      <AntdApp>
        {auth?.token ? (
          <AppShell auth={auth} onLogout={handleLogout} />
        ) : (
          <LoginPage onLogin={handleLogin} />
        )}
      </AntdApp>
    </ConfigProvider>
  );
}

export default App;
