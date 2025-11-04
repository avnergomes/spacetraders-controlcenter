import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useStore } from './store';
import { api } from './api/client';

// Components
import Layout from './components/Layout';
import Login from './components/Login';
import Dashboard from './components/Dashboard/Dashboard';
import Fleet from './components/Fleet/Fleet';
import ShipDetail from './components/Fleet/ShipDetail';
import Markets from './components/Markets/Markets';
import Contracts from './components/Contracts/Contracts';
import Systems from './components/Systems/Systems';
import Navigation from './components/Navigation/Navigation';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5000,
    },
  },
});

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const isAuthenticated = useStore((state) => state.isAuthenticated);
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
}

function App() {
  const { isAuthenticated, token } = useStore();

  useEffect(() => {
    if (isAuthenticated && token) {
      api.setAuthToken(token);
    }
  }, [isAuthenticated, token]);

  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Layout />
              </ProtectedRoute>
            }
          >
            <Route index element={<Dashboard />} />
            <Route path="fleet" element={<Fleet />} />
            <Route path="fleet/:shipSymbol" element={<ShipDetail />} />
            <Route path="markets" element={<Markets />} />
            <Route path="contracts" element={<Contracts />} />
            <Route path="systems" element={<Systems />} />
            <Route path="navigation" element={<Navigation />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
