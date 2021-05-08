import {
  Box, Button, Paper, TextField, Typography,
} from '@material-ui/core';
import 'codemirror-theme-github/theme/github.css';
import 'codemirror/lib/codemirror.css';
import {
  find,
  forEach,
  isEmpty,
  isEqual, isUndefined,
  map,
  mapValues,
  max,
  min,
  pick,
  some,
  toInteger,
  toString,
  values,
} from 'lodash';
import React, { useEffect, useRef, useState } from 'react';
import { UnControlled as CodeMirror } from 'react-codemirror2';
import { getRawContent } from '../../../../fileUtil';

const getRange = (selection, file) => { // convert selection to range object
  const { from, to } = mapValues(selection, toInteger);
  const isAnchorTop = from <= to;
  const anchor = { line: from, ch: isAnchorTop ? 0 : file.content[from].raw.length - 1 };
  const head = { line: to, ch: isAnchorTop ? file.content[to].raw.length - 1 : 0 };
  return { anchor, head };
};

const rangeDiff = (editor, anchor, head) => { // return true if different
  const selections = editor.listSelections();
  if (isEmpty(selections)) return true;
  const selected = pick(selections[0], ['anchor.line', 'anchor.ch', 'head.line', 'head.ch']);
  return !isEqual(selected, { anchor, head });
};

const isValidSelection = (selection) =>
  !isEmpty(selection.from.trim()) && !isEmpty(selection.to.trim());

const isSelectionOverlapping = (selection, tableSelections) => {
  const from = min(values(mapValues(selection, toInteger)));
  const to = max(values(mapValues(selection, toInteger)));
  // table selection from is always leq to (sorted in onExtract)
  return some(tableSelections, (tableSelection) =>
    (from <= tableSelection.from && to >= tableSelection.from)
    || (from <= tableSelection.to && to >= tableSelection.to));
};

const SelectTableArea = ({
  file, highlightLine, onConfirmedSelection, onHighlightLine, onTable, table, tableSelections,
}) => {
  const tableSelectionsRef = useRef(); // workaround as the chosen codemirror seems to be faulty
  tableSelectionsRef.current = tableSelections;
  const [selection, setSelection] = useState({ from: '0', to: '0' });
  const [editor, setEditor] = useState();
  const rawContent = getRawContent(file);
  const lineCount = file.content.length;
  useEffect(() => {
    if (!editor || !file || !isValidSelection(selection) || !file.content.length) return;
    const { anchor, head } = getRange(selection, file);
    if (rangeDiff(editor, anchor, head)) editor.setSelection(anchor, head, { scroll: false });
  }, [editor, file, selection]);
  useEffect(() => {
    if (!editor || !file) return () => {};
    const ranges = map(tableSelections, (tableSelection) => getRange(tableSelection, file));
    const markers = map(ranges, ({ anchor, head }) => editor.markText(anchor, head, { css: 'background-color: #9e9e9e; color: #FFF' }));
    return () => {
      forEach(markers, (marker) => marker.clear());
    };
  }, [editor, file, tableSelections]);
  useEffect(() => {
    if (!editor || !file || !table) return () => {};
    const { anchor, head } = getRange(table, file);
    const marker = editor.markText(anchor, head, { css: 'background-color: #b3e5fc; color: #FFF' });
    return () => marker.clear();
  }, [editor, file, table]);
  useEffect(() => {
    if (!editor || isUndefined(highlightLine)) return () => {};
    const { anchor, head } = getRange({ from: highlightLine, to: highlightLine }, file);
    const marker = editor.markText(anchor, head, { css: 'background-color: #2196f3; color: #FFF' });
    return () => marker.clear();
  }, [editor, file, highlightLine]);
  const onSelection = (_, { ranges }) => {
    const { anchor, head } = ranges[0];
    if (anchor.line === head.line && anchor.ch === head.ch) {
      const selectedTable = find(tableSelectionsRef.current, ({ from, to }) =>
        anchor.line >= from && anchor.line <= to);
      if (selectedTable) {
        onTable(selectedTable);
        onHighlightLine(anchor.line);
      }
    } else {
      setSelection({
        from: toString(anchor.line),
        to: toString(head.line),
      });
    }
  };
  const onInput = (property) => ({ target: { value } }) =>
    setSelection((prevSelection) => ({
      ...prevSelection,
      [property]: isEmpty(value.trim())
        ? value
        : toString(Math.max(0, Math.min(toInteger(value) - 1, lineCount - 1))),
    }));
  const onExtract = () => {
    if (!isValidSelection(selection) || isSelectionOverlapping(selection, tableSelections)) return;
    const confirmedSelection = {
      from: min(values(mapValues(selection, toInteger))),
      to: max(values(mapValues(selection, toInteger))),
    };
    onConfirmedSelection(confirmedSelection);
  };
  return (
    <div className="SelectTableArea">
      <Box display="flex" flexDirection="column">
        <Typography variant="h6" gutterBottom>
          Select table area
        </Typography>
        <Box display="flex">
          <Box flex={1} mr={1} style={{ overflow: 'hidden' }}>
            <Paper variant="outlined">
              <CodeMirror
                value={rawContent}
                options={{
                  configureMouse: () => ({ addNew: false }),
                  lineNumbers: true,
                  readOnly: true,
                  theme: 'github',
                  tabSize: 8
                }}
                onSelection={onSelection}
                editorDidMount={setEditor}
              />
            </Paper>
          </Box>
          <Box display="flex" flexDirection="column">
            <Box display="flex">
              <Box mr={1}>
                <TextField
                  value={toString(toInteger(selection.from) + 1)}
                  onChange={onInput('from')}
                  label="from"
                  type="number"
                  size="small"
                  variant="outlined"
                  inputProps={{
                    min: 0,
                    max: lineCount,
                    step: '1',
                  }}
                  InputLabelProps={{
                    shrink: true,
                  }}
                  required
                />
              </Box>
              <TextField
                value={toString(toInteger(selection.to) + 1)}
                onChange={onInput('to')}
                label="to"
                type="number"
                size="small"
                variant="outlined"
                inputProps={{
                  min: '0',
                  max: lineCount,
                  step: '1',
                }}
                InputLabelProps={{
                  shrink: true,
                }}
                required
              />
            </Box>
            <Box my={1}>
              <Button
                variant="contained"
                onClick={onExtract}
                disabled={
                !isValidSelection(selection) || isSelectionOverlapping(selection, tableSelections)
              }
                fullWidth
              >
                Extract
              </Button>
            </Box>
            <Button
              variant="outlined"
              onClick={() => setSelection({ from: toString(0), to: toString(lineCount - 1) })}
              fullWidth
            >
              Select All
            </Button>
          </Box>
        </Box>
      </Box>
    </div>
  );
};
export default SelectTableArea;
