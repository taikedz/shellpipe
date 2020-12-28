QUOTES = ('"', "'")
ESCAPE = '\\'
WHITESPACE = (" ", "\t")


class TokenError(Exception):
    pass


def parse(command_string):
    """ Given a command string, break it down into a list of command line tokens.
    """
    final_tokens = []
    
    while command_string:
        try:
            next_token, command_string = _take_token(command_string)

        except TokenError as e:
            raise TokenError("{} == {}".format(str(e), command_string))
        final_tokens.append(next_token)

    return final_tokens


def _take_token(command_string):
    """ Given a command string, extract a single token.

    This token reader is capable of detecting several shell idiosyncracies:

    * non-quoted whitespace is discarded
    * escape sequences with "\\" are recognised
    * bunched up strings "like"'this' are detected as a single token 'likethis'

    This tokenizer DOES NOT do globbing NOR shell variable subtitution.

    @return (token, remaining_command_string)
    """

    return _take_unquoted_token(command_string)


def _take_unquoted_token(command_string):
    current_token = []
    escaping = False

    characters = []
    characters.extend(command_string)
    # This effectively splits per-character,
    #   supporting unicode characters atomically
    #   unless encoding is set otherwise

    while characters:
        c = characters.pop(0)

        if c is ESCAPE:
            escaping = _process_escape_character(c, escaping, current_token)

        elif c in QUOTES and not escaping:
            current_token.extend( _take_quoted_token(characters, quote_mark=c) )

        elif c in WHITESPACE and not escaping:
            if current_token: # ... has content
                break

        else:
            current_token.append(c)
            escaping = False

    if escaping:
        raise TokenError("Unterminated escape sequence")

    return ''.join(current_token), ''.join(characters)


def _take_quoted_token(command_characters, quote_mark):
    current_token = []
    escaping = False

    while command_characters:
        c = command_characters.pop(0)

        if c is ESCAPE and quote_mark == '"': # In shell, only double-quoted strings use escaping
            escaping = _process_escape_character(c, escaping, current_token)

        elif c is quote_mark:
            if not escaping:
                return ''.join(current_token)

        else:
            current_token.append(c)
            escaping = False

    raise TokenError("Unterminated quoted string {}".format(''.join(current_token)))


def _process_escape_character(c, escaping, current_token):
    if escaping: # An escaped escape character
        current_token.append(c)

    return not escaping # Escaper or escapee, either way, this state flips

