from copy import deepcopy
from json import dumps, loads


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
    return {'flags': {'escape_next': True, 'escape_occurred': True}}


def handle_quotation(has_starting_quotes, is_open, **_):
    if is_open:
        if not has_starting_quotes:
            return None
        return {'flags': {'has_ending_quotes': True}}
    return {'flags': {'has_starting_quotes': True, 'quotation_occurred': True}, 'open': True}


handlerMap = {
    'content': handle_content,
    'delimiter': handle_delimiter,
    'escape': handle_escape,
    'quotation': handle_quotation,
}


def get_seq_type(config, flags, raw, cursor_position):
    matches = {
        special_name: bool(special_char) and raw.startswith(special_char, cursor_position)
        for special_name, special_char in config.items()
    }
    match_count = len([match_result for match_result in matches.values() if match_result])
    if match_count > 1 and matches['delimiter']:
        raise Exception('Multiple possible interpretations')
    if not match_count:
        return 'content', 1
    matched_type = next(k for k, v in matches.items() if v)
    if match_count > 1:  # escape and quotation both match
        if flags['has_starting_quotes']:
            if raw.startswith(config['quotation'], cursor_position + len(config['escape'])) or \
                    raw.startswith(config['escape'], cursor_position + len(config['escape'])):
                matched_type = 'escape'
            else:
                matched_type = 'quotation'
        else:
            matched_type = 'quotation'
    return matched_type, len(config[matched_type])


def parse_line_character_delimiter(
        raw,
        config,
        handle_possible_quoting_character,
        handle_possible_escape_character,
        max_length,
        cache=None
):
    flags = cache['flags'] if cache else{
        'escape_next': False,
        'has_ending_quotes': False,
        'has_starting_quotes': False,
        'escape_occurred': False,
        'quotation_occurred': False,
        'is_open': False
    }
    row = cache['row'] if cache else []
    current_cell = cache['cell'] if cache else ''
    cursor_position = cache['cursor'] if cache else 0
    while cursor_position < len(raw):
        try:
            seq_type, length = get_seq_type(config, flags, raw, cursor_position)
            if flags['escape_next']:
                if seq_type == 'content':
                    return None
                else:
                    seq_type = 'content'
            if (not ('quotation' in config)
                    and seq_type == 'content'
                    and not raw[cursor_position].isalnum()):
                [
                    handle_possible_quoting_character(raw[cursor_position:cursor_position+i], {'row': [*row], 'cursor': cursor_position, 'flags': {**flags}, 'cell': current_cell})
                    for i in range(1, max_length + 1)
                    if not any(char.isalnum() for char in raw[cursor_position:cursor_position+i])
                ]
            if ('quotation' in config
                    and not ('escape' in config)
                    and seq_type == 'content'
                    and not raw[cursor_position].isalnum()
                    and cursor_position < len(raw) - 1
                    and flags['has_starting_quotes']
            ):
                [
                    handle_possible_escape_character(config['quotation'], raw[cursor_position:cursor_position+i], {'row': [*row], 'cursor': cursor_position, 'flags': {**flags}, 'cell': current_cell})
                    for i in range(1, max_length + 1)
                    if raw[cursor_position:cursor_position+i] and not any(char.isalnum() for char in raw[cursor_position:cursor_position+i])
                ]
            if flags['has_ending_quotes'] and seq_type != 'delimiter':
                # warnings.warn('Illegal character at position ' + str(cursor_position))
                return None
            flags['escape_next'] = False
            if not flags['is_open'] and seq_type == 'content' and raw[cursor_position].isspace():
                # early exit for cases where we have spaces outside of fields
                cursor_position += length
                continue
            update = handlerMap[seq_type](**flags)
            if update is None:
                return None
            flags = {**flags, **update['flags']} if 'flags' in update else flags
            if update.get('open'):
                flags['is_open'] = True
                current_cell = ''
            if update.get('add_as_content'):
                current_cell += raw[cursor_position:cursor_position + length]
            cursor_position += length
            if update.get('close'):
                flags['is_open'] = False
                row.append(current_cell.strip(' '))
                current_cell = ''
        except:  # Exception in get_seq_type
            return None
    if flags['has_starting_quotes'] and not flags['has_ending_quotes'] or flags['escape_next']:
        # warnings.warn('Illegal character at position ' + str(cursor_position))
        return None
    else:
        row.append(current_cell.strip(' '))
    if ('escape' in config and not flags['escape_occurred']) or ('quotation' in config and not flags['quotation_occurred']):
        return None
    return {
        'type': 'character',
        **config,
        'parsed': row
    }


def parse_line(raw, delimiter, max_length):
    possible_quotes = []
    possible_escapes = []
    solutions = []

    def handle_possible_escape_character(quotation, escape, cache):
        if {'quotation': quotation, 'escape': escape} in possible_escapes:
            return
        possible_escapes.append({'quotation': quotation, 'escape': escape})
        solutions.append(parse_line_character_delimiter(
            raw,
            {
                'delimiter': delimiter,
                'quotation': quotation,
                'escape': escape
            },
            handle_possible_quoting_character,
            handle_possible_escape_character,
            max_length,
            deepcopy(cache)
        ))

    def handle_possible_quoting_character(quotation, cache):
        if quotation in possible_quotes:
            return
        possible_quotes.append(quotation)
        solutions.append(parse_line_character_delimiter(
            raw,
            {
                'delimiter': delimiter,
                'quotation': quotation,
            },
            handle_possible_quoting_character,
            handle_possible_escape_character,
            max_length,
            deepcopy(cache)
        ))
        solutions.append(parse_line_character_delimiter(
            raw,
            {
                'delimiter': delimiter,
                'quotation': quotation,
                'escape': quotation  # according to RFC 4180 2 (7)
            },
            handle_possible_quoting_character,
            handle_possible_escape_character,
            max_length,
            deepcopy(cache)
        ))

    solutions.append(parse_line_character_delimiter(raw.strip(' '), {'delimiter': delimiter}, handle_possible_quoting_character,
                                                    handle_possible_escape_character, max_length))
    return [
        loads(dump)
        for dump in set(
            dumps(solution, sort_keys=True)
            for solution in solutions
            if solution
        )
    ]
