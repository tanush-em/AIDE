import ProtectedRoute from '../../../components/auth/ProtectedRoute';

export default function TeacherDashboard() {
  return (
    <ProtectedRoute allowedRoles={['teacher']}>
      <div className="p-8">
        <h1 className="text-3xl font-bold mb-4">Teacher Dashboard</h1>
        <p>Welcome to your dashboard! (Teacher view)</p>
      </div>
    </ProtectedRoute>
  );
} 