from functools import lru_cache
import re
from typing import List, Tuple


emoji_pattern = re.compile("(["
    u"\U0001F600-\U0001F64F"  # emoticons
    u"\U0001F300-\U0001F5FF"  # symbols & pictographs
    u"\U0001F680-\U0001F6FF"  # transport & map symbols
    u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
    u"\U00002500-\U00002BEF"  # chinese char
    u"\U00002702-\U000027B0"
    u"\U00002702-\U000027B0"
    u"\U000024C2-\U0001F251"
    u"\U0001f926-\U0001f937"
    u"\U00010000-\U0010ffff"
    u"\u2640-\u2642"
    u"\u2600-\u2B55"
    u"\u200d"
    u"\u23cf"
    u"\u23e9"
    u"\u231a"
    u"\ufe0f"  # dingbats
    u"\u3030"
    "]+)", flags=re.UNICODE)

def align_text_tokens(tokens: List[str], sentence: str) -> List[Tuple[int, int]]:
    point = 0
    offsets = []
    for token in tokens:
        try:
            start = sentence.index(token, point)
        except ValueError as e:
            raise ValueError(f'substring "{token}" not found in "{sentence}"') from e
    
        point = start + len(token)
        offsets.append((start, point))
    return offsets

"""
Copy from NLTK
"""
class NLTKWordTokenizer:
    """
    The NLTK tokenizer that has improved upon the TreebankWordTokenizer.

    This is the method that is invoked by ``word_tokenize()``.  It assumes that the
    text has already been segmented into sentences, e.g. using ``sent_tokenize()``.

    The tokenizer is "destructive" such that the regexes applied will munge the
    input string to a state beyond re-construction. It is possible to apply
    `TreebankWordDetokenizer.detokenize` to the tokenized outputs of
    `NLTKDestructiveWordTokenizer.tokenize` but there's no guarantees to
    revert to the original string.
    """

    # Starting quotes.
    STARTING_QUOTES = [
        (re.compile("([«“‘„]|[`]+)", re.U), r" \1 "),
        #(re.compile(r"^\""), r"``"),
        (re.compile(r"(``)"), r" \1 "),
        
        #(re.compile(r"([ \(\[{<])(\"|\'{2})"), r"\1 `` "),
        #(re.compile(r"([ \(\[{<])(\")"), r"\1 \" "),
        (re.compile(r"([ \(\[{<])(\'{2})"), r"\1 '' "),

        (re.compile(r"(?i)(\')(re|ve|ll|m|t|s|d|n)(\w)\b", re.U), r"\1 \2"),
    ]

    # Ending quotes.
    ENDING_QUOTES = [
        (re.compile("([»”’])", re.U), r" \1 "),
        (re.compile(r"''"), " '' "),
        (re.compile(r'"'), " \" "),
        (re.compile(r"([^' ])('[sS]|'[mM]|'[dD]|') "), r"\1 \2 "),
        (re.compile(r"([^' ])('ll|'LL|'re|'RE|'ve|'VE|n't|N'T) "), r"\1 \2 "),
    ]

    # For improvements for starting/closing quotes from TreebankWordTokenizer,
    # see discussion on https://github.com/nltk/nltk/pull/1437
    # Adding to TreebankWordTokenizer, nltk.word_tokenize now splits on
    # - chervon quotes u'\xab' and u'\xbb' .
    # - unicode quotes u'\u2018', u'\u2019', u'\u201c' and u'\u201d'
    # See https://github.com/nltk/nltk/issues/1995#issuecomment-376741608
    # Also, behavior of splitting on clitics now follows Stanford CoreNLP
    # - clitics covered (?!re|ve|ll|m|t|s|d)(\w)\b

    # Punctuation.
    PUNCTUATION = [
        (re.compile(r'([^\.])(\.)([\]\)}>"\'' "»”’ " r"]*)\s*$", re.U), r"\1 \2 \3 "),
        (re.compile(r'([a-zA-Z]+)(\.)([a-zA-Z]+)'), r"\1 \2 \3"),
        (re.compile(r"([:,])([^\d])"), r" \1 \2"),
        (re.compile(r"([:,])$"), r" \1 "),
        (
            re.compile(r"\.{2,}", re.U),
            r" \g<0> ",
        ),  # See https://github.com/nltk/nltk/pull/2322
        (re.compile(r"[;@#$%&]"), r" \g<0> "),
        (
            re.compile(r'([^\.])(\.)([\]\)}>"\']*)\s*$'),
            r"\1 \2\3 ",
        ),  # Handles the final period.
        (re.compile(r"[?!]"), r" \g<0> "),
        (re.compile(r"([^'])' "), r"\1 ' "),
        (
            re.compile(r"[*]", re.U),
            r" \g<0> ",
        ),  # See https://github.com/nltk/nltk/pull/2322
    ]

    # Pads parentheses
    PARENS_BRACKETS = (re.compile(r"[\]\[\(\)\{\}\<\>]"), r" \g<0> ")

    DOUBLE_DASHES = (re.compile(r"--"), r" -- ")

    EMOJIS = (emoji_pattern, r" \1 ")

    def tokenize(self, text: str) -> List[str]:

        for regexp, substitution in self.STARTING_QUOTES:
            text = regexp.sub(substitution, text)

        for regexp, substitution in self.PUNCTUATION:
            text = regexp.sub(substitution, text)

        # Handles parentheses.
        regexp, substitution = self.PARENS_BRACKETS
        text = regexp.sub(substitution, text)

        # Handles emojis
        regexp, substitution = self.EMOJIS
        text = regexp.sub(substitution, text)

        # Handles double dash.
        regexp, substitution = self.DOUBLE_DASHES
        text = regexp.sub(substitution, text)

        # add extra space to make things easier
        text = " " + text + " "

        for regexp, substitution in self.ENDING_QUOTES:
            text = regexp.sub(substitution, text)

        return text.split()

_word_tokenizer = NLTKWordTokenizer()

@lru_cache
def camel_case_normalize(text: str) -> str:
    pattern = re.compile('.+?(?:(?<=[a-z])(?=[A-Z])|(?<=[A-Z])(?=[A-Z][a-z])|$)', re.MULTILINE)
    matches = re.finditer(pattern, text)
    words = [m.group(0) for m in matches]
    return " ".join(words)

@lru_cache(maxsize=None)
def word_tokenize(sentence: str) -> List[str]:
    return _word_tokenizer.tokenize(sentence)

def split_into_short(text: str, ngrams: int=8, split_punctuations: str='!?.'):
    words = word_tokenize(text)
    shorts, buf = [], []
    for word in words:
        buf.append(word)

        if word in split_punctuations or len(buf) >= ngrams:
            # TODO: use original sub-string instead of join
            shorts.append(' '.join(buf))
            buf.clear()
            continue
    
    if buf:
        shorts.append(' '.join(buf))

    return shorts
