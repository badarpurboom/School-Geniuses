import { useCallback, useEffect, useMemo, useState } from "react";
import dayjs from "dayjs";
import {
  Alert,
  Button,
  Card,
  Col,
  Form,
  Input,
  Select,
  Row,
  Space,
  Table,
  Tabs,
  TimePicker,
  Typography,
  message
} from "antd";
import api from "../api/client";

const { Title, Paragraph, Text } = Typography;
const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];

function createDefaultPeriods(subjectNames) {
  const names = subjectNames.length ? subjectNames : [""];
  return names.map((subject, idx) => {
    const base = dayjs().startOf("day").hour(9).minute(0).second(0).add(idx * 45, "minute");
    return {
      key: idx + 1,
      subject,
      teacher: "",
      time_from: base,
      time_to: base.add(40, "minute")
    };
  });
}

function AcademicsPage() {
  const [classes, setClasses] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [loadingMeta, setLoadingMeta] = useState(false);

  const [subjectName, setSubjectName] = useState("");
  const [addingSubject, setAddingSubject] = useState(false);

  const [classForm] = Form.useForm();
  const [creatingClass, setCreatingClass] = useState(false);

  const [ttClassId, setTtClassId] = useState();
  const [ttDay, setTtDay] = useState("Monday");
  const [ttClassSubjects, setTtClassSubjects] = useState([]);
  const [ttTeachers, setTtTeachers] = useState([]);
  const [periods, setPeriods] = useState([]);
  const [ttLoading, setTtLoading] = useState(false);
  const [savingTimetable, setSavingTimetable] = useState(false);

  const [promoteCurrentClass, setPromoteCurrentClass] = useState();
  const [promoteTargetClass, setPromoteTargetClass] = useState();
  const [promoteStudents, setPromoteStudents] = useState([]);
  const [selectedStudentIds, setSelectedStudentIds] = useState([]);
  const [loadingPromotion, setLoadingPromotion] = useState(false);
  const [promoting, setPromoting] = useState(false);

  const loadMeta = useCallback(async () => {
    setLoadingMeta(true);
    try {
      const [classesRes, subjectsRes] = await Promise.all([api.get("/classes/"), api.get("/subjects/")]);
      setClasses(classesRes.data || []);
      setSubjects(subjectsRes.data || []);
    } catch (_err) {
      message.error("Classes/subjects load nahi hue");
    } finally {
      setLoadingMeta(false);
    }
  }, []);

  useEffect(() => {
    loadMeta();
  }, [loadMeta]);

  const classOptions = classes.map((item) => ({
    label: `${item.name} - ${item.section}`,
    value: String(item.id)
  }));

  const subjectOptions = subjects.map((item) => ({
    label: item.name,
    value: item.id
  }));

  const loadTimetableContext = useCallback(async (classId, day) => {
    if (!classId) {
      return;
    }

    setTtLoading(true);
    try {
      const [classSubjectsRes, teachersRes] = await Promise.all([
        api.get(`/class-subjects/${classId}/`),
        api.get("/teachers/")
      ]);

      const classSubjectNames = (classSubjectsRes.data || []).map((item) => item.subject_name);
      setTtClassSubjects(classSubjectNames);
      setTtTeachers((teachersRes.data || []).map((item) => item.name));

      let timetableRows = [];
      try {
        const ttRes = await api.get(`/timetable/${classId}/${day}/`);
        timetableRows = ttRes.data || [];
      } catch (_err) {
        timetableRows = [];
      }

      if (timetableRows.length) {
        setPeriods(
          timetableRows.map((row, idx) => ({
            key: idx + 1,
            subject: row.subject || classSubjectNames[0] || "",
            teacher: row.teacher || "",
            time_from: dayjs(`1970-01-01T${row.time_from}`),
            time_to: dayjs(`1970-01-01T${row.time_to}`)
          }))
        );
      } else {
        setPeriods(createDefaultPeriods(classSubjectNames));
      }
    } catch (_err) {
      message.error("Timetable context load failed");
    } finally {
      setTtLoading(false);
    }
  }, []);

  useEffect(() => {
    if (ttClassId) {
      loadTimetableContext(ttClassId, ttDay);
    }
  }, [ttClassId, ttDay, loadTimetableContext]);

  const updatePeriod = (index, field, value) => {
    setPeriods((prev) =>
      prev.map((item, idx) => {
        if (idx !== index) {
          return item;
        }
        return { ...item, [field]: value };
      })
    );
  };

  const handleAddSubject = async () => {
    if (!subjectName.trim()) {
      message.warning("Subject name required");
      return;
    }

    setAddingSubject(true);
    try {
      await api.post("/subjects/create/", { name: subjectName.trim() });
      message.success("Subject added successfully");
      setSubjectName("");
      loadMeta();
    } catch (_err) {
      message.error("Subject add failed");
    } finally {
      setAddingSubject(false);
    }
  };

  const handleCreateClass = async (values) => {
    setCreatingClass(true);
    try {
      await api.post("/class/create/", {
        name: values.name,
        section: values.section,
        subjects: values.subjects
      });
      message.success("Class created successfully");
      classForm.resetFields();
      loadMeta();
    } catch (_err) {
      message.error("Class create failed");
    } finally {
      setCreatingClass(false);
    }
  };

  const handleSaveTimetable = async () => {
    if (!ttClassId) {
      message.warning("Class select karein");
      return;
    }

    const invalid = periods.some(
      (item) =>
        !item.subject ||
        !item.time_from ||
        !item.time_to ||
        !dayjs(item.time_from).isValid() ||
        !dayjs(item.time_to).isValid()
    );
    if (invalid) {
      message.warning("All periods me subject/time fill karein");
      return;
    }

    setSavingTimetable(true);
    try {
      await api.post("/save-timetable/", {
        class_id: Number(ttClassId),
        day: ttDay,
        periods: periods.map((item) => ({
          subject: item.subject,
          teacher: item.teacher || "",
          time_from: item.time_from.format("HH:mm:ss"),
          time_to: item.time_to.format("HH:mm:ss")
        }))
      });
      message.success(`${ttDay} timetable saved`);
      loadTimetableContext(ttClassId, ttDay);
    } catch (_err) {
      message.error("Timetable save failed");
    } finally {
      setSavingTimetable(false);
    }
  };

  const loadPromotionStudents = async () => {
    if (!promoteCurrentClass) {
      message.warning("Current class select karein");
      return;
    }

    setLoadingPromotion(true);
    try {
      const { data } = await api.get("/students/", {
        params: { class_id: promoteCurrentClass }
      });
      setPromoteStudents(data || []);
      setSelectedStudentIds([]);
      message.success("Students loaded");
    } catch (_err) {
      message.error("Students load failed");
    } finally {
      setLoadingPromotion(false);
    }
  };

  const promoteSelected = async () => {
    if (!promoteTargetClass || selectedStudentIds.length === 0) {
      message.warning("Target class and at least one student required");
      return;
    }

    const targetClass = classes.find((item) => String(item.id) === String(promoteTargetClass));
    if (!targetClass) {
      message.warning("Target class invalid");
      return;
    }

    setPromoting(true);
    try {
      await api.post("/students/promote/", {
        student_ids: selectedStudentIds,
        target_class_id: Number(promoteTargetClass),
        target_section: targetClass.section
      });
      message.success("Students promoted successfully");
      setPromoteStudents([]);
      setSelectedStudentIds([]);
    } catch (_err) {
      message.error("Promotion failed");
    } finally {
      setPromoting(false);
    }
  };

  const timetableColumns = useMemo(
    () => [
      {
        title: "Period",
        dataIndex: "key",
        width: 80
      },
      {
        title: "Subject",
        dataIndex: "subject",
        render: (value, _row, index) => (
          <Select
            value={value}
            style={{ width: "100%" }}
            options={ttClassSubjects.map((item) => ({ label: item, value: item }))}
            onChange={(nextValue) => updatePeriod(index, "subject", nextValue)}
          />
        )
      },
      {
        title: "Teacher",
        dataIndex: "teacher",
        render: (value, _row, index) => (
          <Select
            allowClear
            value={value || undefined}
            style={{ width: "100%" }}
            options={ttTeachers.map((item) => ({ label: item, value: item }))}
            onChange={(nextValue) => updatePeriod(index, "teacher", nextValue || "")}
          />
        )
      },
      {
        title: "From",
        dataIndex: "time_from",
        render: (value, _row, index) => (
          <TimePicker
            value={value}
            format="HH:mm"
            onChange={(nextValue) => updatePeriod(index, "time_from", nextValue)}
          />
        )
      },
      {
        title: "To",
        dataIndex: "time_to",
        render: (value, _row, index) => (
          <TimePicker
            value={value}
            format="HH:mm"
            onChange={(nextValue) => updatePeriod(index, "time_to", nextValue)}
          />
        )
      }
    ],
    [ttClassSubjects, ttTeachers]
  );

  const studentColumns = [
    { title: "Name", dataIndex: "name" },
    { title: "Student ID", dataIndex: "student_id" },
    { title: "Roll", dataIndex: "roll_number" },
    { title: "Section", dataIndex: "section" }
  ];

  return (
    <Card className="page-card">
      <Title level={2} className="page-title">
        Academics
      </Title>
      <Paragraph className="page-subtitle">
        Manage subjects, classes, timetables and class promotions.
      </Paragraph>

      <Tabs
        items={[
          {
            key: "subjects",
            label: "Subject Creation",
            children: (
              <Space direction="vertical" size={14} style={{ width: "100%" }}>
                <Row gutter={12}>
                  <Col xs={24} md={12}>
                    <Input
                      value={subjectName}
                      onChange={(e) => setSubjectName(e.target.value)}
                      placeholder="Subject name"
                    />
                  </Col>
                  <Col>
                    <Button type="primary" onClick={handleAddSubject} loading={addingSubject}>
                      Add Subject
                    </Button>
                  </Col>
                </Row>
                <Text type="secondary">Total subjects: {subjects.length}</Text>
              </Space>
            )
          },
          {
            key: "class-creation",
            label: "Class Creation",
            children: (
              <Form form={classForm} layout="vertical" onFinish={handleCreateClass} autoComplete="off">
                <Row gutter={16}>
                  <Col xs={24} md={8}>
                    <Form.Item
                      label="Class Name"
                      name="name"
                      rules={[{ required: true, message: "Class name required" }]}
                    >
                      <Input placeholder="Example: Class 6" />
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={8}>
                    <Form.Item
                      label="Section"
                      name="section"
                      rules={[{ required: true, message: "Section required" }]}
                    >
                      <Input placeholder="A / B / C" />
                    </Form.Item>
                  </Col>
                  <Col xs={24} md={8}>
                    <Form.Item
                      label="Subjects"
                      name="subjects"
                      rules={[{ required: true, message: "At least one subject required" }]}
                    >
                      <Select mode="multiple" options={subjectOptions} placeholder="Select subjects" />
                    </Form.Item>
                  </Col>
                </Row>
                <Button type="primary" htmlType="submit" loading={creatingClass}>
                  Create Class
                </Button>
              </Form>
            )
          },
          {
            key: "timetable",
            label: "Class Time Table",
            children: (
              <Space direction="vertical" size={14} style={{ width: "100%" }}>
                <Row gutter={12}>
                  <Col xs={24} md={8}>
                    <Select
                      placeholder="Select class"
                      value={ttClassId}
                      options={classOptions}
                      onChange={setTtClassId}
                      style={{ width: "100%" }}
                    />
                  </Col>
                  <Col xs={24} md={8}>
                    <Select
                      value={ttDay}
                      options={DAYS.map((item) => ({ label: item, value: item }))}
                      onChange={setTtDay}
                      style={{ width: "100%" }}
                    />
                  </Col>
                  <Col>
                    <Button onClick={() => ttClassId && loadTimetableContext(ttClassId, ttDay)}>Reload</Button>
                  </Col>
                </Row>

                {!ttClassId && (
                  <Alert type="info" showIcon message="Timetable edit karne ke liye class select karein" />
                )}

                {ttClassId && (
                  <Table
                    rowKey="key"
                    loading={ttLoading}
                    dataSource={periods}
                    columns={timetableColumns}
                    pagination={false}
                    scroll={{ x: 900 }}
                  />
                )}

                <Space>
                  <Button
                    type="dashed"
                    disabled={!ttClassId}
                    onClick={() =>
                      setPeriods((prev) => [
                        ...prev,
                        {
                          key: prev.length + 1,
                          subject: ttClassSubjects[0] || "",
                          teacher: "",
                          time_from: dayjs().startOf("day").hour(9).minute(0).second(0),
                          time_to: dayjs().startOf("day").hour(9).minute(40).second(0)
                        }
                      ])
                    }
                  >
                    Add Period
                  </Button>

                  <Button
                    type="primary"
                    onClick={handleSaveTimetable}
                    loading={savingTimetable}
                    disabled={!ttClassId}
                  >
                    Save {ttDay} Timetable
                  </Button>
                </Space>
              </Space>
            )
          },
          {
            key: "promote",
            label: "Promote",
            children: (
              <Space direction="vertical" size={14} style={{ width: "100%" }}>
                <Row gutter={12}>
                  <Col xs={24} md={8}>
                    <Select
                      placeholder="Current class"
                      value={promoteCurrentClass}
                      options={classOptions}
                      onChange={setPromoteCurrentClass}
                      style={{ width: "100%" }}
                    />
                  </Col>
                  <Col xs={24} md={8}>
                    <Select
                      placeholder="Target class"
                      value={promoteTargetClass}
                      options={classOptions}
                      onChange={setPromoteTargetClass}
                      style={{ width: "100%" }}
                    />
                  </Col>
                  <Col>
                    <Button onClick={loadPromotionStudents} loading={loadingPromotion}>
                      Load Students
                    </Button>
                  </Col>
                </Row>

                <Table
                  rowKey="id"
                  dataSource={promoteStudents}
                  columns={studentColumns}
                  pagination={{ pageSize: 8 }}
                  rowSelection={{
                    selectedRowKeys: selectedStudentIds,
                    onChange: (keys) => setSelectedStudentIds(keys)
                  }}
                />

                <Button
                  type="primary"
                  onClick={promoteSelected}
                  disabled={!selectedStudentIds.length}
                  loading={promoting}
                >
                  Promote Selected Students
                </Button>
              </Space>
            )
          }
        ]}
      />

      <Paragraph type="secondary" style={{ marginTop: 12, marginBottom: 0 }}>
        {loadingMeta ? "Refreshing metadata..." : `Classes: ${classes.length} | Subjects: ${subjects.length}`}
      </Paragraph>
    </Card>
  );
}

export default AcademicsPage;
