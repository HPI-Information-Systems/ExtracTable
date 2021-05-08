import {
  Paper, Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
} from '@material-ui/core';
import { flatten, isEmpty, map } from 'lodash';
import React from 'react';
import styles from '../../styles';

const TablePreview = ({ header, rows, rowStyles }) => {
  const classes = styles();
  return (
    <div className="TablePreview">
      <TableContainer component={Paper} variant="outlined">
        <Table size="small" className={classes.tableGridLines}>
          {
            !isEmpty(header) && (
              <TableHead>
                <TableRow>
                  {
                    map(header, (columnName, iColumnName) =>
                      (<TableCell key={iColumnName}>{ columnName }</TableCell>))
                  }
                </TableRow>
              </TableHead>
            )
          }
          <TableBody>
            {
              isEmpty(flatten(rows)) ? (
                <TableRow>
                  <TableCell colSpan={isEmpty(header) ? 1 : header.length} align="center">No Data</TableCell>
                </TableRow>
              ) : map(rows, (row, iRow) => (
                <TableRow
                  key={iRow}
                  style={rowStyles && iRow < rowStyles.length && rowStyles[iRow]}
                >
                  {
                    map(row, (column, iColumn) => (
                      <TableCell
                        key={iColumn}
                        className={classes.tableCellGridLines}
                      >
                        { column }
                      </TableCell>
                    ))
                  }
                </TableRow>
              ))
            }
          </TableBody>
        </Table>
      </TableContainer>
    </div>
  );
};

export default TablePreview;
