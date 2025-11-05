import React, { Suspense, lazy, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useStore } from './store';
import { api } from './api/client';

// Components
import LoadingScreen from './components/common/LoadingScreen';

const Layout = lazy(() => import('./components/Layout'));
const Login = lazy(() => import('./components/Login'));
const Dashboard = lazy(() => import('./components/Dashboard/Dashboard'));
const Fleet = lazy(() => import('./components/Fleet/Fleet'));
const ShipDetail = lazy(() => import('./components/Fleet/ShipDetail'));
const Markets = lazy(() => import('./components/Markets/Markets'));
const Contracts = lazy(() => import('./components/Contracts/Contracts'));
const Systems = lazy(() => import('./components/Systems/Systems'));
const Navigation = lazy(() => import('./components/Navigation/Navigation'));

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
        <Suspense fallback={<LoadingScreen fullScreen message="Preparing command interface..." />}>
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
        </Suspense>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
