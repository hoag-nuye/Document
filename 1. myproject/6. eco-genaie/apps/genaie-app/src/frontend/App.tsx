import React from 'react';
import { Box,  ThemeProvider, createTheme} from '@mui/material';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { CssBaseline } from '@mui/material';
import LoginForm from './features/auth/components/LoginForm';
import ChatWithGeNaie from './features/playground/components/ChatWithGeNaie';
import AddToolForm from './features/playground/components/AddToolForm';
import { useAuth } from './features/auth/hooks/useAuth';

const theme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: '#1976d2',
    },
    secondary: {
      main: '#dc004e',
    },
  },
});

const PrivateRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated } = useAuth();
  // return isAuthenticated ? <>{children}</> : <Navigate to="/login" />;
  return <>{children}</>;
};


const App: React.FC = () => {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
          <Routes>
            <Route path="/login" element={<LoginForm />} />
            <Route
              path="/playground"
              element={
                <PrivateRoute>
                  <Box sx={{ display: 'flex', height: '100%' }}>
                    <Box sx={{ flex: 1, p: 2 }}>
                      <ChatWithGeNaie />
                    </Box>
                    <Box sx={{ width: '400px', p: 2 }}>
                      <AddToolForm />
                    </Box>
                  </Box>
                </PrivateRoute>
              }
            />
            <Route path="/" element={<Navigate to="/login" />} />
          </Routes>
        </Box>
      </Router>
    </ThemeProvider>
  );
};

export default App; 