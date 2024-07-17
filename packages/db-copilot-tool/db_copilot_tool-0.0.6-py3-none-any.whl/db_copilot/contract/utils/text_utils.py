def rstrip_text(source: str, text: str):
    source = source.strip()
    text = text.strip()
    if source.endswith(text):
        return source[:-len(text)].strip()

    return source

def lstrip_text(source: str, text: str):
    source = source.strip()
    text = text.strip()
    if source.startswith(text):
        return source[len(text):].strip()
    
    return source