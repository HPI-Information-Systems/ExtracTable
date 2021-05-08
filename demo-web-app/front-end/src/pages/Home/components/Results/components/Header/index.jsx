import { Box, Button } from '@material-ui/core';
import { ArrowBackOutlined, GetAppOutlined } from '@material-ui/icons';
import PropTypes from 'prop-types';
import React from 'react';

const Header = ({ isExporting, onDownload, onReset }) => (
  <div className="Header">
    <Box display="flex" mt={2} alignItems="center">
      <Button
        size="small"
        startIcon={<ArrowBackOutlined fontSize="small" />}
        onClick={onReset}
      >
        Try another file
      </Button>
      <Box flexGrow={1} />
      <Button
        color="primary"
        startIcon={<GetAppOutlined />}
        size="small"
        onClick={onDownload}
        disabled={isExporting}
      >
        Download
      </Button>
    </Box>
  </div>
);

Header.propTypes = {
  isExporting: PropTypes.bool.isRequired,
  onDownload: PropTypes.func.isRequired,
  onReset: PropTypes.func.isRequired,
};

export default Header;
