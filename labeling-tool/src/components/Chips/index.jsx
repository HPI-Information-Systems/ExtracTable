import { Box, Chip } from '@material-ui/core';
import Grid from '@material-ui/core/Grid';
import { includes, map } from 'lodash';
import React from 'react';

const Chips = ({ elements, nonDeletableElements = [], onDelete }) => (
  <div className="Chips">
    <Box display="flex" flexWrap="wrap">
      <Grid
        container
        direction="row"
        justify="space-between"
        alignItems="flex-start"
      >
        {
          map(elements, (element, iElement) => (
            <Grid key={iElement} item xs>
              <Chip
                label={element}
                onDelete={!includes(nonDeletableElements, element) && (() => onDelete(element))}
              />
            </Grid>
          ))
        }
      </Grid>
    </Box>
  </div>
);

export default Chips;
