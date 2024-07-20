import textwrap

def wrap(text, length=150):
    texts = text.split('\n')
    wraped_texts = [textwrap.wrap(text, length) for text in texts]
    
    result = ''
    first = True
    for lines in wraped_texts:
        for line in lines:
            result += ('\n' if not first else '') + line
            first = False
        if len(lines) == 0: result += '\n'

    return result