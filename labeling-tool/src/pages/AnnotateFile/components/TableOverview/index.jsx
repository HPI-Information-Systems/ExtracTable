import {
  Box,
  IconButton,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@material-ui/core';
import { DeleteOutlined, EditOutlined } from '@material-ui/icons';
import { isEmpty } from 'codemirror/src/util/misc';
import { map } from 'lodash';
import React from 'react';
import theme from '../../../../theme';

const TableOverview = ({ onRemoveTable, onTable, tables }) => (
  <div className="TableOverview">
    <TableContainer component={Paper} variant="outlined" style={{ borderColor: theme.palette.primary.main }}>
      <Table size="small">
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>From</TableCell>
            <TableCell>To</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {
            isEmpty(tables)
              ? (<TableRow><TableCell colSpan={4} align="center">No tables extracted yet</TableCell></TableRow>)
              : map(tables, (table, iTable) => (
                <TableRow key={iTable}>
                  <TableCell>{ iTable + 1 }</TableCell>
                  <TableCell>{ table.from + 1 }</TableCell>
                  <TableCell>{ table.to + 1 }</TableCell>
                  <TableCell>
                    <Box display="flex">
                      <IconButton size="small" onClick={() => onTable(table)}>
                        <EditOutlined fontSize="small" color="primary" />
                      </IconButton>
                      <Box flexGrow={1} />
                      <IconButton size="small" onClick={() => onRemoveTable(iTable)}>
                        <DeleteOutlined fontSize="small" style={{ color: theme.palette.error.main }} />
                      </IconButton>
                    </Box>
                  </TableCell>
                </TableRow>
              ))
          }
        </TableBody>
      </Table>
    </TableContainer>
  </div>
);

export default TableOverview;
