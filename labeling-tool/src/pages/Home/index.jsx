import { Button, Box, Typography } from '@material-ui/core';
import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';

const Home = () => {
  useEffect(() => {
    document.title = 'Labeling tool';
  }, []);
  return (
    <div className="Home">
      <Box height="100vh" display="flex" alignItems="center">
        <Box py={1} px={2} border={1} borderColor="primary.main" borderRadius={5}>
          <Typography color="primary" align="center" variant="h6" gutterBottom>
            What do you want to do?
          </Typography>
          <Box display="flex" mt={2}>
            <Box flexGrow={1}>
              <Button component={Link} to="/filter" variant="contained" color="secondary" fullWidth>
                Collect table files
              </Button>
            </Box>
            <Box mx={1} />
            <Box flexGrow={1}>
              <Button component={Link} to="/label" variant="contained" color="primary" fullWidth>
                Label table files
              </Button>
            </Box>
          </Box>
        </Box>
      </Box>
    </div>
  );
};

export default Home;
