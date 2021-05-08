import { Box, IconButton } from '@material-ui/core';
import { ThemeProvider } from '@material-ui/core/styles';
import { CloseOutlined } from '@material-ui/icons';
import { SnackbarProvider } from 'notistack';
import React, { createRef } from 'react';
import {
  BrowserRouter as Router,
  Route,
  Routes,
} from 'react-router-dom';
import Header from './components/Header';
import Home from './pages/Home';
import theme from './theme';

function App() {
  const notistackRef = createRef();
  const onClickDismiss = (key) => () => {
    notistackRef.current.closeSnackbar(key);
  };
  return (
    <div className="App">
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
            <Header />
            <Router>
              <Box>
                <Routes>
                  <Route path="/" element={<Home />} />
                </Routes>
              </Box>
            </Router>
          </Box>
        </SnackbarProvider>
      </ThemeProvider>
    </div>
  );
}

export default App;
