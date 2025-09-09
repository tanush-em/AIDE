import './globals.css'

export const metadata = {
  title: 'Academic Management System',
  description: 'Faculty Portal for Academic Management',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
