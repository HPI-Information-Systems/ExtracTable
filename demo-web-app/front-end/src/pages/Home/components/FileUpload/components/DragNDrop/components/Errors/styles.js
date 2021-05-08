import { makeStyles } from '@material-ui/core';
import theme from '../../../../../../../../theme';

export default makeStyles({
  root: {
    backgroundColor: theme.palette.error.main,
  },
  errorText: {
    color: '#FFFFFF',
  },
  errorList: {
    listStyle: 'none',
    margin: 0,
  },
});
