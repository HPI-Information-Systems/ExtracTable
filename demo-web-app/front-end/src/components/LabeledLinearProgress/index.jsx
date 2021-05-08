import { Box, LinearProgress, Typography } from '@material-ui/core';
import PropTypes from 'prop-types';
import React from 'react';

const LabeledLinearProgress = ({ value }) => (
  <Box
    display="flex"
    alignItems="center"
    px={1}
    width="100%"
  >
    <Box
      flexGrow={1}
      mr={1}
    >
      <LinearProgress variant="determinate" value={value} />
    </Box>
    <Box minWidth={35}>
      <Typography variant="body2" color="textSecondary" align="right">
        {`${Math.round(value)}%`}
      </Typography>
    </Box>
  </Box>
);

LabeledLinearProgress.propTypes = {
  value: PropTypes.number.isRequired,
};

export default LabeledLinearProgress;
