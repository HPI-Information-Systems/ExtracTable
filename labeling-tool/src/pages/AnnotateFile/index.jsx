import {
  Box, Grid, Paper, Typography,
} from '@material-ui/core';
import Button from '@material-ui/core/Button';
import CircularProgress from '@material-ui/core/CircularProgress';
import {
  ClearOutlined, CloudUploadOutlined, RefreshOutlined, SendOutlined, SkipNextOutlined,
} from '@material-ui/icons';
import {
  has, isEqual, map, slice, sortBy,
} from 'lodash';
import moment from 'moment';
import { useSnackbar } from 'notistack';
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router';
import {
  denounceFile, getFileById, replaceFile, reviewDiscussFile, reviewOKFile, skipFile,
} from '../../api/files';
import { classifyFile } from '../../api/repositories';
import Error from '../../components/Error';
import LoadingScreen from '../../components/LoadingScreen';
import TablePreview from '../../components/TablePreview';
import { parseLine } from '../../fileUtil';
import RedirectToNextFile from '../../routing/Label/subpages/RedirectToNextFile';
import theme from '../../theme';
import AnnotateTable from './components/AnnotateTable';
import FileNotesTextArea from './components/FileNotesTextArea';
import SelectTableArea from './components/SelectTableArea';
import TableOverview from './components/TableOverview';
import TimeClock from './components/TimeClock';
import VirtualizedTable from './components/VirtualizedTable';

const FILE_TEMPLATE = {
  tables: [],
  timeClock: [],
  notes: '',
};

const LINE_TEMPLATE = {
  delimiter: {
    type: 'character',
    sequence: [','],
  },
  escape: [],
  quotation: [],
  rowType: 'data',
  visited: false,
};

const ROW_STYLES = {
  header: { backgroundColor: '#cfd8dc' },
  other: { backgroundColor: '#fff9c4' },
};

const prepareFile = (file) => ({
  ...FILE_TEMPLATE,
  ...file,
  content: map(file.content, (line) => ({ ...LINE_TEMPLATE, ...line })),
});

const parserBlob = new Blob([
  // eslint-disable-next-line no-template-curly-in-string
  "addEventListener('message', ({ data: { content, url } }) => {  importScripts(`${url}/workers/modules/fileUtilBundle.js`);  const parsedContent = content.map(({    raw, delimiter, escape, quotation,  }) => Parser.parseLine(raw, {    delimiter, escape, quotation,  }));  postMessage(parsedContent);});"], { type: 'text/javascript' });

// const parser = new Worker('/workers/parser.js');
const parser = new Worker(window.URL.createObjectURL(parserBlob));

