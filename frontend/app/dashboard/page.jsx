import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

export default function DashboardPage() {
  const [user, setUser] = useState(null);
  const [attendance, setAttendance] = useState([]);
  const [timetable, setTimetable] = useState([]);
  const [notices, setNotices] = useState([]);
  const [leaves, setLeaves] = useState([]);
  const [leaveForm, setLeaveForm] = useState({ from: "", to: "", reason: "" });
  const [leaveError, setLeaveError] = useState("");
  const [leaveSuccess, setLeaveSuccess] = useState("");
  const router = useRouter();

  useEffect(() => {
    // Fetch user session info (simulate by checking attendance fetch)
    fetch("http://localhost:4000/attendance", { credentials: "include" })
      .then((res) => {
        if (res.status === 403 || res.status === 401) {
          router.push("/login");
        }
        return res.json();
      })
      .then((data) => setAttendance(data));
    fetch("http://localhost:4000/timetable", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setTimetable(data));
    fetch("http://localhost:4000/notices", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setNotices(data));
    fetch("http://localhost:4000/leaves", { credentials: "include" })
      .then((res) => res.json())
      .then((data) => setLeaves(data));
  }, [router]);

  const handleLeaveSubmit = async (e) => {
    e.preventDefault();
    setLeaveError("");
    setLeaveSuccess("");
    const res = await fetch("http://localhost:4000/leaves", {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(leaveForm),
    });
    if (res.ok) {
      setLeaveSuccess("Leave applied successfully!");
      setLeaveForm({ from: "", to: "", reason: "" });
      // Refresh leaves
      fetch("http://localhost:4000/leaves", { credentials: "include" })
        .then((res) => res.json())
        .then((data) => setLeaves(data));
    } else {
      const data = await res.json();
      setLeaveError(data.message || "Failed to apply for leave");
    }
  };

  return (
    <div className="container mx-auto py-8">
      <h1 className="text-3xl font-bold mb-6">Student Dashboard</h1>
      {/* Attendance Section */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Attendance</h2>
        <div className="bg-card p-4 rounded-lg shadow">
          {attendance.length === 0 ? (
            <p>No attendance records found.</p>
          ) : (
            <ul>
              {attendance.map((a, i) => (
                <li key={i} className="mb-1">
                  {a.date}: <span className={a.status === "Present" ? "text-green-600" : "text-red-600"}>{a.status}</span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
      {/* Timetable Section */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Timetable</h2>
        <div className="bg-card p-4 rounded-lg shadow">
          {timetable.length === 0 ? (
            <p>No timetable found.</p>
          ) : (
            <ul>
              {timetable.map((t, i) => (
                <li key={i} className="mb-1">
                  {t.day} - {t.subject} ({t.time})
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
      {/* Notices Section */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Notices</h2>
        <div className="bg-card p-4 rounded-lg shadow">
          {notices.length === 0 ? (
            <p>No notices found.</p>
          ) : (
            <ul>
              {notices.map((n) => (
                <li key={n.id} className="mb-2">
                  <strong>{n.title}</strong> <span className="text-xs text-muted-foreground">({n.date})</span>
                  <div>{n.content}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
      {/* Leave Application Section */}
      <section className="mb-8">
        <h2 className="text-xl font-semibold mb-2">Apply for Leave</h2>
        <div className="bg-card p-4 rounded-lg shadow">
          <form onSubmit={handleLeaveSubmit} className="flex flex-col gap-2">
            <input
              type="date"
              value={leaveForm.from}
              onChange={(e) => setLeaveForm({ ...leaveForm, from: e.target.value })}
              className="input input-bordered"
              required
            />
            <input
              type="date"
              value={leaveForm.to}
              onChange={(e) => setLeaveForm({ ...leaveForm, to: e.target.value })}
              className="input input-bordered"
              required
            />
            <textarea
              placeholder="Reason"
              value={leaveForm.reason}
              onChange={(e) => setLeaveForm({ ...leaveForm, reason: e.target.value })}
              className="input input-bordered"
              required
            />
            {leaveError && <div className="text-red-500 text-sm">{leaveError}</div>}
            {leaveSuccess && <div className="text-green-600 text-sm">{leaveSuccess}</div>}
            <button
              type="submit"
              className="bg-primary text-primary-foreground py-2 rounded-md font-semibold hover:bg-primary/90 transition"
            >
              Apply
            </button>
          </form>
          <div className="mt-4">
            <h3 className="font-semibold mb-2">Your Leave Applications</h3>
            {leaves.length === 0 ? (
              <p>No leave applications found.</p>
            ) : (
              <ul>
                {leaves.map((l) => (
                  <li key={l.id} className="mb-1">
                    {l.from} to {l.to}: {l.reason} (<span className="text-blue-600">{l.status}</span>)
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      </section>
    </div>
  );
} 