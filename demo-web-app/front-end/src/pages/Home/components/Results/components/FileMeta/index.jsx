import { Box, Typography } from '@material-ui/core';
import { round } from 'lodash';
import PropTypes from 'prop-types';
import React from 'react';

const FileMeta = ({ fileName, runTime, tables }) => (
  <div className="Meta">
    <Box
      display="flex"
      flexDirection="column"
      mt={2}
    >
      <Typography variant="h5" color="textPrimary" align="center" gutterBottom>
        {fileName}
      </Typography>
      <Typography variant="body2" color="textSecondary" align="center" gutterBottom>
        {`Found ${tables} ${tables === 1 ? 'table' : 'tables'} in ${round(runTime, 3)} seconds.`}
      </Typography>
    </Box>
  </div>
);

FileMeta.propTypes = {
  fileName: PropTypes.string.isRequired,
  runTime: PropTypes.number.isRequired,
  tables: PropTypes.number.isRequired,
};

export default FileMeta;
