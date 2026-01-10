import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom';
import DashboardPage from './dashboard/DashboardPage';

const App = () => {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/dashboard" element={<DashboardPage />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
