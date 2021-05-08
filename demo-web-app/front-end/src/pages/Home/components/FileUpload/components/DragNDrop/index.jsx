import { Box, Paper, Typography } from '@material-ui/core';
import { map } from 'lodash';
import PropTypes from 'prop-types';
import React, { useState } from 'react';
import { useDropzone } from 'react-dropzone';
import theme from '../../../../../../theme';
import Errors from './components/Errors';
import styles from './styles';

const getBorderColor = (isDragActive, isDragAccept, isDragReject) => {
  if (isDragActive) {
    if (isDragAccept) return theme.palette.success.main;
    if (isDragReject) return theme.palette.error.main;
  }
  return theme.palette.primary.main;
};

const DragNDrop = ({ onFile }) => {
  const [errors, setErrors] = useState();
  const onDropRejected = (droppedFiles) => setErrors(droppedFiles[0].errors);
  const onDropAccepted = (droppedFiles) => {
    setErrors(undefined);
    onFile(droppedFiles[0]);
  };
  const classes = styles();
  const {
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject,
  } = useDropzone({
    accept: 'text/*',
    maxFiles: 1,
    minSize: 1,
    multiple: false,
    onDropRejected,
    onDropAccepted,
  });
  return (
    <div className="DragNDrop">
      <Paper
        variant="outlined"
        className={classes.root}
        style={{ borderColor: getBorderColor(isDragActive, isDragAccept, isDragReject) }}
        {...getRootProps()}
      >
        <Box
          display="flex"
          width="33vw"
          height={100}
          p={1}
          justifyContent="center"
          alignItems="center"
        >
          <input {...getInputProps()} />
          <Typography color="textSecondary" variant="body1">Upload a file!</Typography>
        </Box>
      </Paper>
      { errors && <Errors errorMessages={map(errors, 'message')} /> }
    </div>
  );
};

DragNDrop.propTypes = {
  onFile: PropTypes.func.isRequired,
};

export default DragNDrop;
