from typing import Dict, List, Tuple
from collections import defaultdict
from dataclasses import dataclass

from db_copilot.db_provider.utils import normalize_tokens, word_tokenize

def generate_ngrams(tokens: List[str], sep: str = ' ', max_tokens: int=6) -> List[Tuple[int, int, str]]:
    ngrams = []
    for i in range(len(tokens)):
        for j in range(i, len(tokens)):
            if j - i > max_tokens:
                break
            
            ngram = sep.join(tokens[i:j+1])
            ngrams.append((i, j, ngram))

    return ngrams


@dataclass
class NGramItem:
    # document id
    idx: int
    start: int
    end: int
    length: int
    
    @property
    def score(self) -> float:
        return (self.end - self.start + 1) / self.length

@dataclass
class NGramIndex:
    ngram2items: Dict[str, List[NGramItem]]
    max_ngram_tokens: int
    
    @classmethod
    def from_texts(cls, texts: List[str], max_ngram_tokens: int=5, **kwargs):
        ngram_index: Dict[str, List[NGramItem]] = defaultdict(list)

        for doc_id, text in enumerate(texts):
            tokens = word_tokenize(text)
            tokens = normalize_tokens(tokens, ignore_stopword=True, ignore_punctuation=True)
            if not tokens:
                continue

            ngrams = generate_ngrams(tokens, max_tokens=max_ngram_tokens)
            for i, j, ngram in ngrams:
                # (doc_id, start_idx, end_idx, total_tokens)
                ngram_index[ngram].append(NGramItem(doc_id, i, j, len(tokens)))
        
        for ngram, items in ngram_index.items():
            sorted_items = sorted(items, key=lambda x: x.score, reverse=True)
            ngram_index[ngram] = list(sorted_items)[:200]
        
        return NGramIndex(
            ngram2items=ngram_index,
            max_ngram_tokens=max_ngram_tokens
        )

    def search(self, query: str, top_k: int=None):
        query_tokens = word_tokenize(query)
        query_tokens = normalize_tokens(query_tokens, ignore_stopword=True, ignore_punctuation=True)
        
        matched_results = defaultdict(list)
        for i, j, ngram in generate_ngrams(query_tokens, max_tokens=self.max_ngram_tokens):
            for ngram_item in self.ngram2items.get(ngram, []):
                matched_results[ngram_item.idx].append(ngram_item)
        
        def _aggregate_items(items: List[NGramItem]) -> float:
            num_tokens = items[0].length
            matched_indices = {}
            for item in items:
                for k in range(item.start, item.end + 1):
                    matched_indices[k] = True
            num_matched = len(matched_indices)

            return num_matched / num_tokens

        results = {
            idx: _aggregate_items(items)
            for idx, items in matched_results.items()
        }

        results = list(sorted(results.items(), key=lambda x: x[1], reverse=True))

        if top_k:
            results = results[:top_k]
        
        return results
