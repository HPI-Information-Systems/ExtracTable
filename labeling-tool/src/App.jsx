import { Box, IconButton } from '@material-ui/core';
import { CloseOutlined } from '@material-ui/icons';
import { ThemeProvider } from '@material-ui/styles';
import { SnackbarProvider } from 'notistack';
import React, { createRef } from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import AppNavigation from './components/AppNavigation';
import Home from './pages/Home';
import ViewFile from './pages/ViewFile';
import Filter from './routing/Filter';
import Label from './routing/Label';
import theme from './theme';

const App = () => {
  const notistackRef = createRef();
  const onClickDismiss = (key) => () => {
    notistackRef.current.closeSnackbar(key);
  };
  return (
    <ThemeProvider theme={theme}>
      <SnackbarProvider
        ref={notistackRef}
        action={(key) => (
          <IconButton color="inherit" onClick={onClickDismiss(key)} size="small">
            <CloseOutlined />
          </IconButton>
        )}
        hideIconVariant
      >
        <Box
          display="flex"
          flexDirection="column"
          minHeight="100vh"
          alignItems="center"
          style={{ backgroundColor: theme.palette.background.default, overflow: 'auto' }}
        >
          <Router>
            <Box mb={4}>
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/filter/*" element={<Filter />} />
                <Route path="/label/*" element={<Label />} />
                <Route path="/view/:fileId" element={<ViewFile />} />
              </Routes>
            </Box>
            <AppNavigation />
          </Router>
        </Box>
      </SnackbarProvider>
    </ThemeProvider>
  );
};

export default App;
