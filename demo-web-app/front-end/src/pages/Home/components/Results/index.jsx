import { Box, Paper, Typography } from '@material-ui/core';
import { Pagination } from '@material-ui/lab';
import PropTypes from 'prop-types';
import React from 'react';
import { saveAs } from 'file-saver';
import { exportTables } from '../../../../utils/CSVExport';
import Header from './components/Header';
import FileMeta from './components/FileMeta';
import TableContent from './components/TableContent';
import TableMeta from './components/TableMeta';

const Results = ({
  fileName, onReset, runTime, tables,
}) => {
  const [page, setPage] = React.useState(1);
  const [csvBlob, setCSVBlob] = React.useState();
  const [isExporting, setIsExporting] = React.useState(false);
  const onPage = (event, value) => {
    setPage(value);
  };
  const onDownload = () => {
    if (isExporting) return;
    (csvBlob
      ? Promise.resolve(csvBlob)
      : Promise.resolve(() => setIsExporting(true))
        .then(() => exportTables(tables))
        .then((blob) => {
          setIsExporting(false);
          setCSVBlob(blob);
          return blob;
        }))
      .then((blob) => saveAs(blob, `${fileName}.zip`));
  };
  return (
    <div className="Results">
      <Header onReset={onReset} onDownload={onDownload} isExporting={isExporting} />
      <FileMeta
        tables={tables.length}
        fileName={fileName}
        runTime={runTime}
      />
      {
        tables.length ? (
          <>
            <Box display="flex" justifyContent="center" my={2}>
              <Pagination
                count={tables.length}
                page={page}
                onChange={onPage}
                shape="rounded"
                showFirstButton
                showLastButton
              />
            </Box>
            <Box my={1}>
              <TableMeta table={!!tables.length && tables[page - 1]} />
            </Box>
            <Box display="flex" mb={4}>
              <TableContent table={tables[page - 1]} />
            </Box>
          </>
        ) : (
          <Box mt={2}>
            <Paper variant="outlined">
              <Box
                display="flex"
                width={800}
                height={100}
                p={1}
                justifyContent="center"
                alignItems="center"
              >
                <Typography>No tables found!</Typography>
              </Box>
            </Paper>
          </Box>
        )
      }
    </div>
  );
};

Results.propTypes = {
  fileName: PropTypes.string.isRequired,
  onReset: PropTypes.func.isRequired,
  runTime: PropTypes.number.isRequired,
  tables: PropTypes.arrayOf(PropTypes.shape({
    from: PropTypes.number,
    to: PropTypes.number,
    headerRows: PropTypes.number,
    dataRows: PropTypes.number,
    headerConsistency: PropTypes.number,
    dataConsistency: PropTypes.number,
    columns: PropTypes.number,
    parsingInstruction: PropTypes.shape({
      type: PropTypes.string,
      dialect: PropTypes.shape({
        delimiter: PropTypes.string,
        quotation: PropTypes.string,
        escape: PropTypes.string,
      }),
    }),
    content: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.string)),
  })).isRequired,
};

export default Results;
