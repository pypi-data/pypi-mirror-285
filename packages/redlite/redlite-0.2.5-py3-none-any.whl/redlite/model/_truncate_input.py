from redlite._core import Message


'''
Truncate input (useful for models with smaller context size).

Please note that we truncate based on the character count (not token count). Therefore, you can still get
context overflow if you are unlucky.

Strategy applied depends on the existense or absense of system message:

1. If no system message:
   * try to remove older user messages, until conversation fits into the `max_chars` limit.
     If you end up with non-empty conversation, we are done
   * Else we have the latest user message that is longer than the limit. Truncate it, removing enough characters
     from the middle and replacing with text "...[snip]..."

2. If there is system message:
   * lower the limit by the size of the system message, and apply algorithm (1) to the rest. If result is a non-empty conversation,
     then insert system message upfront and return this conversation
   * Else, take only the last user message and truncate it by half of the amount, do the same to the system

'''
class TruncateInput:
    def __init__(self, engine, max_chars=32*1024):
        self.max_chars = max_chars
        self.engine = engine

    def __call__(self, messages: list[Message]) -> str:
        text = [message['content'] for message in messages]
        if sum(len(x) for x in text) <= self.max_chars:
            return self.engine(messages)

        if messages[0]['role'] != 'system':
            truncated = []
            l = 0
            for mess in reversed(messages):
                if l + len(mess) > self.max_chars:
                    break
                else:
                    truncated.append(mess)
                    l += len(mess)
            return reversed(truncated)



        if messages[0]['role'] == 'system':
            # try not to throw system message away
            if len(text[0]) + len(text[-1]) <= self.max_chars:
                # remove earlier conversation messages untill we fit
                space = self.max_chars - len(text[0])
                i = -1
                out = []
                while space - len(text[i]) >= 0:
                    out.append(messages[i])
                    i -= 1
                    space -= len(text[i])
                messages = [messages[0]] + reversed(out)
                return self.engine(messages)
            elif len(text[0]) < self.max_chars // 2:
                # leave system as-is, truncate user message
                pass
            else:
                # truncate both - user and system, equally (from the middle)

        else:
            space = self.max_chars
            i = -1
            out = []
            while space - len(text[i]) >= 0:
                out.append(messages[i])
                i -= 1
                space -= len(text[i])
            messages = [messages[0]] + reversed(out)
            return self.engine(messages)


SNIP = "...[snip]..."

def _truncate_conversation(messages: list[Message], max_chars: int, snip=SNIP) -> list[Message]:
    if messages[0]['role'] != 'system':
        result = _truncate_blocks(messages, max_chars)
        if result:
            return result
        text = _truncate_text(messages[-1]['content'], max_chars, snip)
        return [{
            **messages[-1],
            'content': text,
        }]

    # deal with system message
    if len(messages[0]['content']) + len(snip) < max_chars:
        return [messages[0]] + _truncate_conversation(messages[1:], max_chars - len(messages[0]['content']) - len(snip))]

def _truncate_text(text, max_chars, snip=SNIP):
    '''Truncates input message to the target length, removing stuff in the middle and replacing it with '''
    assert max_chars >= len(snip)

    to_delete = len(text) - max_chars
    if to_delete <= 0:
        return text

    to_delete += len(snip)
    prefix = text[: (len(text) - to_delete) // 2] + snip
    suffix = text[len(prefix):]

    return prefix + suffix


def _truncate_blocks(messages: list[Message], max_chars: int) -> list[Message]:
    truncated = []
    l = 0
    for mess in reversed(messages):
        if l + len(mess['content']) > max_chars:
            break

        truncated.append(mess)
        l += len(mess)

    return reversed(truncated)
