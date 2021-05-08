import {
  Box, FormControl, FormHelperText, MenuItem, Paper, Select,
} from '@material-ui/core';
import React from 'react';

const DELIMITER_TEMPLATES = {
  character: {
    sequence: ',',
  },
  layout: {
    indexes: [0],
  },
};

const DelimiterTypeSelect = ({ delimiter, onDelimiter }) => {
  const onSelect = ({ target: { value } }) =>
    onDelimiter({ ...DELIMITER_TEMPLATES[value], ...delimiter, type: value });
  return (
    <div className="DelimiterTypeSelect">
      <Paper variant="outlined">
        <Box p={1}>
          <FormControl size="small" fullWidth>
            <Select
              value={delimiter.type}
              onChange={onSelect}
              style={{ minHeight: 32 }}
            >
              <MenuItem value="character">Character</MenuItem>
              <MenuItem value="layout">Layout</MenuItem>
            </Select>
            <FormHelperText>Delimiter Type</FormHelperText>
          </FormControl>
        </Box>
      </Paper>
    </div>
  );
};

export default DelimiterTypeSelect;
