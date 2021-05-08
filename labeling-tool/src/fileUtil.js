import * as expandtabs from 'expandtabs';
import {
  assign,
  filter,
  findIndex,
  findKey,
  flatten,
  get,
  isEmpty,
  join,
  map,
  mapValues,
  replace,
  some,
  startsWith,
  takeRight,
  trim,
  values,
  zip,
} from 'lodash';

export const getRawContent = ({ content }) => join(map(content, ({ raw }) => raw.replace(/(\r\n|\n|\r)/gm, '')), '\r\n');

/*
  delimiter: determines end of field
  quotation: has to be at the beginning and ending of a cell, after seeing the opening quotation
             char, delimiters are ignored until closing quotation char appeared
             (field delimiter or EOL has to occur afterwards)
  escape: next (single!) char has no special meaning and counts as content
          (rule counts for quotation and escape; cannot be applied to content or delimiter)
 */

const handleContent = ({ isOpen }) => ({
  addAsContent: true,
  open: !isOpen,
});

const handleDelimiter = ({ hasEndingQuotes, hasStartingQuotes, isOpen }) => {
  if (isOpen) {
    if (!hasStartingQuotes || hasEndingQuotes) {
      return {
        close: true,
        flags: {
          hasEndingQuotes: false,
          hasStartingQuotes: false,
        },
      };
    }
    return {
      addAsContent: true,
    };
  }
  return {
    open: true,
    close: true,
  };
};

const handleEscape = () => ({
  flags: {
    escapeNext: true,
  },
});

const handleQuotation = ({ hasStartingQuotes, isOpen }) => {
  if (isOpen) {
    if (!hasStartingQuotes) throw Error('Unescaped quotes within field!');
    return { flags: { hasEndingQuotes: true } };
  }
  return { flags: { hasStartingQuotes: true }, open: true };
};

const handlerMap = {
  content: handleContent,
  delimiter: handleDelimiter,
  escape: handleEscape,
  quotation: handleQuotation,
};

const getType = (config, flags, raw, cursorPosition) => {
  const matches = mapValues(config, (specials) =>
    map(specials, (special) => !isEmpty(special) && startsWith(raw, special, cursorPosition)));
  const matchCount = filter(flatten(values(matches))).length;
  if (matchCount > 1 && some(matches.delimiter)) throw Error('Multiple possible interpretations');
  if (!matchCount) return { type: 'content', length: 1 };
  let type = findKey(matches, some);
  if (matchCount > 1) {
    if (flags.hasStartingQuotes) {
      if (startsWith(raw, config.quotation[0], cursorPosition + config.escape[0].length)) type = 'escape'; // assume just one escape/ quotation
      else type = 'quotation';
    } else type = 'quotation';
  }
  return {
    type,
    length: config[type][findIndex(matches[type])].length,
  };
};

const parseLineCharacterDelimiter = (raw, config) => {
  const flags = {
    escapeNext: false,
    hasEndingQuotes: false,
    hasStartingQuotes: false,
    isOpen: false,
  };
  const rows = [];
  let currentCell = '';
  let cursorPosition = 0;
  try {
    while (cursorPosition < raw.length) {
      let { length, type } = getType(config, flags, raw, cursorPosition);
      if (flags.escapeNext) {
        if (type === 'content') throw Error('Cannot escape content!');
        length = 1;
        type = 'content';
      }
      if (flags.hasEndingQuotes && type !== 'delimiter') throw Error('Delimiter expected after ending quotes!');
      flags.escapeNext = false;
      const update = handlerMap[type](flags);
      assign(flags, get(update, 'flags', {}));
      if (update.open) {
        currentCell = '';
        flags.isOpen = true;
      }
      if (update.addAsContent) {
        currentCell += raw.substring(cursorPosition, cursorPosition + length);
      }
      cursorPosition += length;
      if (update.close) {
        flags.isOpen = false;
        rows.push(currentCell);
        currentCell = '';
      }
    }
    if ((flags.hasStartingQuotes && !flags.hasEndingQuotes) || flags.escapeNext) { throw Error('Missing ending quotes or trailing escape'); } else rows.push(currentCell);
  } catch (error) {
    console.warn(error);
    return [];
  }
  return rows;
};

const splitStringByIndexes = (str, indexes) => {
  if (isEmpty(indexes)) return [str];
  if (some(indexes, (index) => index < 0 || index > str.length)) {
    // console.warn('Index out of bounds');
    return [];
  }
  const pairs = zip(indexes, [...takeRight(indexes, indexes.length - 1), str.length]);
  return map(pairs, ([from, to]) => str.substring(from, to));
};

const parseLineLayoutDelimiter = (raw, {
  delimiters, escape, quotation,
}) => {
  const fields = splitStringByIndexes(raw, delimiters);
  return map(fields, (field) =>
    parseLineCharacterDelimiter(trim(field), {
      delimiter: '', escape, quotation,
    }));
};

export const parseLine = (raw, {
  delimiter, escape, quotation,
}) => {
  switch (delimiter.type) {
    case 'character':
      return parseLineCharacterDelimiter(raw.replace(/\n$/g, ''), {
        delimiter: map(delimiter.sequence, (seq) => replace(seq, /\\t/g, '\t')), escape, quotation,
      });
    case 'layout':
      return parseLineLayoutDelimiter(expandtabs(raw), {
        delimiters: delimiter.indexes, escape, quotation,
      });
    default:
      return [];
  }
};

/*
  File changes need browserify to get bundled and then stored in public/workers/modules!
  `browserify src/fileUtil.js -o public/workers/modules/fileUtilBundle.js -t [ babelify --presets [ @babel/preset-env @babel/preset-react] ]`
 */
