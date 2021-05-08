import { map } from 'lodash';
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { getFileById } from '../../api/files';
import Error from '../../components/Error';
import LoadingScreen from '../../components/LoadingScreen';
import FileViewer from '../../components/FileViewer';

const ViewFile = () => {
  const { fileId } = useParams();
  const [fetchedFile, setFile] = useState();
  const [fetchError, setError] = useState();
  useEffect(() => {
    document.title = `Viewing ${fileId}`;
    getFileById(fileId)
      .then((file) => {
        document.title = `Viewing ${file.name}`;
        setFile({
          ...file,
          content: map(file.content, (line) => ({
            ...line,
            raw: line.raw
              .replaceAll(/ /g, '␣')
              .replaceAll(/\t/g, '→'),
          })),
        });
      })
      .catch(setError);
  }, [fileId]);
  return (
    <div className="ViewFile">
      {
        fetchedFile ? (
          <FileViewer file={fetchedFile} />
        ) : (
          <LoadingScreen message="Fetching file..." />
        )
      }
      {
        fetchError && (
          <Error message="Could not fetch file" description={fetchError.message} />
        )
      }
    </div>
  );
};

export default ViewFile;
