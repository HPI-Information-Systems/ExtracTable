import { Box, Paper, Typography } from '@material-ui/core';
import PropTypes from 'prop-types';
import React from 'react';
import { CountdownCircleTimer } from 'react-countdown-circle-timer';
import LabeledLinearProgress from '../../../../../../components/LabeledLinearProgress';
import theme from '../../../../../../theme';

const ExtractProgress = ({
  file: { name }, progress: {
    direction, loaded, percent, total,
  },
}) => {
  const isUploading = direction === 'upload';
  const isDownloading = direction === 'download';
  const isLoading = loaded < total;
  const isUploadFinished = isUploading && !isLoading;
  const isDownloadFinished = isDownloading && !isLoading;
  return (
    <Paper
      className="ExtractProgress"
      variant="outlined"
    >
      <Box
        display="flex"
        flexDirection="column"
        width="33vw"
        height={100}
        p={1}
        justifyContent="center"
        alignItems="center"
      >
        <Typography variant="body2" gutterBottom>
          { isUploadFinished && 'Extracting tables...'}
          { isUploading && !isUploadFinished && `Uploading ${name} ...`}
          { isDownloadFinished && 'Download complete'}
          { isDownloading && !isDownloadFinished && 'Downloading results...'}
        </Typography>
        {
          !isDownloadFinished && (
            <Box
              display="flex"
              mt={2}
              width="100%"
            >
              {isLoading && <LabeledLinearProgress value={percent} />}
              {isUploadFinished && (
                <Box display="flex" flexGrow={1} justifyContent="center">
                  <CountdownCircleTimer
                    strokeWidth={2}
                    duration={60}
                    colors={theme.palette.primary.main}
                    size={40}
                    isLinearGradient
                    isPlaying
                  >
                    {({ remainingTime }) => (
                      <Typography variant="body2" color="textSecondary">{ remainingTime }</Typography>
                    )}
                  </CountdownCircleTimer>
                </Box>
              )}
            </Box>
          )
        }
      </Box>
    </Paper>
  );
};

ExtractProgress.propTypes = {
  file: PropTypes.shape({
    name: PropTypes.string.isRequired,
  }).isRequired,
  progress: PropTypes.shape({
    direction: PropTypes.string.isRequired,
    loaded: PropTypes.number.isRequired,
    percent: PropTypes.number,
    total: PropTypes.number.isRequired,
  }).isRequired,
};

export default ExtractProgress;
