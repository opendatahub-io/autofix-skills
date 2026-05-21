import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AnalyticsDashboard } from './pages/AnalyticsDashboard';
import { MonitoringDashboard } from './pages/MonitoringDashboard';
import { UserManagement } from './pages/UserManagement';
import { Sidebar } from './components/Sidebar';

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/analytics" element={<AnalyticsDashboard />} />
            <Route path="/monitoring" element={<MonitoringDashboard />} />
            <Route path="/users" element={<UserManagement />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;
