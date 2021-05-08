import {
  Box, Paper, TextField, Typography,
} from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import * as expandtabs from 'expandtabs';
import { sortBy, sortedUniq, without } from 'lodash';
import React, { useEffect, useRef } from 'react';
import Chips from '../../../../../../components/Chips';
import TablePreview from '../../../../../../components/TablePreview';
import { parseLine } from '../../../../../../fileUtil';
import DelimiterTypeSelect from './components/DelimiterTypeSelect';
import RowTypeSelect from './components/RowTypeSelect';
import SimpleAnnotationInput from './components/SimpleAnnotationInput';

const AnnotateLine = ({
  line: {
    delimiter, escape, quotation, raw, rowType,
  }, onUpdate,
}) => {
  const inputRef = useRef();
  useEffect(() => {
    if (delimiter.type === 'layout') {
      inputRef.current.focus();
      inputRef.current.setSelectionRange(0, 0);
    }
  }, [delimiter.type, inputRef]);
  const removeIndex = (index) => onUpdate('delimiter')({
    ...delimiter,
    indexes: without(delimiter.indexes, index),
  });
  const addIndex = (index) => {
    if (delimiter.type === 'layout') { onUpdate('delimiter')({ ...delimiter, indexes: sortedUniq(sortBy([...delimiter.indexes, index])) }); }
  };
  const onInputClick = () => {
    const { selectionStart, selectionEnd } = inputRef.current;
    if (selectionStart !== selectionEnd) return;
    addIndex(selectionStart);
  };
  const onKeyDown = (event) => {
    if (event.which === 32) {
      onInputClick();
      event.preventDefault();
    }
  };
  return (
    <div className="AnnotateLine">
      <TextField
        value={delimiter.type === 'layout' ? expandtabs(raw) : raw}
        onKeyDown={onKeyDown}
        inputRef={inputRef}
        onClick={onInputClick}
        variant="filled"
        fullWidth
        inputProps={{
          style: {
            whiteSpace: 'nowrap',
            overflowX: 'scroll',
            padding: '6px 0 7px',
          },
        }}
      />
      <Box mt={2} mb={1}>
        <Grid
          container
          direction="row"
          justify="space-between"
          alignItems="stretch"
          spacing={1}
        >
          <Grid item xs><DelimiterTypeSelect delimiter={delimiter} onDelimiter={onUpdate('delimiter')} /></Grid>
          {
            delimiter.type === 'character' && (
              <Grid item xs>
                <SimpleAnnotationInput
                  annotations={delimiter.sequence}
                  label="Delimiter"
                  onAnnotation={(sequence) => {
                    onUpdate('delimiter')({ ...delimiter, sequence });
                  }}
                />
              </Grid>
            )
          }
          {
            delimiter.type === 'layout' && (
              <Grid item xs>
                <Paper variant="outlined">
                  <Box p={1}>
                    <Chips
                      elements={delimiter.indexes}
                      nonDeletableElements={[0]}
                      onDelete={removeIndex}
                    />
                  </Box>
                </Paper>
              </Grid>
            )
          }
          <Grid item xs><SimpleAnnotationInput annotations={quotation} label="Quote" onAnnotation={onUpdate('quotation')} /></Grid>
          <Grid item xs><SimpleAnnotationInput annotations={escape} label="Escape" onAnnotation={onUpdate('escape')} /></Grid>
          <Grid item xs><RowTypeSelect rowType={rowType} onRowType={onUpdate('rowType')} /></Grid>
        </Grid>
      </Box>
      <Typography color="textSecondary">Preview</Typography>
      <TablePreview rows={[parseLine(raw, {
        delimiter, escape, quotation,
      })]}
      />
    </div>
  );
};

export default AnnotateLine;
