import React from 'react';
import { Route, Routes } from 'react-router-dom';
import ClassifyFile from '../../pages/ClassifyFile';
import RedirectToNextFile from './subpages/RedirectToNextFile';

const Filter = () => (
  <div className="Filter">
    <Routes>
      <Route path="/" element={<RedirectToNextFile />} />
      <Route path=":fileId" element={<ClassifyFile />} />
    </Routes>
  </div>
);

export default Filter;
