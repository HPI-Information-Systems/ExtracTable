import { Box, Button, Typography } from '@material-ui/core';
import { ErrorOutlined } from '@material-ui/icons';
import PropTypes from 'prop-types';
import React from 'react';

const Error = ({ description, onReset, title }) => (
  <Box
    display="flex"
    flexDirection="column"
    alignItems="center"
    maxWidth="33vw"
    mt="33vh"
  >
    <ErrorOutlined fontSize="large" color="error" />
    <Box
      display="flex"
      flexDirection="column"
      alignItems="center"
      my={2}
    >
      <Typography variant="h6" color="error">{ title }</Typography>
      <Typography color="textSecondary" gutterBottom>{ description }</Typography>
    </Box>
    <Button size="small" onClick={onReset}>Try another file</Button>
  </Box>
);

Error.propTypes = {
  description: PropTypes.string.isRequired,
  onReset: PropTypes.func.isRequired,
  title: PropTypes.string.isRequired,
};

export default Error;
