import superagent from 'superagent';
import { get as fpGet } from 'lodash/fp';

// eslint-disable-next-line import/prefer-default-export
export const extract = (file, onProgress) => superagent
  .post('/api/extract')
  .timeout({
    response: 60000, // Wait 60 seconds for the server to start sending,
  })
  .attach('inputFile', file)
  .on('progress', onProgress)
  .then(fpGet('body'));
