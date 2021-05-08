import { grey } from '@material-ui/core/colors';
import { makeStyles } from '@material-ui/core/styles';

export default makeStyles({
  tableGridLines: {
    borderCollapse: 'collapse',
    borderWidth: 1,
    borderStyle: 'solid',
    borderColor: grey[500],
  },
  tableCellGridLines: {
    borderWidth: 1,
    borderStyle: 'solid',
    borderColor: grey[500],
  },
});
