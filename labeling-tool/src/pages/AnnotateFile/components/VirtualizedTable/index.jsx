import { Paper, TableContainer } from '@material-ui/core';
import TableCell from '@material-ui/core/TableCell';
import { flatten, map, max } from 'lodash';
import React from 'react';
import { FixedSizeGrid } from 'react-window';

const VirtualizedTable = ({ data, rowStyles }) => {
  const longestValue = 8 * max([8, ...map(flatten(data), (value) => value.length)]);
  return (
    <div className="VirtualizedTable">
      <TableContainer component={Paper} variant="outlined">
        <FixedSizeGrid
          columnCount={max(map(data, (row) => row.length))}
          columnWidth={longestValue}
          height={300}
          rowCount={data.length}
          rowHeight={48}
          width={898}
        >
          {
              ({ columnIndex, rowIndex, style }) => (
                <TableCell
                  component="div"
                  variant="body"
                  style={{
                    ...style,
                    ...rowStyles && rowIndex < rowStyles.length && rowStyles[rowIndex],
                  }}
                >
                  <span>{ columnIndex < data[rowIndex].length ? data[rowIndex][columnIndex] : '' }</span>
                </TableCell>
              )
            }
        </FixedSizeGrid>
      </TableContainer>
    </div>
  );
};

export default VirtualizedTable;