const AnnotateFile = () => {
  const { enqueueSnackbar } = useSnackbar();
  const { fileId } = useParams();
  const [file, setFile] = useState();
  const [fetchError, setError] = useState();
  const [table, setTable] = useState();
  const [currentLine, setCurrentLine] = useState();
  const [startTime, setStartTime] = useState();
  const [parsedTable, setParsedTable] = useState({ content: [[]], rowStyles: [] });
  const [isDone, setDone] = useState(false);
  const [isParsing, setParsing] = useState(false);
  document.title = `Annotate ${fileId}`;
  useEffect(() => {
    setDone(false);
    setFile();
    setTable();
    setError();
    setCurrentLine();
    setParsedTable({ content: [[]], rowStyles: [] });
    getFileById(fileId)
      .then((fetchedFile) => {
        document.title = `Annotate ${fetchedFile.name}`;
        if (!has(fetchedFile, 'status')) {
          setError('File needs to be filtered first!');
        } else {
          setFile(prepareFile(fetchedFile));
          setStartTime(moment());
        }
      })
      .catch(setError);
  }, [fileId]);
  useEffect(() => {
    const beforeUnload = (event) => {
      // eslint-disable-next-line no-param-reassign
      event.returnValue = 'Changes will be lost!';
    };
    const handleParserMessage = ({ data: parsedContent }) => {
      setParsedTable({
        content: parsedContent,
        rowStyles: map(file.content, ({ rowType }) => ROW_STYLES[rowType]),
      });
      setParsing(false);
    };
    window.addEventListener('beforeunload', beforeUnload);
    parser.addEventListener('message', handleParserMessage);
    return () => {
      window.removeEventListener('beforeunload', beforeUnload);
      parser.removeEventListener('message', handleParserMessage);
    };
  }, [file]);
  const onAnnotationChange = (lineIndex) => (property) => (nextValue) =>
    setFile((prevFile) => ({
      ...prevFile,
      content: [
        ...slice(prevFile.content, 0, lineIndex),
        {
          ...prevFile.content[lineIndex],
          [property]: nextValue,
        },
        ...slice(prevFile.content, lineIndex + 1),
      ],
    }));
  const applyAnnotationToLine = (lineIndex, template) =>
    setFile((prevFile) => ({
      ...prevFile,
      content: [
        ...slice(prevFile.content, 0, lineIndex),
        {
          ...prevFile.content[lineIndex],
          ...template,
          raw: prevFile.content[lineIndex].raw,
        },
        ...slice(prevFile.content, lineIndex + 1),
      ],
    }));
  const applyAnnotationToRemaining = (lineIndex, template) =>
    setFile((prevFile) => ({
      ...prevFile,
      content: [
        ...slice(prevFile.content, 0, lineIndex),
        ...map(slice(prevFile.content, lineIndex, table.to + 1), (line) => ({
          ...line,
          ...template,
          visited: true,
          raw: line.raw,
        })),
        ...slice(prevFile.content, table.to + 1),
      ],
    }));
  const closeAnnotation = () => {
    setTable();
    setCurrentLine();
  };
  const addTableRange = (newTableRange) =>
    setFile((prevFile) => ({
      ...prevFile,
      tables: sortBy([
        ...prevFile.tables,
        newTableRange,
      ], 'from'),
    }));
  const removeTableRange = (tableIndex) => {
    if (isEqual(table, file.tables[tableIndex])) closeAnnotation();
    setFile((prevFile) => ({
      ...prevFile,
      tables: [
        ...slice(prevFile.tables, 0, tableIndex),
        ...slice(prevFile.tables, tableIndex + 1),
      ],
    }));
  };
  const onConfirmedTableSelection = (range) => {
    addTableRange(range);
    setTable(range);
  };
  const onUpdateParsedTable = () => {
    const content = slice(file.content, table.from, table.to + 1);
    if (content.length > 5000) { // only use web worker if copying the data is worth it
      setParsing(true);
      parser.postMessage({ content, url: window.location.origin });
    } else {
      // runs on main thread (blocks ui) but has no copy
      setParsedTable({
        content: map(content, ({
          raw, delimiter, escape, quotation,
        }) => parseLine(raw, {
          delimiter, escape, quotation,
        })),
        rowStyles: map(content, ({ rowType }) => ROW_STYLES[rowType]),
      });
    }
  };
  const nextFile = () => setDone(true);
  const upload = (finish) => {
    const updatedFile = {
      ...file,
      timeClock: [
        ...file.timeClock,
        { start: startTime, end: moment() },
      ],
      ...(finish && { status: 'annotated' }),
    };
    return replaceFile(fileId, updatedFile)
      .then(() => {
        setStartTime(moment());
        setFile(updatedFile);
      })
      .then(() => enqueueSnackbar('Successfully saved.', { variant: 'success' }))
      .catch(() => enqueueSnackbar('Could not save file', { variant: 'error' }));
  };
  const markAsBadFile = () =>
    denounceFile(fileId)
      .then(() => classifyFile(file.repositoryId, fileId, 'none'))
      .then(nextFile)
      .then(() => enqueueSnackbar('Removed file from selection', { variant: 'info' }))
      .catch(() => enqueueSnackbar('Error removing file from selection. DB might be inconsistent!', { variant: 'error' }));
  const markAsSkipped = () =>
    skipFile(fileId)
      .then(nextFile)
      .then(() => enqueueSnackbar('Skipped file', { variant: 'info' }))
      .catch(() => enqueueSnackbar('Error skipping file. DB might be inconsistent!', { variant: 'error' }));
  const onNotes = (notes) =>
    setFile((prevFile) => ({
      ...prevFile,
      notes,
    }));
  const onReview = (isOk) =>
    (isOk ? reviewOKFile(fileId) : reviewDiscussFile(fileId))
      .then(nextFile);
  return (
    <div className="AnnotateFile">
      {
        isDone && (
          <RedirectToNextFile />
        )
      }
      {
        file && (
          <Box display="flex" flexDirection="column" width={1200} mb={4}>
            <Box my={2}><Typography variant="h4" align="center" gutterBottom>{file.name}</Typography></Box>
            <Grid
              container
              direction="row"
              justify="center"
              alignItems="flex-start"
              spacing={2}
            >
              <Grid item xs={9}>
                <Grid
                  container
                  direction="column"
                  justify="flex-start"
                  alignItems="stretch"
                  spacing={2}
                >
                  <Grid item xs>
                    <Paper variant="outlined" style={{ borderColor: theme.palette.primary.main }}>
                      <Box p={2}>
                        <SelectTableArea
                          file={file}
                          onConfirmedSelection={onConfirmedTableSelection}
                          tableSelections={file.tables}
                          table={table}
                          highlightLine={currentLine}
                          onHighlightLine={setCurrentLine}
                          onTable={setTable}
                        />
                      </Box>
                    </Paper>
                  </Grid>
                  {
                    table && (
                      <>
                        <Grid item xs>
                          <Paper variant="outlined" style={{ borderColor: theme.palette.primary.main }}>
                            <Box p={2}>
                              <AnnotateTable
                                content={file.content}
                                tableRange={table}
                                onAnnotationChange={onAnnotationChange}
                                highlightLine={currentLine}
                                onHighlightLine={setCurrentLine}
                                onDone={closeAnnotation}
                                applyAnnotationToLine={applyAnnotationToLine}
                                applyAnnotationToRemaining={applyAnnotationToRemaining}
                              />
                            </Box>
                          </Paper>
                        </Grid>
                        <Grid item xs>
                          <Box display="flex" justifyContent="flex-end">
                            <Button
                              variant="outlined"
                              size="small"
                              onClick={onUpdateParsedTable}
                              startIcon={isParsing
                                ? <CircularProgress size={16} /> : <RefreshOutlined />}
                              disabled={isParsing || (table.to - table.from >= 5000)}
                            >
                              { isParsing ? 'Refreshing...' : 'Refresh' }
                            </Button>
                          </Box>
                        </Grid>
                        <Grid item xs>
                          {
                            parsedTable.content.length > 1000
                              ? (
                                <VirtualizedTable
                                  data={parsedTable.content}
                                  rowStyles={parsedTable.rowStyles}
                                />
                              )
                              : (
                                <TablePreview
                                  rows={parsedTable.content}
                                  rowStyles={parsedTable.rowStyles}
                                />
                              )
                          }
                        </Grid>
                      </>
                    )
                  }
                </Grid>
              </Grid>
              <Grid item xs={3}>
                <Box display="flex" flexDirection="column">
                  <TimeClock startTime={startTime} timeClock={file.timeClock} />
                  <Box my={3}>
                    <FileNotesTextArea notes={file.notes} onNotes={onNotes} />
                  </Box>
                  <TableOverview
                    tables={file.tables}
                    onTable={setTable}
                    onRemoveTable={removeTableRange}
                  />
                  <Box display="flex" mt={3}>
                    <Button
                      variant="contained"
                      color="primary"
                      size="small"
                      onClick={() => upload(false)}
                      startIcon={<CloudUploadOutlined />}
                      fullWidth
                    >
                      Save
                    </Button>
                    <Box mr={1} />
                    <Button
                      variant="contained"
                      color="primary"
                      size="small"
                      onClick={() => upload(true).then(nextFile)}
                      startIcon={<SendOutlined />}
                      fullWidth
                    >
                      Finish
                    </Button>
                  </Box>
                  <Box display="flex" mt={1}>
                    <Button
                      variant="outlined"
                      color="primary"
                      size="small"
                      onClick={markAsSkipped}
                      startIcon={<SkipNextOutlined />}
                      fullWidth
                    >
                      Skip
                    </Button>
                    <Box mr={1} />
                    <Button
                      variant="outlined"
                      color="secondary"
                      size="small"
                      onClick={markAsBadFile}
                      startIcon={<ClearOutlined />}
                      style={{
                        color: '#FFF',
                        backgroundColor: theme.palette.error.main,
                      }}
                      fullWidth
                    >
                      Remove
                    </Button>
                  </Box>
                </Box>
                {
                  file.status === 'annotated' && (
                    <Box display="flex" mt={3}>
                      <Button
                        variant="contained"
                        style={{
                          color: '#FFF',
                          backgroundColor: theme.palette.success.main,
                        }}
                        size="small"
                        onClick={() => onReview(true)}
                        fullWidth
                      >
                        OK
                      </Button>
                      <Box mr={1} />
                      <Button
                        variant="contained"
                        style={{
                          color: '#FFF',
                          backgroundColor: theme.palette.warning.main,
                        }}
                        size="small"
                        onClick={() => onReview(false)}
                        fullWidth
                      >
                        Discuss
                      </Button>
                    </Box>
                  )
                }
              </Grid>
            </Grid>
          </Box>
        )
      }
      {
        !file && !fetchError && !isDone && (
          <LoadingScreen message="Fetching file..." />
        )
      }
      {
        fetchError && (
          <Error message="Cannot annotate file!" description={fetchError.message || fetchError} />
        )
      }
    </div>
  );
};

export default AnnotateFile;
