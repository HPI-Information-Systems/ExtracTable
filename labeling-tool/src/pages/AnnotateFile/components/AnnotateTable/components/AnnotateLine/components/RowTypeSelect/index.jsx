import {
  Box, FormControl, FormHelperText, MenuItem, Paper, Select,
} from '@material-ui/core';
import React from 'react';

const RowTypeSelect = ({ onRowType, rowType }) => (
  <div className="RowTypeSelect">
    <Paper variant="outlined">
      <Box p={1}>
        <FormControl size="small" fullWidth>
          <Select
            value={rowType}
            onChange={({ target: { value } }) => onRowType(value)}
            style={{ minHeight: 32 }}
            autoWidth
          >
            <MenuItem key="header" value="header">Header</MenuItem>
            <MenuItem key="data" value="data">Data</MenuItem>
            <MenuItem key="other" value="other">Other</MenuItem>
          </Select>
          <FormHelperText>Row type</FormHelperText>
        </FormControl>
      </Box>
    </Paper>
  </div>
);

export default RowTypeSelect;
