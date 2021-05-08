import React from 'react';
import { Route, Routes } from 'react-router-dom';
import AnnotateFile from '../../pages/AnnotateFile';
import RedirectToNextFile from './subpages/RedirectToNextFile';

const Label = () => (
  <div className="Label">
    <Routes>
      <Route path="/" element={<RedirectToNextFile />} />
      <Route path=":fileId" element={<AnnotateFile />} />
    </Routes>
  </div>
);

export default Label;
