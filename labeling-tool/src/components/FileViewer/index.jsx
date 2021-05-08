import { Box, IconButton, Typography } from '@material-ui/core';
import Paper from '@material-ui/core/Paper';
import { ZoomInOutlined, ZoomOutOutlined } from '@material-ui/icons';
import React, { useState } from 'react';
import { getRawContent } from '../../fileUtil';

const FileViewer = ({ file }) => {
  const [fontSize, setFontSize] = useState(14);
  return (
    <div className="FileViewer">
      <Box
        display="flex"
        flexDirection="column"
        width="calc(100vw * 2/3)"
      >
        <Typography variant="h6" align="center" gutterBottom>
          { file.name }
        </Typography>
        <Box display="flex" justifyContent="flex-end">
          <IconButton
            color="inherit"
            onClick={() => setFontSize((prevFontSize) => prevFontSize - 1)}
            size="small"
            disabled={!fontSize}
          >
            <ZoomOutOutlined />
          </IconButton>
          <IconButton
            color="inherit"
            onClick={() => setFontSize((prevFontSize) => prevFontSize + 1)}
            size="small"
            disabled={!fontSize}
          >
            <ZoomInOutlined />
          </IconButton>
        </Box>
        <Paper variant="outlined">
          <Box p={2} style={{ maxHeight: 'calc(100vh * 2/3', overflow: 'scroll' }}>
            <Typography style={{ fontSize, whiteSpace: 'pre', fontFamily: 'Courier New' }}>
              { getRawContent(file) }
            </Typography>
          </Box>
        </Paper>
      </Box>
    </div>
  );
};

export default FileViewer;
