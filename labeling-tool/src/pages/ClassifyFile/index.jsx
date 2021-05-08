import { Box } from '@material-ui/core';
import { get } from 'lodash';
import { useSnackbar } from 'notistack';
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getFileById, unlockFile } from '../../api/files';
import { classifyFile } from '../../api/repositories';
import Error from '../../components/Error';
import LoadingScreen from '../../components/LoadingScreen';
import RedirectToNextFile from '../../routing/Filter/subpages/RedirectToNextFile';
import Controller from './components/Controller';
import FileViewer from '../../components/FileViewer';

const ClassifyFile = () => {
  const { fileId } = useParams();
  const [fetchedFile, setFile] = useState();
  const [fetchError, setError] = useState();
  const [isDone, setDone] = useState(false);
  const { enqueueSnackbar } = useSnackbar();
  useEffect(() => {
    setDone(false);
    setError(undefined);
    setFile(undefined);
    document.title = `Classifying ${fileId}`;
    getFileById(fileId)
      .then((file) => {
        document.title = `Classifying ${file.name}`;
        setFile(file);
      })
      .catch(setError);
  }, [fileId]);
  const onFileClassification = (containsTable) => {
    classifyFile(fetchedFile.repositoryId, fileId, containsTable)
      .then(() => containsTable !== 'none' && unlockFile(fileId))
      .then(() => setDone(true))
      .catch((error) => enqueueSnackbar(get(error, 'message', 'Could not classify file'), { variant: 'error' }));
  };
  return (
    <div className="ClassifyFile">
      { isDone ? (
        <RedirectToNextFile />
      ) : (
        <>
          {
            fetchedFile ? (
              <Box display="flex" flexDirection="column">
                <FileViewer file={fetchedFile} />
                <Box my={1} />
                <Controller onFileClassification={onFileClassification} />
              </Box>
            ) : (
              <LoadingScreen message="Fetching file..." />
            )
          }
          {
            fetchError && (
              <Error message="Could not fetch file" description={fetchError.message} />
            )
          }
        </>
      )}
    </div>
  );
};

export default ClassifyFile;
