import { createMuiTheme } from '@material-ui/core/styles';
import { grey } from '@material-ui/core/colors';

export default createMuiTheme({
  palette: {
    background: {
      default: grey[50],
    },
    primary: {
      main: grey[800],
    },
    secondary: {
      main: grey[50],
    },
    text: {
      primary: grey[800],
    },
  },
  props: {
    MuiButton: {
      disableRipple: true,
      disableElevation: true,
    },
    MuiIconButton: {
      disableRipple: true,
    },
  },
});
