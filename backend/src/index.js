const express = require('express');
const session = require('express-session');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 4000;

app.use(cors({
  origin: 'http://localhost:3000',
  credentials: true
}));
app.use(express.json());
app.use(session({
  secret: 'supersecret',
  resave: false,
  saveUninitialized: false,
  cookie: { secure: false }
}));

const DATA_DIR = path.join(__dirname, '../data');

function readJson(file) {
  return JSON.parse(fs.readFileSync(path.join(DATA_DIR, file), 'utf-8'));
}
function writeJson(file, data) {
  fs.writeFileSync(path.join(DATA_DIR, file), JSON.stringify(data, null, 2));
}

// Login endpoint
app.post('/login', (req, res) => {
  const { username, password } = req.body;
  const users = readJson('users.json');
  const user = users.find(u => u.username === username && u.password === password);
  if (user) {
    req.session.user = { username: user.username, role: user.role, id: user.id, name: user.name };
    res.json({ success: true, user: req.session.user });
  } else {
    res.status(401).json({ success: false, message: 'Invalid credentials' });
  }
});

// Auth middleware
function requireStudent(req, res, next) {
  if (req.session.user && req.session.user.role === 'student') {
    next();
  } else {
    res.status(403).json({ message: 'Forbidden' });
  }
}

// Attendance endpoint
app.get('/attendance', requireStudent, (req, res) => {
  const attendance = readJson('attendance.json');
  const studentAttendance = attendance.find(a => a.studentId === req.session.user.id);
  res.json(studentAttendance ? studentAttendance.attendance : []);
});

// Timetable endpoint
app.get('/timetable', requireStudent, (req, res) => {
  const timetable = readJson('timetable.json');
  const studentTimetable = timetable.find(t => t.studentId === req.session.user.id);
  res.json(studentTimetable ? studentTimetable.timetable : []);
});

// Notices endpoint
app.get('/notices', requireStudent, (req, res) => {
  const notices = readJson('notices.json');
  res.json(notices);
});

// Get leaves
app.get('/leaves', requireStudent, (req, res) => {
  const leaves = readJson('leaves.json');
  const studentLeaves = leaves.filter(l => l.studentId === req.session.user.id);
  res.json(studentLeaves);
});

// Apply for leave
app.post('/leaves', requireStudent, (req, res) => {
  const { from, to, reason } = req.body;
  if (!from || !to || !reason) {
    return res.status(400).json({ message: 'Missing fields' });
  }
  const leaves = readJson('leaves.json');
  const newLeave = {
    id: 'L' + (leaves.length + 1).toString().padStart(3, '0'),
    studentId: req.session.user.id,
    from,
    to,
    reason,
    status: 'Pending',
    appliedAt: new Date().toISOString()
  };
  leaves.push(newLeave);
  writeJson('leaves.json', leaves);
  res.json(newLeave);
});

// Logout endpoint
app.post('/logout', (req, res) => {
  req.session.destroy(() => {
    res.json({ success: true });
  });
});

app.listen(PORT, () => {
  console.log(`Backend server running on http://localhost:${PORT}`);
});
