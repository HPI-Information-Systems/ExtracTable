import { stringify } from 'csv-string';
import JSZip from 'jszip';
import { forEach } from 'lodash';

// eslint-disable-next-line import/prefer-default-export
export const exportTables = (tables) => {
  const zip = JSZip();
  forEach(tables, (table) => {
    zip.file(`Table ${table.from}-${table.to} ${table.parsingInstruction.type}.csv`, stringify(table.content));
  });
  return zip.generateAsync({ type: 'blob' });
};
