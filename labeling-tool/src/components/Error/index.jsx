import { Typography, Box } from '@material-ui/core';
import { ErrorOutlined } from '@material-ui/icons';
import React from 'react';

const Error = ({ message, description }) => (
  <div className="Error">
    <Box height="100vh" display="flex" alignItems="center">
      <Box display="flex" flexDirection="column" alignItems="center" maxWidth="33vw">
        <Box mb={2}><ErrorOutlined fontSize="large" color="error" /></Box>
        <Typography variant="h6" color="error">{ message }</Typography>
        {
        description && (
          <Typography color="textSecondary">{ description }</Typography>
        )
      }
      </Box>
    </Box>
  </div>
);

export default Error;
