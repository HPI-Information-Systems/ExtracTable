import AppBar from '@material-ui/core/AppBar';
import BottomNavigation from '@material-ui/core/BottomNavigation';
import BottomNavigationAction from '@material-ui/core/BottomNavigationAction';
import { DescriptionOutlined, HomeOutlined, LibraryBooksOutlined } from '@material-ui/icons';
import React from 'react';
import { useNavigate } from 'react-router';

const AppNavigation = () => {
  const navigate = useNavigate();
  const handleChange = (_, nextLocation) => {
    navigate(`/${nextLocation}`);
  };
  return (
    <div className="AppNavigation">
      <AppBar component="footer" elevation={0} color="primary" style={{ top: 'auto', bottom: 0 }}>
        <BottomNavigation
          onChange={handleChange}
          showLabels
        >
          <BottomNavigationAction label="Filter" value="filter" icon={<LibraryBooksOutlined />} />
          <BottomNavigationAction label="Home" value="" icon={<HomeOutlined />} />
          <BottomNavigationAction label="Annotate" value="label" icon={<DescriptionOutlined />} />
        </BottomNavigation>
      </AppBar>
    </div>
  );
};

export default AppNavigation;
