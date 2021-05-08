import {
  Box, FormControl, FormHelperText, Paper, TextField,
} from '@material-ui/core';
import {
  includes,
  isEmpty, some, startsWith, uniq, without,
} from 'lodash';
import React, { useState } from 'react';
import Chips from '../../../../../../../../components/Chips';

const SimpleAnnotationInput = ({ annotations, label, onAnnotation }) => {
  const [input, setInput] = useState('');
  const addAnnotation = (annotation) => onAnnotation(uniq([...annotations, annotation]));
  const removeAnnotation = (annotation) => onAnnotation(without(annotations, annotation));
  const onKeyDown = ({ which }) => {
    if (which === 13) {
      if (isEmpty(input)) return;
      if (includes(annotations, input)) {
        setInput('');
        return;
      }
      if (some(annotations,
        (annotation) => startsWith(annotation, input) || startsWith(input, annotation))) return;
      addAnnotation(input);
      setInput('');
    }
  };
  return (
    <div className="SimpleAnnotationInput">
      <Paper variant="outlined">
        <Box p={1}>
          <FormControl size="small" fullWidth>
            <TextField
              value={input}
              onChange={({ target: { value } }) => setInput(value)}
              onKeyDown={onKeyDown}
            />
            <FormHelperText>{ label }</FormHelperText>
          </FormControl>
          <Box display="flex">
            <Chips elements={annotations} onDelete={removeAnnotation} />
          </Box>
        </Box>
      </Paper>
    </div>
  );
};

export default SimpleAnnotationInput;
