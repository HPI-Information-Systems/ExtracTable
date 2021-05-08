import { Box, Button } from '@material-ui/core';
import { InfoOutlined } from '@material-ui/icons';
import PropTypes from 'prop-types';
import React, { useState } from 'react';
import InfoDialog from './components/InfoDialog';

const TableMeta = ({ table }) => {
  const [isOpen, setOpen] = useState(false);
  return (
    <div className="TableMeta">
      <Box display="flex" justifyContent="flex-end">
        <Button
          color="primary"
          startIcon={<InfoOutlined />}
          size="small"
          onClick={() => setOpen(true)}
        >
          Details
        </Button>
      </Box>
      <InfoDialog
        table={table}
        handleClose={() => setOpen(false)}
        open={isOpen}
      />
    </div>
  );
};

TableMeta.defaultProps = {
  table: undefined,
};

TableMeta.propTypes = {
  table: PropTypes.shape({
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
  }),
};

export default TableMeta;
