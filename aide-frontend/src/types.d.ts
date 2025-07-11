export type User = {
  id: number;
  username: string;
  password: string;
  role: 'student' | 'teacher';
  name: string;
  studentId?: string;
  employeeId?: string;
  department: string;
};

export type Notice = {
  id: number;
  title: string;
  content: string;
  category: string;
  priority: string;
  postedBy: string;
  postedAt: string;
  department: string;
};

export type Attendance = {
  studentId: string;
  subject: string;
  date: string;
  status: 'present' | 'absent';
  markedBy: string;
};

export type LeaveApplication = {
  id: number;
  studentId: string;
  leaveType: string;
  startDate: string;
  endDate: string;
  reason: string;
  status: string;
  appliedAt: string;
};

export type Timetable = {
  id: number;
  department: string;
  week: string;
  schedule: Array<{
    day: string;
    subject: string;
    time: string;
    room: string;
    faculty: string;
  }>;
}; 