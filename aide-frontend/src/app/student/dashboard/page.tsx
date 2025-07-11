import ProtectedRoute from '../../../components/auth/ProtectedRoute';

export default function StudentDashboard() {
  return (
    <ProtectedRoute allowedRoles={['student']}>
      <div className="p-8">
        <h1 className="text-3xl font-bold mb-4">Student Dashboard</h1>
        <p>Welcome to your dashboard! (Student view)</p>
      </div>
    </ProtectedRoute>
  );
} 