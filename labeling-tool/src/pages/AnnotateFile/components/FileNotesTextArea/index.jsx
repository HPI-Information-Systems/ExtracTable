import { TextField } from '@material-ui/core';
import React from 'react';

const FileNotesTextArea = ({ notes, onNotes }) => (
  <div className="FileNotesTextArea">
    <TextField
      value={notes}
      onChange={({ target: { value } }) => onNotes(value)}
      placeholder="Enter your notes here..."
      label="Notes"
      rows={3}
      variant="outlined"
      style={{ backgroundColor: '#FFF' }}
      multiline
      fullWidth
    />
  </div>
);

export default FileNotesTextArea;
