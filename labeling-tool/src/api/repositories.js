import {
  concat, every, get, has, isEmpty, map, omit, partition, reject, sample,
} from 'lodash';
import { get as fpGet } from 'lodash/fp';
import superagent from 'superagent';

const getUnusedRepositories = () => superagent
  .get('/api/repositories')
  .query({
    used__exists: 'false',
  })
  .then(fpGet('body'));

const updateRepository = (repositoryId, update) => superagent
  .patch(`/api/repositories/${repositoryId}`, update);

const setRepositoryUsed = (repositoryId, used) => updateRepository(repositoryId, { used });

export const replaceRepository = (repositoryId, repository) => superagent
  .put(`/api/repositories/${repositoryId}`, omit({
    ...repository,
    files: map(repository.files, (file) => ({ ...file, id: { $oid: file.id } })),
  }, ['_id']));

export const getFileForClassification = () => getUnusedRepositories()
  .then((repositories) => {
    if (isEmpty(repositories)) throw Error('No unused repositories!');
    const randomRepository = sample(repositories);
    const unclassifiedFiles = reject(randomRepository.files, (file) => has(file, 'isContainingTable'));
    if (isEmpty(unclassifiedFiles)) {
      return setRepositoryUsed(get(randomRepository, '_id'), false).then(getFileForClassification);
    }
    const file = sample(unclassifiedFiles);
    return file.id;
  });

const getRepositoryById = (repositoryId) => superagent
  .get(`/api/repositories/${encodeURI(repositoryId)}`)
  .then(fpGet('body'));

export const classifyFile = (repositoryId, fileId, isContainingTable) =>
  getRepositoryById(repositoryId)
    .then((repository) => {
      if (get(repository, 'used') && isContainingTable !== 'none') throw Error('Repository is already being used.');
      const [[prevFile], otherFiles] = partition(repository.files, (file) => file.id === fileId);
      const nextFile = { ...prevFile, isContainingTable };
      const lacksRemainingCandidates = every(otherFiles, (file) => has(file, 'isContainingTable'));
      const update = {
        ...omit(repository, ['used']),
        files: concat(otherFiles, [nextFile]),
        ...(lacksRemainingCandidates && { used: false }),
        ...(isContainingTable === 'multi' && { used: true }),
      };
      return replaceRepository(repositoryId, update);
    });
