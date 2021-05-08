import { Box, CircularProgress, Typography } from '@material-ui/core';
import React from 'react';

const LoadingScreen = ({ message }) => (
  <div className="LoadingScreen">
    <Box height="100vh" display="flex" alignItems="center">
      <Box display="flex" flexDirection="column">
        <Box display="flex" mb={2} justifyContent="center">
          <CircularProgress />
        </Box>
        <Typography>{ message }</Typography>
      </Box>
    </Box>
  </div>
);

export default LoadingScreen;
