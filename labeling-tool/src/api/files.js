import {
  get, head, isEmpty, omit, sortBy,
} from 'lodash';
import { get as fpGet } from 'lodash/fp';
import superagent from 'superagent';
import { batchReplaceLines, getAllLinesByFileId } from './lines';

export const getFileById = (fileId) => superagent
  .get(`/api/files/${encodeURI(fileId)}`)
  .then(fpGet('body'))
  .then((file) => getAllLinesByFileId(get(file, '_id'))
    .then((content) => ({ ...file, content: sortBy(content, 'index') })));

const updateFile = (fileId, update) => superagent
  .patch(`/api/files/${fileId}`, update);

export const unlockFile = (fileId) => updateFile(fileId, { status: 'unlocked' });

export const skipFile = (fileId) => updateFile(fileId, { status: 'skipped' });

export const reviewOKFile = (fileId) => updateFile(fileId, { review: 'ok' });

export const reviewDiscussFile = (fileId) => updateFile(fileId, { review: 'discuss' });

export const denounceFile = (fileId) => updateFile(fileId, { status: 'denounced' });

const getUnlockedFiles = () => superagent
  .get('/api/files')
  .query({
    status: 'unlocked',
  })
  .then(fpGet('body'));

export const getFileForAnnotation = () => getUnlockedFiles()
  .then((unlockedFiles) => {
    if (isEmpty(unlockedFiles)) throw Error('No unlocked files available');
    return get(head(unlockedFiles), '_id');
  });

export const getUnreviewedAnnotatedFiles = () => superagent
  .get('/api/files')
  .query({
    status: 'annotated',
    type: 'complex',
    review__exists: false,
  })
  .then(fpGet('body'));

export const getFileForReview = () => getUnreviewedAnnotatedFiles()
  .then((unreviewedFiles) => {
    if (isEmpty(unreviewedFiles)) throw Error('No unreviewed files available');
    return get(head(unreviewedFiles), '_id');
  });

export const replaceFile = (fileId, file) => superagent
  .put(`/api/files/${fileId}`, omit({
    ...file,
    repositoryId: { $oid: file.repositoryId },
  }, ['_id', 'content']))
  .then(() => batchReplaceLines(file.content));
