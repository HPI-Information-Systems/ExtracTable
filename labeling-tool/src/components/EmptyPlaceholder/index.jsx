import { Box } from '@material-ui/core';
import Typography from '@material-ui/core/Typography';
import React from 'react';
import theme from '../../theme';

const EmptyPlaceholder = ({ text }) => (
  <Box
    display="flex"
    width="100%"
    height={100}
    justifyContent="center"
    alignItems="center"
    style={{ backgroundColor: theme.palette.background.default }}
  >
    <Typography color="textSecondary" align="center">{ text }</Typography>
  </Box>
);

export default EmptyPlaceholder;
