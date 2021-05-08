import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { getFileForClassification } from '../../../../api/repositories';
import Error from '../../../../components/Error';
import LoadingScreen from '../../../../components/LoadingScreen';

const RedirectToNextFile = () => {
  const [next, setNext] = useState();
  const [fetchError, setError] = useState();
  useEffect(() => {
    getFileForClassification()
      .then((fileId) => setNext(`/filter/${encodeURIComponent(fileId)}`))
      .catch(setError);
  }, []);
  return (
    <>
      { next && (<Navigate to={next} />)}
      { !next && (
        fetchError ? (
          <Error message="No repository left" description={fetchError.message} />
        ) : (
          <LoadingScreen message="Fetching next file..." />
        )
      )}
    </>
  );
};

export default RedirectToNextFile;
