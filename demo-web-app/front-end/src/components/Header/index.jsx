import { AppBar, Toolbar, Typography } from '@material-ui/core';
import React from 'react';

const Header = () => (
  <AppBar className="Header" position="static" elevation={0}>
    <Toolbar variant="dense">
      <Typography variant="h6">ExtracTable</Typography>
    </Toolbar>
  </AppBar>
);

export default Header;
