QUOTES = ('"', "'")
ESCAPE = ('\\',)
WHITESPACE = (" ", "\t")


class TokenError(Exception):
    pass


def _take_token(command_string):
    """ Given a command string, extract a single token.

    This token reader is capable of detecting several shell idiosyncracies:

    * non-quoted whitespace is discarded
    * escape sequences with "\\" are recognised
    * bunched up strings "like"'this' are detected as a single token 'likethis'

    This tokenizer DOES NOT do globbing.

    @return (token, remaining_command_string)
    """
    current_token = []
    in_token = False
    escaping = False
    found = False

    characters = []
    characters.extend(command_string)
    # This effectively splits per-character,
    #   supporting unicode characters atomically
    #   unless encoding is set otherwise

    while not found and characters:
        c = characters.pop(0)
        if c in QUOTES:
            if escaping:
                current_token.append(c)
                escaping = False
            else:
                if in_token:
                    found = True
                    in_token = False

                else:
                    in_token = True

                if characters[0:1] in QUOTES:
                    # Shell idiosyncracy:
                    #   When quoted strings are back to back,
                    #   they form a single string token!
                    # Don't declare victory yet.
                    found = False

        elif c in WHITESPACE:
            if escaping:
                current_token.append(c)
                escaping = False

            elif in_token:
                current_token.append(c)

            else:
                if current_token:
                    found = True
                # Else, ignore space

        elif c in ESCAPE:
            current_token.append(c)
            # If we were already escaping, this escaper is escaped, come out
            #   else, start escaping
            escaping = not escaping

        else:
            current_token.append(c)
            escaping = False

    if in_token:
        raise TokenError("Unterminated quoted string {}".format(characters))

    elif escaping:
        raise TokenError("Unterminated escape sequence")

    return ''.join(current_token), ''.join(characters)


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

