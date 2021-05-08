import React, { useEffect, useState } from 'react';
import { Navigate } from 'react-router-dom';
import { getFileForAnnotation, getFileForReview } from '../../../../api/files';
import Error from '../../../../components/Error';
import LoadingScreen from '../../../../components/LoadingScreen';

const REVIEW_MODE = true;

const RedirectToNextFile = () => {
  const [next, setNext] = useState();
  const [fetchError, setError] = useState();
  useEffect(() => {
    (REVIEW_MODE ? getFileForReview() : getFileForAnnotation())
      .then((fileId) => setNext(`/label/${encodeURIComponent(fileId)}`))
      .catch(setError);
  }, []);
  return (
    <>
      { next && (<Navigate to={next} />)}
      { !next && (
        fetchError ? (
          <Error message="No unlocked files available" description={fetchError.message} />
        ) : (
          <LoadingScreen message="Fetching next file..." />
        )
      )}
    </>
  );
};

export default RedirectToNextFile;
