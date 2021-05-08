import { Box, Typography } from '@material-ui/core';
import { map } from 'lodash';
import PropTypes from 'prop-types';
import React from 'react';
import styles from './styles';

const Errors = ({ errorMessages }) => {
  const classes = styles();
  return (
    <Box display="flex" className={`Errors ${classes.root}`} py={1} mt={1}>
      {
          errorMessages ? (
            <Typography variant="body2" className={classes.errorText}>
              <ul className={classes.errorList}>
                {
                  map(errorMessages, (error) => (
                    <li>{ error }</li>
                  ))
                }
              </ul>
            </Typography>
          ) : (
            'No errors found'
          )
        }
    </Box>
  );
};

Errors.defaultProps = {
  errorMessages: [],
};

Errors.propTypes = {
  errorMessages: PropTypes.arrayOf(PropTypes.string),
};

export default Errors;
