import { Button, Typography } from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import React, { useEffect } from 'react';

const Controller = ({ onFileClassification }) => {
  useEffect(() => {
    const handleKeyUp = ({ which }) => {
      if (which === 37) onFileClassification('none');
      else if (which === 38) onFileClassification('simple');
      else if (which === 39) onFileClassification('multi');
    };
    window.addEventListener('keyup', handleKeyUp);
    return () => {
      window.removeEventListener('keyup', handleKeyUp);
    };
  }, [onFileClassification]);
  return (
    <div className="Controller">
      <Grid
        container
        direction="row"
        justify="space-between"
        alignItems="flex-start"
      >
        <Grid container item xs={4} direction="column" alignItems="flex-start">
          <Grid item xs>
            <Button variant="contained" onClick={() => onFileClassification('none')}>No Table</Button>
          </Grid>
          <Grid item xs>
            <Typography variant="caption" color="textSecondary">
              ⬅︎ Press left
            </Typography>
          </Grid>
        </Grid>
        <Grid container item xs={4} direction="column" alignItems="center">
          <Grid item xs>
            <Button
              variant="contained"
              color="primary"
              onClick={() => onFileClassification('simple')}
            >
              Simple Table
            </Button>
          </Grid>
          <Grid item xs>
            <Typography variant="caption" align="center" color="textSecondary">
              Press up ⬆︎
            </Typography>
          </Grid>
        </Grid>
        <Grid container item xs={4} direction="column" alignItems="flex-end">
          <Grid item xs>
            <Button
              variant="contained"
              color="primary"
              onClick={() => onFileClassification('multi')}
            >
              Complex Table(s)
            </Button>
          </Grid>
          <Grid item xs>
            <Typography variant="caption" align="right" color="textSecondary">
              Press right ⮕
            </Typography>
          </Grid>
        </Grid>
      </Grid>
    </div>
  );
};

export default Controller;
