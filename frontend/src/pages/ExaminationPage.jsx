import { useCallback, useEffect, useMemo, useState } from "react";
import dayjs from "dayjs";
import {
  Alert,
  Button,
  Card,
  Col,
  DatePicker,
  Input,
  InputNumber,
  Row,
  Select,
  Space,
  Table,
  Tabs,
  TimePicker,
  Typography,
  message
} from "antd";
import api from "../api/client";

const { Title, Paragraph, Text } = Typography;

function ExaminationPage() {
  const [classes, setClasses] = useState([]);
  const [exams, setExams] = useState([]);
  const [loadingMeta, setLoadingMeta] = useState(false);

  const [createExamName, setCreateExamName] = useState("");
  const [createClassName, setCreateClassName] = useState("");
  const [scheduleRows, setScheduleRows] = useState([]);
  const [creatingExam, setCreatingExam] = useState(false);

  const [selectedExamId, setSelectedExamId] = useState();
  const [selectedSection, setSelectedSection] = useState();
  const [selectedSubject, setSelectedSubject] = useState();
  const [students, setStudents] = useState([]);
  const [marksMap, setMarksMap] = useState({});
  const [savingMarks, setSavingMarks] = useState(false);

  const loadMeta = useCallback(async () => {
    setLoadingMeta(true);
    try {
      const [classRes, examRes] = await Promise.all([api.get("/classes/"), api.get("/exams/")]);
      setClasses(classRes.data || []);
      setExams(examRes.data || []);
    } catch (_err) {
      message.error("Examination data load failed");
    } finally {
      setLoadingMeta(false);
    }
  }, []);

  useEffect(() => {
    loadMeta();
  }, [loadMeta]);

  const uniqueClassNames = useMemo(
    () => Array.from(new Set((classes || []).map((item) => item.name))).sort(),
    [classes]
  );

  const selectedExam = useMemo(
    () => exams.find((item) => Number(item.id) === Number(selectedExamId)),
    [exams, selectedExamId]
  );

  const sectionOptions = useMemo(() => {
    if (!selectedExam) {
      return [];
    }
    return classes
      .filter((item) => item.name === selectedExam.class_name)
      .map((item) => ({
        label: `${item.name} - ${item.section}`,
        value: `${item.name} - ${item.section}`
      }));
  }, [classes, selectedExam]);

  const selectedSubjectMeta = useMemo(() => {
    if (!selectedExam || !selectedSubject) {
      return null;
    }
    return (selectedExam.schedule || []).find((item) => item.subject === selectedSubject) || null;
  }, [selectedExam, selectedSubject]);

  const updateScheduleRow = (index, field, value) => {
    setScheduleRows((prev) =>
      prev.map((row, idx) => {
        if (idx !== index) {
          return row;
        }
        return { ...row, [field]: value };
      })
    );
  };

  const loadClassSubjects = async (className) => {
    setCreateClassName(className);
    setScheduleRows([]);

    if (!className) {
      return;
    }

    try {
      const { data } = await api.get("/subjects/", { params: { class_name: className } });
      const names = (data || []).map((item) => item.name);
      if (!names.length) {
        message.warning("Is class ke liye subjects nahi mile");
      }
      setScheduleRows(
        names.map((name) => ({
          subject: name,
          date: dayjs(),
          time: dayjs().startOf("day").hour(9).minute(0).second(0),
          total_marks: 100,
          description: ""
        }))
      );
    } catch (_err) {
      message.error("Class subjects load failed");
    }
  };

  const createExamSchedule = async () => {
    if (!createExamName.trim() || !createClassName || !scheduleRows.length) {
      message.warning("Exam name, class and subject schedule required");
      return;
    }

    setCreatingExam(true);
    try {
      await api.post("/exams/create-bulk/", {
        exam_name: createExamName.trim(),
        class_name: createClassName,
        schedule: scheduleRows.map((item) => ({
          subject: item.subject,
          date: item.date.format("YYYY-MM-DD"),
          time: item.time.format("HH:mm:ss"),
          total_marks: Number(item.total_marks || 0),
          description: item.description || ""
        }))
      });

      message.success("Exam schedule created");
      setCreateExamName("");
      setCreateClassName("");
      setScheduleRows([]);
      loadMeta();
    } catch (_err) {
      message.error("Exam creation failed");
    } finally {
      setCreatingExam(false);
    }
  };

  useEffect(() => {
    if (!selectedExam) {
      setSelectedSubject(undefined);
      setSelectedSection(undefined);
      setStudents([]);
      setMarksMap({});
      return;
    }

    const firstSubject = selectedExam.schedule?.[0]?.subject;
    setSelectedSubject(firstSubject);
    setSelectedSection(undefined);
    setStudents([]);
    setMarksMap({});
  }, [selectedExamId, selectedExam]);

  const loadStudentsForMarks = async (sectionLabel) => {
    setSelectedSection(sectionLabel);
    setStudents([]);
    setMarksMap({});

    if (!sectionLabel) {
      return;
    }

    try {
      const { data } = await api.get("/students/", {
        params: { section_full: sectionLabel }
      });
      const rows = data || [];
      setStudents(rows);
      const initial = {};
      rows.forEach((item) => {
        initial[item.id] = 0;
      });
      setMarksMap(initial);
    } catch (_err) {
      message.error("Students load failed");
    }
  };

  const saveMarks = async () => {
    if (!selectedExam || !selectedSubject || !students.length) {
      message.warning("Exam, subject aur students required");
      return;
    }

    setSavingMarks(true);
    try {
      await api.post("/marks/save-bulk/", {
        exam_id: Number(selectedExam.id),
        subject: selectedSubject,
        section: selectedSection,
        marks_list: students.map((item) => ({
          student_id: item.id,
          marks: Number(marksMap[item.id] || 0)
        }))
      });
      message.success("Marks saved successfully");
    } catch (_err) {
      message.error("Marks save failed");
    } finally {
      setSavingMarks(false);
    }
  };

  const scheduleColumns = [
    { title: "Subject", dataIndex: "subject", width: 180 },
    {
      title: "Date",
      dataIndex: "date",
      render: (value, _row, index) => (
        <DatePicker
          value={value}
          format="DD/MM/YYYY"
          onChange={(next) => updateScheduleRow(index, "date", next)}
        />
      )
    },
    {
      title: "Time",
      dataIndex: "time",
      render: (value, _row, index) => (
        <TimePicker value={value} format="HH:mm" onChange={(next) => updateScheduleRow(index, "time", next)} />
      )
    },
    {
      title: "Total Marks",
      dataIndex: "total_marks",
      render: (value, _row, index) => (
        <InputNumber
          min={1}
          value={value}
          onChange={(next) => updateScheduleRow(index, "total_marks", next || 0)}
        />
      )
    },
    {
      title: "Description",
      dataIndex: "description",
      render: (value, _row, index) => (
        <Input
          value={value}
          placeholder="Syllabus / remarks"
          onChange={(e) => updateScheduleRow(index, "description", e.target.value)}
        />
      )
    }
  ];

  const marksColumns = [
    { title: "Student Name", dataIndex: "name" },
    { title: "Roll", dataIndex: "roll_number", width: 100 },
    {
      title: `Marks${selectedSubjectMeta ? ` (Max ${selectedSubjectMeta.total_marks})` : ""}`,
      dataIndex: "id",
      width: 220,
      render: (studentId) => (
        <InputNumber
          min={0}
          max={Number(selectedSubjectMeta?.total_marks || 200)}
          value={marksMap[studentId]}
          onChange={(value) =>
            setMarksMap((prev) => ({
              ...prev,
              [studentId]: Number(value || 0)
            }))
          }
        />
      )
    }
  ];

  return (
    <Card className="page-card">
      <Title level={2} className="page-title">
        Examination Management
      </Title>
      <Paragraph className="page-subtitle">
        Create exam schedules and fill student marks by section.
      </Paragraph>

      <Tabs
        items={[
          {
            key: "create",
            label: "Create Exam",
            children: (
              <Space direction="vertical" size={14} style={{ width: "100%" }}>
                <Row gutter={12}>
                  <Col xs={24} md={10}>
                    <Input
                      placeholder="Exam name (Example: Unit Test 1)"
                      value={createExamName}
                      onChange={(e) => setCreateExamName(e.target.value)}
                    />
                  </Col>
                  <Col xs={24} md={10}>
                    <Select
                      placeholder="Select class"
                      value={createClassName || undefined}
                      options={uniqueClassNames.map((item) => ({ label: item, value: item }))}
                      onChange={loadClassSubjects}
                      style={{ width: "100%" }}
                    />
                  </Col>
                </Row>

                {scheduleRows.length > 0 ? (
                  <Table
                    rowKey={(row) => row.subject}
                    dataSource={scheduleRows}
                    columns={scheduleColumns}
                    pagination={false}
                    scroll={{ x: 900 }}
                  />
                ) : (
                  <Alert type="info" showIcon message="Class choose karke subject schedule generate karein" />
                )}

                <Button
                  type="primary"
                  onClick={createExamSchedule}
                  loading={creatingExam}
                  disabled={!scheduleRows.length}
                >
                  Create Exam & Schedule
                </Button>
              </Space>
            )
          },
          {
            key: "marks",
            label: "Fill Marks",
            children: (
              <Space direction="vertical" size={14} style={{ width: "100%" }}>
                <Row gutter={12}>
                  <Col xs={24} md={8}>
                    <Select
                      placeholder="Select exam"
                      value={selectedExamId}
                      options={exams.map((item) => ({
                        label: `${item.exam_name} (${item.class_name})`,
                        value: item.id
                      }))}
                      onChange={setSelectedExamId}
                      style={{ width: "100%" }}
                    />
                  </Col>
                  <Col xs={24} md={8}>
                    <Select
                      placeholder="Select section"
                      value={selectedSection}
                      options={sectionOptions}
                      onChange={loadStudentsForMarks}
                      style={{ width: "100%" }}
                      disabled={!selectedExam}
                    />
                  </Col>
                  <Col xs={24} md={8}>
                    <Select
                      placeholder="Select subject"
                      value={selectedSubject}
                      options={(selectedExam?.schedule || []).map((item) => ({
                        label: item.subject,
                        value: item.subject
                      }))}
                      onChange={setSelectedSubject}
                      style={{ width: "100%" }}
                      disabled={!selectedExam}
                    />
                  </Col>
                </Row>

                <Table
                  rowKey="id"
                  dataSource={students}
                  columns={marksColumns}
                  pagination={{ pageSize: 8 }}
                  locale={{ emptyText: "Students not loaded" }}
                />

                <Button
                  type="primary"
                  onClick={saveMarks}
                  loading={savingMarks}
                  disabled={!students.length || !selectedSubject}
                >
                  Save All Marks
                </Button>
              </Space>
            )
          }
        ]}
      />

      <Text type="secondary">{loadingMeta ? "Refreshing examination data..." : `Exams: ${exams.length}`}</Text>
    </Card>
  );
}

export default ExaminationPage;
