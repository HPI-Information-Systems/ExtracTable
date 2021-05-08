import {
  chunk, get, map, reduce,
} from 'lodash';
import { get as fpGet } from 'lodash/fp';
import superagent from 'superagent';

const CHUNK_SIZE_IN_LINES = 1000;

export const getAllLinesByFileId = (fileId) => superagent
  .get('/api/lines')
  .query({ fileId })
  .then(fpGet('body'));

export const batchReplaceLines = (lines) =>
  reduce(
    chunk(lines, CHUNK_SIZE_IN_LINES),
    (prevPromise, lineChunk) => prevPromise.then(() => superagent
      .put('/api/lines', map(lineChunk, (line) => ({
        ...line,
        _id: { $oid: get(line, '_id') },
      })))),
    Promise.resolve(),
  );
