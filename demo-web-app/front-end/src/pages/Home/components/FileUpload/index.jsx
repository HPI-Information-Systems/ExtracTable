import PropTypes from 'prop-types';
import React, { useState } from 'react';
import { extract } from '../../../../api/extracTable';
import DragNDrop from './components/DragNDrop';
import ExtractProgress from './components/ExtractProgress';

const FileUpload = ({ onError, onResult }) => {
  const [file, setFile] = useState();
  const [uploadProgress, setUploadProgress] = useState();
  const startUpload = (selectedFile) => {
    setFile(selectedFile);
    extract(selectedFile, setUploadProgress)
      .then((result) => onResult({ ...result, fileName: selectedFile.name }))
      .catch(onError);
  };
  return (
    <div className="FileUpload">
      {
        uploadProgress ? (
          <ExtractProgress
            file={file}
            progress={uploadProgress}
          />
        ) : (
          <DragNDrop onFile={startUpload} />
        )
      }
    </div>
  );
};

FileUpload.propTypes = {
  onError: PropTypes.func.isRequired,
  onResult: PropTypes.func.isRequired,
};

export default FileUpload;
