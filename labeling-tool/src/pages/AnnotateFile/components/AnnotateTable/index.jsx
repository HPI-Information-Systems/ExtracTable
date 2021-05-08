import { Box, Typography } from '@material-ui/core';
import Button from '@material-ui/core/Button';
import MobileStepper from '@material-ui/core/MobileStepper';
import {
  DoneAllOutlined,
  FileCopyOutlined,
  KeyboardArrowLeftOutlined,
  KeyboardArrowRightOutlined,
} from '@material-ui/icons';
import {
  every, isUndefined, map, pick, slice,
} from 'lodash';
import React, { useEffect, useState } from 'react';
import AnnotateLine from './components/AnnotateLine';

const AnnotateTable = ({
  applyAnnotationToLine,
  applyAnnotationToRemaining,
  content,
  highlightLine,
  onAnnotationChange,
  onDone,
  onHighlightLine,
  tableRange,
}) => {
  const [rowIndex, setRowIndex] = useState(0);
  const handleNext = () => setRowIndex((prevRowIndex) => prevRowIndex + 1);
  const handlePrev = () => setRowIndex((prevRowIndex) => prevRowIndex - 1);
  const totalRows = tableRange.to - tableRange.from + 1;
  useEffect(() => {
    if (isUndefined(highlightLine)) return;
    setRowIndex(highlightLine - tableRange.from);
  }, [highlightLine, setRowIndex]);
  useEffect(() => {
    onHighlightLine(rowIndex + tableRange.from);
  }, [onHighlightLine, rowIndex, tableRange]);
  useEffect(() => {
    if (content[tableRange.from + rowIndex].visited) return;
    if (rowIndex > 0) {
      applyAnnotationToLine(
        tableRange.from + rowIndex,
        pick(content[tableRange.from + rowIndex - 1], ['delimiter', 'escape', 'quotation', 'rowType']),
      );
    }
    onAnnotationChange(tableRange.from + rowIndex)('visited')(true);
  }, [rowIndex]);
  const onApplyCurrentToRemaining = () => {
    applyAnnotationToRemaining(
      tableRange.from + rowIndex + 1,
      pick(content[tableRange.from + rowIndex], ['delimiter', 'escape', 'quotation', 'rowType']),
    );
    setRowIndex(totalRows - 1);
  };
  return (
    <div className="AnnotateTable">
      <Box display="flex" flexDirection="column">
        <Box display="flex" mb={2}>
          <Typography variant="h6">
            { `Annotate Line ${tableRange.from + rowIndex + 1} (${rowIndex + 1}/${totalRows})` }
          </Typography>
          <Box flexGrow={1} />
          { every(map(slice(content, tableRange.from, tableRange.to + 1), 'visited')) ? (
            <Button
              variant="contained"
              color="secondary"
              startIcon={<DoneAllOutlined />}
              size="small"
              onClick={onDone}
            >
              Done
            </Button>
          ) : (
            <Button
              variant="contained"
              color="secondary"
              startIcon={<FileCopyOutlined />}
              size="small"
              onClick={onApplyCurrentToRemaining}
            >
              Apply to remaining
            </Button>
          )}
        </Box>
        <AnnotateLine
          line={content[tableRange.from + rowIndex]}
          onUpdate={onAnnotationChange(tableRange.from + rowIndex)}
        />
        <Box mt={2}>
          <MobileStepper
            variant="progress"
            steps={totalRows}
            position="static"
            activeStep={rowIndex}
            nextButton={(
              <Button size="small" onClick={handleNext} disabled={rowIndex === totalRows - 1}>
                Next Row
                {' '}
                <KeyboardArrowRightOutlined />
              </Button>
            )}
            backButton={(
              <Button size="small" onClick={handlePrev} disabled={!rowIndex}>
                <KeyboardArrowLeftOutlined />
                {' '}
                Previous Row
              </Button>
            )}
          />
        </Box>
      </Box>
    </div>
  );
};

export default AnnotateTable;
