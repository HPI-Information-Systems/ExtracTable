import { Box, Container } from '@material-ui/core';
import React, { useState } from 'react';
import Error from './components/Error';
import FileUpload from './components/FileUpload';
import Results from './components/Results';

const Home = () => {
  const [result, setResult] = useState();
  const [error, setError] = useState();
  const onResult = (uploadResult) => {
    setError();
    setResult(uploadResult);
  };
  const onError = (uploadError) => {
    setError(uploadError);
    setResult();
  };
  const onReset = () => {
    setResult();
    setError();
  };
  return (
    <Container className="Home">
      {
        !result && !error && (
          <Box mt="33vh">
            <FileUpload onResult={onResult} onError={onError} />
          </Box>
        )
      }
      {
        error && (
          <Error description={error.message} onReset={onReset} title="Could not extract tables" />
        )
      }
      {
        result && (
          <Results
            fileName={result.fileName}
            runTime={result.runTime}
            tables={result.tables}
            onReset={onReset}
          />
        )
      }
    </Container>
  );
};

export default Home;
