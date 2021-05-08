import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TablePagination,
  TableRow,
} from '@material-ui/core';
import { map, slice } from 'lodash';
import PropTypes from 'prop-types';
import React, { useEffect } from 'react';
import styles from './styles';

const TableContent = ({ table }) => {
  const [page, setPage] = React.useState(0);
  const [rowsPerPage, setRowsPerPage] = React.useState(10);
  useEffect(() => {
    setPage(0);
  }, [table]);
  const onPage = (event, newPage) => {
    setPage(newPage);
  };
  const onRowsPerPage = (event) => {
    setRowsPerPage(parseInt(event.target.value, 10));
    setPage(0);
  };
  const classes = styles();
  const header = slice(table.content, 0, table.headerRows);
  const data = slice(table.content, table.headerRows);
  return (
    <Box display="flex" flexDirection="column" width={800}>
      <TableContainer component={Paper} variant="outlined">
        <Table size="small" classes={classes.table}>
          <TableHead>
            {
              map(header, (row, iRow) => (
                <TableRow key={iRow}>
                  {
                  map(row, (cell, iCell) => (
                    <TableCell key={iCell}>{cell}</TableCell>
                  ))
                }
                </TableRow>
              ))
            }
          </TableHead>
          <TableBody>
            {
              map(slice(data, page * rowsPerPage, (page + 1) * rowsPerPage), (row, iRow) => (
                <TableRow key={iRow}>
                  {
                  map(row, (cell, iCell) => (
                    <TableCell key={iCell}>{cell}</TableCell>
                  ))
                }
                </TableRow>
              ))
            }
          </TableBody>
        </Table>
      </TableContainer>
      <Box display="flex" justifyContent="flex-end">
        <TablePagination
          count={table.dataRows}
          page={page}
          onChangePage={onPage}
          rowsPerPage={rowsPerPage}
          onChangeRowsPerPage={onRowsPerPage}
        />
      </Box>
    </Box>
  );
};

TableContent.propTypes = {
  table: PropTypes.shape({
    dataRows: PropTypes.number,
    headerRows: PropTypes.number,
    content: PropTypes.arrayOf(PropTypes.arrayOf(PropTypes.string)),
  }).isRequired,
};

export default TableContent;
