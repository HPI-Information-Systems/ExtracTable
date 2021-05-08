from typing import Dict, List, Optional, Any

from pydash import find_key, find_index


def handle_content(is_open, **_):
    return {
        'add_as_content': True,
        'open': not is_open,
    }


def handle_delimiter(has_ending_quotes, has_starting_quotes, is_open, **_):
    if is_open:
        if not has_starting_quotes or has_ending_quotes:
            return {
                'close': True,
                'flags': {
                    'has_ending_quotes': False,
                    'has_starting_quotes': False,
                },
            }
        return {
            'add_as_content': True,
        }
    return {
        'open': True,
        'close': True,
    }


def handle_escape(**_):
    return {'flags': {'escape_next': True}}


def handle_quotation(has_starting_quotes, is_open, **_):
    if is_open:
        if not has_starting_quotes:
            raise Exception('Unescaped quotes within field!')
        return {'flags': {'has_ending_quotes': True}}
    return {'flags': {'has_starting_quotes': True, 'quotation_occurred': True}, 'open': True}


handler_map = {
    'content': handle_content,
    'delimiter': handle_delimiter,
    'escape': handle_escape,
    'quotation': handle_quotation,
}


def get_seq_type(config, flags, raw, cursor_position):
    matches = {
        special_name: [bool(special_char) and raw.startswith(special_char, cursor_position) for special_char in special_chars]
        for special_name, special_chars in config.items()
    }
    match_count = len([match_result for match_result in matches.values() if any(match_result)])
    if match_count > 1 and any(matches['delimiter']):
        raise Exception('Multiple possible interpretations')
    if not match_count:
        return 'content', 1
    matched_type = find_key(matches, any)
    if match_count > 1:  # can be escape or quotation
        if flags['has_starting_quotes']:
            if raw.startswith(config['quotation'][0], cursor_position + len(config['escape'][0])):  # assume just one escape/ quotation
                matched_type = 'escape'
            else:
                matched_type = 'quotation'
        else:
            matched_type = 'quotation'
    return matched_type, len(config[matched_type][find_index(matches[matched_type])])


def parse_line_using_layout_delimiter(raw: str, config: Dict[str, Any]) -> List[str]:
    indexes = config['delimiters']
    if not indexes:
        return [raw]
    pairs = zip(indexes, [*indexes[1:], len(raw)])
    return [raw[from_index:to_index].strip() for (from_index, to_index) in pairs]


def parse_line_using_character_delimiter(raw: str, config: Dict[str, List[str]]) -> Optional[List[str]]:
    flags = {
        'escape_next': False,
        'has_ending_quotes': False,
        'has_starting_quotes': False,
        'is_open': False
    }
    raw = raw.rstrip('\n').strip('\x00')
    row = []
    current_cell = ''
    cursor_position = 0
    trim = not any(' ' in ''.join(special_chars) for special_chars in config.values())
    if trim:
        raw = raw.strip(' ')
    while cursor_position < len(raw):
        seq_type, length = get_seq_type(config, flags, raw, cursor_position)
        if flags['escape_next']:
            if seq_type == 'content':
                raise Exception('Cannot escape content!')
            seq_type, length = ('content', 1)
        if flags['has_ending_quotes'] and seq_type != 'delimiter':
            raise Exception('Delimiter expected after ending quotes!')
        flags['escape_next'] = False
        if not flags['is_open'] and seq_type == 'content' and raw[cursor_position].isspace():
            # early exit for cases where we have spaces outside of fields
            cursor_position += length
            continue
        update = handler_map[seq_type](**flags)
        flags = {**flags, **update['flags']} if 'flags' in update else flags
        if update.get('open'):
            current_cell = ''
            flags['is_open'] = True
        if update.get('add_as_content'):
            current_cell += raw[cursor_position:cursor_position + length]
        cursor_position += length
        if update.get('close'):
            flags['is_open'] = False
            row.append(current_cell.strip(' ') if trim else current_cell)
            current_cell = ''
    if flags['has_starting_quotes'] and not flags['has_ending_quotes'] or flags['escape_next']:
        raise Exception('Missing ending quotes or trailing escape')
    row.append(current_cell.strip(' ') if trim else current_cell)
    row = [field.strip() for field in row]
    return row


def parse_line(annotated_line: Dict[str, any]) -> List[str]:
    delimiter = annotated_line['delimiter']
    raw = annotated_line['raw'].rstrip('\n')
    if delimiter['type'] == 'character':
        return parse_line_using_character_delimiter(
            raw,
            {
                'delimiter': [sequence.replace(r'\t', '\t') for sequence in delimiter['sequence']],
                'escape': annotated_line['escape'],
                'quotation': annotated_line['quotation']
            }
        )
    else:
        return parse_line_using_layout_delimiter(
            raw.expandtabs(),
            {
                'delimiters': delimiter['indexes']
            }
        )
