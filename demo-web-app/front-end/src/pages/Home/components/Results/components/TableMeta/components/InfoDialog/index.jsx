import {
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Grid,
  Typography,
} from '@material-ui/core';
import PropTypes from 'prop-types';
import React from 'react';

const InfoDialog = ({
  handleClose, open, table,
}) => (
  <Dialog
    open={open}
    onClose={handleClose}
    fullWidth
  >
    <DialogTitle>Table details</DialogTitle>
    <DialogContent>
      <Grid
        container
        direction="row"
        justify="space-between"
        alignItems="flex-start"
        spacing={1}
      >
        <Grid item xs={4}><Typography variant="body2" color="textPrimary">From</Typography></Grid>
        <Grid item xs={1}><Typography variant="body2" color="textSecondary" align="right">{ table.from }</Typography></Grid>
        <Grid item xs={1} />
        <Grid item xs={4}><Typography variant="body2" color="textPrimary">To</Typography></Grid>
        <Grid item xs={1}><Typography variant="body2" color="textSecondary" align="right">{ table.to }</Typography></Grid>
        <Grid item xs={4}><Typography variant="body2" color="textPrimary">Header rows</Typography></Grid>
        <Grid item xs={1}><Typography variant="body2" color="textSecondary" align="right">{ table.headerRows }</Typography></Grid>
        <Grid item xs={1} />
        <Grid item xs={4}><Typography variant="body2" color="textPrimary">Data rows</Typography></Grid>
        <Grid item xs={1}><Typography variant="body2" color="textSecondary" align="right">{ table.dataRows }</Typography></Grid>
        <Grid item xs={4}><Typography variant="body2" color="textPrimary">Header consistency</Typography></Grid>
        <Grid item xs={1}><Typography variant="body2" color="textSecondary" align="right">{ table.headerConsistency.toFixed(2) }</Typography></Grid>
        <Grid item xs={1} />
        <Grid item xs={4}><Typography variant="body2" color="textPrimary">Data consistency</Typography></Grid>
        <Grid item xs={1}><Typography variant="body2" color="textSecondary" align="right">{ table.dataConsistency.toFixed(2) }</Typography></Grid>
        <Grid item xs={4}><Typography variant="body2" color="textPrimary">Parsing Instruction</Typography></Grid>
        <Grid item xs={1}><Typography variant="body2" color="textSecondary" align="right">{ table.parsingInstruction.type }</Typography></Grid>
        <Grid item xs={1} />
        {
            table.parsingInstruction.type === 'CSV' ? (
              <>
                <Grid item xs={4}><Typography variant="body2" color="textPrimary">Delimiter</Typography></Grid>
                <Grid item xs={1}><Typography variant="body2" color="textSecondary" align="right">{ table.parsingInstruction.dialect.delimiter }</Typography></Grid>
                <Grid item xs={4} />
                <Grid item xs={1} />
                <Grid item xs={1} />
                <Grid item xs={4}><Typography variant="body2" color="textPrimary">Quotation</Typography></Grid>
                <Grid item xs={1}><Typography variant="body2" color="textSecondary" align="right">{ table.parsingInstruction.dialect.quotation || 'NaN' }</Typography></Grid>
                <Grid item xs={4} />
                <Grid item xs={1} />
                <Grid item xs={1} />
                <Grid item xs={4}><Typography variant="body2" color="textPrimary">Escape</Typography></Grid>
                <Grid item xs={1}><Typography variant="body2" color="textSecondary" align="right">{ table.parsingInstruction.dialect.escape || 'NaN' }</Typography></Grid>
              </>
            ) : (
              <>
                <Grid item xs={4} />
                <Grid item xs={1} />
              </>
            )
          }
      </Grid>
    </DialogContent>
    <DialogActions>
      <Button onClick={handleClose} color="primary" autoFocus>
        Close
      </Button>
    </DialogActions>
  </Dialog>
);

InfoDialog.defaultProps = {
  table: undefined,
};

InfoDialog.propTypes = {
  handleClose: PropTypes.func.isRequired,
  open: PropTypes.bool.isRequired,
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

export default InfoDialog;
