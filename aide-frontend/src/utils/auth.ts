import usersData from '../data/users.json';
import { User } from '../types';

export function getUserByUsername(username: string): User | undefined {
  return usersData.users.find((user) => user.username === username);
}

export function validateUser(username: string, password: string): User | null {
  const user = getUserByUsername(username);
  if (user && user.password === password) {
    return user;
  }
  return null;
}

export function isStudent(user: User): boolean {
  return user.role === 'student';
}

export function isTeacher(user: User): boolean {
  return user.role === 'teacher';
} 