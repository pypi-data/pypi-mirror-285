from typing import Iterator, List
from functools import lru_cache
import uuid
import ipaddress
import os
import re
import logging

from .hub_utils import cached_path

MAX_CACHE_SIZE = 1_000_000

def u(s):
    if isinstance(s, bytes):
        return s.decode("ascii")
    return s

_Accent_Map = {
    u('H'): u('h'), # H -> h
    u('I'): u('i'), # I -> i
    u('J'): u('j'), # J -> j
    u('N'): u('n'), # N -> n
    u('P'): u('p'), # P -> p
    u('S'): u('s'), # S -> s
    u('T'): u('t'), # T -> t
    u('W'): u('w'), # W -> w
    u('Y'): u('y'), # Y -> y
    u('i'): u('i'), # i -> i
    u('n'): u('n'), # n -> n
    u('p'): u('p'), # p -> p
    u('s'): u('s'), # s -> s
    u('\xc0'): u('a'), # À -> a
    u('\xc1'): u('a'), # Á -> a
    u('\xc2'): u('a'), # Â -> a
    u('\xc3'): u('a'), # Ã -> a
    u('\xc4'): u('a'), # Ä -> a
    u('\xc5'): u('a'), # Å -> a
    u('\xc7'): u('c'), # Ç -> c
    u('\xc8'): u('e'), # È -> e
    u('\xc9'): u('e'), # É -> e
    u('\xca'): u('e'), # Ê -> e
    u('\xcb'): u('e'), # Ë -> e
    u('\xcc'): u('i'), # Ì -> i
    u('\xcd'): u('i'), # Í -> i
    u('\xce'): u('i'), # Î -> i
    u('\xcf'): u('i'), # Ï -> i
    u('\xd1'): u('n'), # Ñ -> n
    u('\xd2'): u('o'), # Ò -> o
    u('\xd3'): u('o'), # Ó -> o
    u('\xd4'): u('o'), # Ô -> o
    u('\xd5'): u('o'), # Õ -> o
    u('\xd6'): u('o'), # Ö -> o
    u('\xd8'): u('o'), # Ø -> o
    u('\xd9'): u('u'), # Ù -> u
    u('\xda'): u('u'), # Ú -> u
    u('\xdb'): u('u'), # Û -> u
    u('\xdc'): u('u'), # Ü -> u
    u('\xdd'): u('y'), # Ý -> y
    u('\xde'): u('t'), # Þ -> t
    u('\xdf'): u('s'), # ß -> s
    u('\xe0'): u('a'), # à -> a
    u('\xe1'): u('a'), # á -> a
    u('\xe2'): u('a'), # â -> a
    u('\xe3'): u('a'), # ã -> a
    u('\xe4'): u('a'), # ä -> a
    u('\xe5'): u('a'), # å -> a
    u('\xe7'): u('c'), # ç -> c
    u('\xe8'): u('e'), # è -> e
    u('\xe9'): u('e'), # é -> e
    u('\xea'): u('e'), # ê -> e
    u('\xeb'): u('e'), # ë -> e
    u('\xec'): u('i'), # ì -> i
    u('\xed'): u('i'), # í -> i
    u('\xee'): u('i'), # î -> i
    u('\xef'): u('i'), # ï -> i
    u('\xf0'): u('d'), # ð -> d
    u('\xf1'): u('n'), # ñ -> n
    u('\xf2'): u('o'), # ò -> o
    u('\xf3'): u('o'), # ó -> o
    u('\xf4'): u('o'), # ô -> o
    u('\xf5'): u('o'), # õ -> o
    u('\xf6'): u('o'), # ö -> o
    u('\xf8'): u('o'), # ø -> o
    u('\xf9'): u('u'), # ù -> u
    u('\xfa'): u('u'), # ú -> u
    u('\xfb'): u('u'), # û -> u
    u('\xfc'): u('u'), # ü -> u
    u('\xfd'): u('y'), # ý -> y
    u('\xfe'): u('t'), # þ -> t
    u('\xff'): u('y'), # ÿ -> y
    u('\u0100'): u('a'), # Ā -> a
    u('\u0101'): u('a'), # ā -> a
    u('\u0102'): u('a'), # Ă -> a
    u('\u0103'): u('a'), # ă -> a
    u('\u0104'): u('a'), # Ą -> a
    u('\u0105'): u('a'), # ą -> a
    u('\u0106'): u('c'), # Ć -> c
    u('\u0107'): u('c'), # ć -> c
    u('\u0108'): u('c'), # Ĉ -> c
    u('\u0109'): u('c'), # ĉ -> c
    u('\u010a'): u('c'), # Ċ -> c
    u('\u010b'): u('c'), # ċ -> c
    u('\u010c'): u('c'), # Č -> c
    u('\u010d'): u('c'), # č -> c
    u('\u010e'): u('d'), # Ď -> d
    u('\u010f'): u('d'), # ď -> d
    u('\u0110'): u('d'), # Đ -> d
    u('\u0111'): u('d'), # đ -> d
    u('\u0112'): u('e'), # Ē -> e
    u('\u0113'): u('e'), # ē -> e
    u('\u0114'): u('e'), # Ĕ -> e
    u('\u0115'): u('e'), # ĕ -> e
    u('\u0116'): u('e'), # Ė -> e
    u('\u0117'): u('e'), # ė -> e
    u('\u0118'): u('e'), # Ę -> e
    u('\u0119'): u('e'), # ę -> e
    u('\u011a'): u('e'), # Ě -> e
    u('\u011b'): u('e'), # ě -> e
    u('\u011c'): u('g'), # Ĝ -> g
    u('\u011d'): u('g'), # ĝ -> g
    u('\u011e'): u('g'), # Ğ -> g
    u('\u011f'): u('g'), # ğ -> g
    u('\u0120'): u('g'), # Ġ -> g
    u('\u0121'): u('g'), # ġ -> g
    u('\u0122'): u('g'), # Ģ -> g
    u('\u0123'): u('g'), # ģ -> g
    u('\u0124'): u('h'), # Ĥ -> h
    u('\u0125'): u('h'), # ĥ -> h
    u('\u0126'): u('h'), # Ħ -> h
    u('\u0127'): u('h'), # ħ -> h
    u('\u0128'): u('i'), # Ĩ -> i
    u('\u0129'): u('i'), # ĩ -> i
    u('\u012a'): u('i'), # Ī -> i
    u('\u012b'): u('i'), # ī -> i
    u('\u012c'): u('i'), # Ĭ -> i
    u('\u012d'): u('i'), # ĭ -> i
    u('\u012e'): u('i'), # Į -> i
    u('\u012f'): u('i'), # į -> i
    u('\u0130'): u('i'), # İ -> i
    u('\u0131'): u('i'), # ı -> i
    u('\u0134'): u('j'), # Ĵ -> j
    u('\u0135'): u('j'), # ĵ -> j
    u('\u0136'): u('k'), # Ķ -> k
    u('\u0137'): u('k'), # ķ -> k
    u('\u0139'): u('a'), # Ĺ -> a
    u('\u013a'): u('l'), # ĺ -> l
    u('\u013b'): u('l'), # Ļ -> l
    u('\u013c'): u('l'), # ļ -> l
    u('\u013d'): u('l'), # Ľ -> l
    u('\u013e'): u('l'), # ľ -> l
    u('\u013f'): u('l'), # Ŀ -> l
    u('\u0140'): u('l'), # ŀ -> l
    u('\u0141'): u('l'), # Ł -> l
    u('\u0142'): u('l'), # ł -> l
    u('\u0143'): u('n'), # Ń -> n
    u('\u0144'): u('n'), # ń -> n
    u('\u0145'): u('n'), # Ņ -> n
    u('\u0146'): u('n'), # ņ -> n
    u('\u0147'): u('n'), # Ň -> n
    u('\u0148'): u('n'), # ň -> n
    u('\u014c'): u('o'), # Ō -> o
    u('\u014d'): u('o'), # ō -> o
    u('\u014e'): u('o'), # Ŏ -> o
    u('\u014f'): u('o'), # ŏ -> o
    u('\u0150'): u('o'), # Ő -> o
    u('\u0151'): u('o'), # ő -> o
    u('\u0154'): u('r'), # Ŕ -> r
    u('\u0155'): u('r'), # ŕ -> r
    u('\u0156'): u('r'), # Ŗ -> r
    u('\u0157'): u('r'), # ŗ -> r
    u('\u0158'): u('r'), # Ř -> r
    u('\u0159'): u('r'), # ř -> r
    u('\u015a'): u('s'), # Ś -> s
    u('\u015b'): u('s'), # ś -> s
    u('\u015c'): u('s'), # Ŝ -> s
    u('\u015d'): u('s'), # ŝ -> s
    u('\u015e'): u('s'), # Ş -> s
    u('\u015f'): u('s'), # ş -> s
    u('\u0160'): u('s'), # Š -> s
    u('\u0161'): u('s'), # š -> s
    u('\u0162'): u('t'), # Ţ -> t
    u('\u0163'): u('t'), # ţ -> t
    u('\u0164'): u('t'), # Ť -> t
    u('\u0165'): u('t'), # ť -> t
    u('\u0166'): u('t'), # Ŧ -> t
    u('\u0167'): u('t'), # ŧ -> t
    u('\u0168'): u('u'), # Ũ -> u
    u('\u0169'): u('u'), # ũ -> u
    u('\u016a'): u('u'), # Ū -> u
    u('\u016b'): u('u'), # ū -> u
    u('\u016c'): u('u'), # Ŭ -> u
    u('\u016d'): u('u'), # ŭ -> u
    u('\u016e'): u('u'), # Ů -> u
    u('\u016f'): u('u'), # ů -> u
    u('\u0170'): u('u'), # Ű -> u
    u('\u0171'): u('u'), # ű -> u
    u('\u0172'): u('u'), # Ų -> u
    u('\u0173'): u('u'), # ų -> u
    u('\u0174'): u('w'), # Ŵ -> w
    u('\u0175'): u('w'), # ŵ -> w
    u('\u0176'): u('y'), # Ŷ -> y
    u('\u0177'): u('y'), # ŷ -> y
    u('\u0178'): u('y'), # Ÿ -> y
    u('\u0179'): u('z'), # Ź -> z
    u('\u017a'): u('z'), # ź -> z
    u('\u017b'): u('z'), # Ż -> z
    u('\u017c'): u('z'), # ż -> z
    u('\u017d'): u('z'), # Ž -> z
    u('\u017e'): u('z'), # ž -> z
    u('\u0180'): u('b'), # ƀ -> b
    u('\u0181'): u('b'), # Ɓ -> b
    u('\u0182'): u('b'), # Ƃ -> b
    u('\u0183'): u('b'), # ƃ -> b
    u('\u0187'): u('c'), # Ƈ -> c
    u('\u0188'): u('c'), # ƈ -> c
    u('\u0189'): u('d'), # Ɖ -> d
    u('\u018a'): u('d'), # Ɗ -> d
    u('\u018b'): u('d'), # Ƌ -> d
    u('\u018c'): u('d'), # ƌ -> d
    u('\u018e'): u('e'), # Ǝ -> e
    u('\u018f'): u('e'), # Ə -> e
    u('\u0191'): u('f'), # Ƒ -> f
    u('\u0192'): u('f'), # ƒ -> f
    u('\u0193'): u('g'), # Ɠ -> g
    u('\u0197'): u('i'), # Ɨ -> i
    u('\u0198'): u('k'), # Ƙ -> k
    u('\u0199'): u('k'), # ƙ -> k
    u('\u019a'): u('l'), # ƚ -> l
    u('\u019d'): u('n'), # Ɲ -> n
    u('\u019e'): u('n'), # ƞ -> n
    u('\u019f'): u('o'), # Ɵ -> o
    u('\u01a0'): u('o'), # Ơ -> o
    u('\u01a1'): u('o'), # ơ -> o
    u('\u01a4'): u('p'), # Ƥ -> p
    u('\u01a5'): u('p'), # ƥ -> p
    u('\u01ab'): u('t'), # ƫ -> t
    u('\u01ac'): u('t'), # Ƭ -> t
    u('\u01ad'): u('t'), # ƭ -> t
    u('\u01ae'): u('t'), # Ʈ -> t
    u('\u01af'): u('u'), # Ư -> u
    u('\u01b0'): u('u'), # ư -> u
    u('\u01b2'): u('v'), # Ʋ -> v
    u('\u01b3'): u('y'), # Ƴ -> y
    u('\u01b4'): u('y'), # ƴ -> y
    u('\u01b5'): u('z'), # Ƶ -> z
    u('\u01b6'): u('z'), # ƶ -> z
    u('\u01ba'): u('z'), # ƺ -> z
    u('\u01cd'): u('a'), # Ǎ -> a
    u('\u01ce'): u('a'), # ǎ -> a
    u('\u01cf'): u('i'), # Ǐ -> i
    u('\u01d0'): u('i'), # ǐ -> i
    u('\u01d1'): u('o'), # Ǒ -> o
    u('\u01d2'): u('o'), # ǒ -> o
    u('\u01d3'): u('u'), # Ǔ -> u
    u('\u01d4'): u('u'), # ǔ -> u
    u('\u01d5'): u('u'), # Ǖ -> u
    u('\u01d6'): u('u'), # ǖ -> u
    u('\u01d7'): u('u'), # Ǘ -> u
    u('\u01d8'): u('u'), # ǘ -> u
    u('\u01d9'): u('u'), # Ǚ -> u
    u('\u01da'): u('u'), # ǚ -> u
    u('\u01db'): u('u'), # Ǜ -> u
    u('\u01dc'): u('u'), # ǜ -> u
    u('\u01dd'): u('e'), # ǝ -> e
    u('\u01de'): u('a'), # Ǟ -> a
    u('\u01df'): u('a'), # ǟ -> a
    u('\u01e0'): u('a'), # Ǡ -> a
    u('\u01e1'): u('a'), # ǡ -> a
    u('\u01e2'): u('a'), # Ǣ -> a
    u('\u01e3'): u('a'), # ǣ -> a
    u('\u01e4'): u('g'), # Ǥ -> g
    u('\u01e5'): u('g'), # ǥ -> g
    u('\u01e6'): u('g'), # Ǧ -> g
    u('\u01e7'): u('g'), # ǧ -> g
    u('\u01e8'): u('k'), # Ǩ -> k
    u('\u01e9'): u('k'), # ǩ -> k
    u('\u01ea'): u('o'), # Ǫ -> o
    u('\u01eb'): u('o'), # ǫ -> o
    u('\u01ec'): u('o'), # Ǭ -> o
    u('\u01ed'): u('o'), # ǭ -> o
    u('\u01ee'): u('z'), # Ǯ -> z
    u('\u01ef'): u('z'), # ǯ -> z
    u('\u01f0'): u('j'), # ǰ -> j
    u('\u01f4'): u('g'), # Ǵ -> g
    u('\u01f5'): u('g'), # ǵ -> g
    u('\u01f8'): u('n'), # Ǹ -> n
    u('\u01f9'): u('n'), # ǹ -> n
    u('\u01fa'): u('a'), # Ǻ -> a
    u('\u01fb'): u('a'), # ǻ -> a
    u('\u01fc'): u('a'), # Ǽ -> a
    u('\u01fd'): u('a'), # ǽ -> a
    u('\u01fe'): u('o'), # Ǿ -> o
    u('\u01ff'): u('o'), # ǿ -> o
    u('\u0200'): u('a'), # Ȁ -> a
    u('\u0201'): u('a'), # ȁ -> a
    u('\u0202'): u('a'), # Ȃ -> a
    u('\u0203'): u('a'), # ȃ -> a
    u('\u0204'): u('e'), # Ȅ -> e
    u('\u0205'): u('e'), # ȅ -> e
    u('\u0206'): u('e'), # Ȇ -> e
    u('\u0207'): u('e'), # ȇ -> e
    u('\u0208'): u('i'), # Ȉ -> i
    u('\u0209'): u('i'), # ȉ -> i
    u('\u020a'): u('i'), # Ȋ -> i
    u('\u020b'): u('i'), # ȋ -> i
    u('\u020c'): u('o'), # Ȍ -> o
    u('\u020d'): u('o'), # ȍ -> o
    u('\u020e'): u('o'), # Ȏ -> o
    u('\u020f'): u('o'), # ȏ -> o
    u('\u0210'): u('r'), # Ȑ -> r
    u('\u0211'): u('r'), # ȑ -> r
    u('\u0212'): u('r'), # Ȓ -> r
    u('\u0213'): u('r'), # ȓ -> r
    u('\u0214'): u('u'), # Ȕ -> u
    u('\u0215'): u('u'), # ȕ -> u
    u('\u0216'): u('u'), # Ȗ -> u
    u('\u0217'): u('u'), # ȗ -> u
    u('\u0218'): u('s'), # Ș -> s
    u('\u0219'): u('s'), # ș -> s
    u('\u021a'): u('t'), # Ț -> t
    u('\u021b'): u('t'), # ț -> t
    u('\u021e'): u('h'), # Ȟ -> h
    u('\u021f'): u('h'), # ȟ -> h
    u('\u0220'): u('n'), # Ƞ -> n
    u('\u0221'): u('d'), # ȡ -> d
    u('\u0224'): u('z'), # Ȥ -> z
    u('\u0225'): u('z'), # ȥ -> z
    u('\u0226'): u('a'), # Ȧ -> a
    u('\u0227'): u('a'), # ȧ -> a
    u('\u0228'): u('e'), # Ȩ -> e
    u('\u0229'): u('e'), # ȩ -> e
    u('\u022a'): u('o'), # Ȫ -> o
    u('\u022b'): u('o'), # ȫ -> o
    u('\u022c'): u('o'), # Ȭ -> o
    u('\u022d'): u('o'), # ȭ -> o
    u('\u022e'): u('o'), # Ȯ -> o
    u('\u022f'): u('o'), # ȯ -> o
    u('\u0230'): u('o'), # Ȱ -> o
    u('\u0231'): u('o'), # ȱ -> o
    u('\u0232'): u('y'), # Ȳ -> y
    u('\u0233'): u('y'), # ȳ -> y
    u('\u0234'): u('l'), # ȴ -> l
    u('\u0235'): u('n'), # ȵ -> n
    u('\u0236'): u('t'), # ȶ -> t
    u('\u0237'): u('j'), # ȷ -> j
    u('\u023a'): u('a'), # Ⱥ -> a
    u('\u023b'): u('c'), # Ȼ -> c
    u('\u023c'): u('c'), # ȼ -> c
    u('\u023d'): u('l'), # Ƚ -> l
    u('\u023e'): u('t'), # Ⱦ -> t
    u('\u0243'): u('b'), # Ƀ -> b
    u('\u0244'): u('u'), # Ʉ -> u
    u('\u0246'): u('e'), # Ɇ -> e
    u('\u0247'): u('e'), # ɇ -> e
    u('\u0248'): u('j'), # Ɉ -> j
    u('\u0249'): u('j'), # ɉ -> j
    u('\u024a'): u('q'), # Ɋ -> q
    u('\u024b'): u('q'), # ɋ -> q
    u('\u024c'): u('r'), # Ɍ -> r
    u('\u024d'): u('r'), # ɍ -> r
    u('\u024e'): u('y'), # Ɏ -> y
    u('\u024f'): u('y'), # ɏ -> y
    u('\u0253'): u('b'), # ɓ -> b
    u('\u0255'): u('c'), # ɕ -> c
    u('\u0256'): u('d'), # ɖ -> d
    u('\u0257'): u('d'), # ɗ -> d
    u('\u025a'): u('e'), # ɚ -> e
    u('\u025d'): u('e'), # ɝ -> e
    u('\u025f'): u('j'), # ɟ -> j
    u('\u0260'): u('g'), # ɠ -> g
    u('\u0268'): u('i'), # ɨ -> i
    u('\u026b'): u('l'), # ɫ -> l
    u('\u026c'): u('l'), # ɬ -> l
    u('\u026d'): u('l'), # ɭ -> l
    u('\u0271'): u('m'), # ɱ -> m
    u('\u0272'): u('n'), # ɲ -> n
    u('\u0273'): u('n'), # ɳ -> n
    u('\u0275'): u('o'), # ɵ -> o
    u('\u027c'): u('r'), # ɼ -> r
    u('\u027d'): u('r'), # ɽ -> r
    u('\u027e'): u('r'), # ɾ -> r
    u('\u0282'): u('s'), # ʂ -> s
    u('\u0284'): u('j'), # ʄ -> j
    u('\u0288'): u('t'), # ʈ -> t
    u('\u0289'): u('u'), # ʉ -> u
    u('\u028b'): u('v'), # ʋ -> v
    u('\u028f'): u('y'), # ʏ -> y
    u('\u0290'): u('z'), # ʐ -> z
    u('\u0291'): u('z'), # ʑ -> z
    u('\u029d'): u('j'), # ʝ -> j
    u('\u02a0'): u('q'), # ʠ -> q
    u('\u0303'): u('p'), # ̃ -> p
    u('\u0308'): u('t'), # ̈ -> t
    u('\u030a'): u('y'), # ̊ -> y
    u('\u030c'): u('j'), # ̌ -> j
    u('\u0323'): u('l'), # ̣ -> l
    u('\u0329'): u('s'), # ̩ -> s
    u('\u0331'): u('h'), # ̱ -> h
    u('\u1d6c'): u('b'), # ᵬ -> b
    u('\u1d6d'): u('d'), # ᵭ -> d
    u('\u1d6e'): u('f'), # ᵮ -> f
    u('\u1d72'): u('r'), # ᵲ -> r
    u('\u1d73'): u('r'), # ᵳ -> r
    u('\u1d75'): u('t'), # ᵵ -> t
    u('\u1e00'): u('a'), # Ḁ -> a
    u('\u1e01'): u('a'), # ḁ -> a
    u('\u1e02'): u('b'), # Ḃ -> b
    u('\u1e03'): u('b'), # ḃ -> b
    u('\u1e04'): u('b'), # Ḅ -> b
    u('\u1e05'): u('b'), # ḅ -> b
    u('\u1e06'): u('b'), # Ḇ -> b
    u('\u1e07'): u('b'), # ḇ -> b
    u('\u1e08'): u('c'), # Ḉ -> c
    u('\u1e09'): u('c'), # ḉ -> c
    u('\u1e0a'): u('d'), # Ḋ -> d
    u('\u1e0b'): u('d'), # ḋ -> d
    u('\u1e0c'): u('d'), # Ḍ -> d
    u('\u1e0d'): u('d'), # ḍ -> d
    u('\u1e0e'): u('d'), # Ḏ -> d
    u('\u1e0f'): u('d'), # ḏ -> d
    u('\u1e10'): u('d'), # Ḑ -> d
    u('\u1e11'): u('d'), # ḑ -> d
    u('\u1e12'): u('d'), # Ḓ -> d
    u('\u1e13'): u('d'), # ḓ -> d
    u('\u1e14'): u('e'), # Ḕ -> e
    u('\u1e15'): u('e'), # ḕ -> e
    u('\u1e16'): u('e'), # Ḗ -> e
    u('\u1e17'): u('e'), # ḗ -> e
    u('\u1e18'): u('e'), # Ḙ -> e
    u('\u1e19'): u('e'), # ḙ -> e
    u('\u1e1a'): u('e'), # Ḛ -> e
    u('\u1e1b'): u('e'), # ḛ -> e
    u('\u1e1c'): u('e'), # Ḝ -> e
    u('\u1e1d'): u('e'), # ḝ -> e
    u('\u1e1e'): u('f'), # Ḟ -> f
    u('\u1e1f'): u('f'), # ḟ -> f
    u('\u1e20'): u('g'), # Ḡ -> g
    u('\u1e21'): u('g'), # ḡ -> g
    u('\u1e22'): u('h'), # Ḣ -> h
    u('\u1e23'): u('h'), # ḣ -> h
    u('\u1e24'): u('h'), # Ḥ -> h
    u('\u1e25'): u('h'), # ḥ -> h
    u('\u1e26'): u('h'), # Ḧ -> h
    u('\u1e27'): u('h'), # ḧ -> h
    u('\u1e28'): u('h'), # Ḩ -> h
    u('\u1e29'): u('h'), # ḩ -> h
    u('\u1e2a'): u('h'), # Ḫ -> h
    u('\u1e2b'): u('h'), # ḫ -> h
    u('\u1e2c'): u('i'), # Ḭ -> i
    u('\u1e2d'): u('i'), # ḭ -> i
    u('\u1e2e'): u('i'), # Ḯ -> i
    u('\u1e2f'): u('i'), # ḯ -> i
    u('\u1e30'): u('k'), # Ḱ -> k
    u('\u1e31'): u('k'), # ḱ -> k
    u('\u1e32'): u('k'), # Ḳ -> k
    u('\u1e33'): u('k'), # ḳ -> k
    u('\u1e34'): u('k'), # Ḵ -> k
    u('\u1e35'): u('k'), # ḵ -> k
    u('\u1e36'): u('l'), # Ḷ -> l
    u('\u1e37'): u('l'), # ḷ -> l
    u('\u1e38'): u('l'), # Ḹ -> l
    u('\u1e39'): u('l'), # ḹ -> l
    u('\u1e3a'): u('l'), # Ḻ -> l
    u('\u1e3b'): u('l'), # ḻ -> l
    u('\u1e3c'): u('l'), # Ḽ -> l
    u('\u1e3d'): u('l'), # ḽ -> l
    u('\u1e3e'): u('m'), # Ḿ -> m
    u('\u1e3f'): u('m'), # ḿ -> m
    u('\u1e40'): u('m'), # Ṁ -> m
    u('\u1e41'): u('m'), # ṁ -> m
    u('\u1e42'): u('m'), # Ṃ -> m
    u('\u1e43'): u('m'), # ṃ -> m
    u('\u1e44'): u('n'), # Ṅ -> n
    u('\u1e45'): u('n'), # ṅ -> n
    u('\u1e46'): u('n'), # Ṇ -> n
    u('\u1e47'): u('n'), # ṇ -> n
    u('\u1e48'): u('n'), # Ṉ -> n
    u('\u1e49'): u('n'), # ṉ -> n
    u('\u1e4a'): u('n'), # Ṋ -> n
    u('\u1e4b'): u('n'), # ṋ -> n
    u('\u1e4c'): u('o'), # Ṍ -> o
    u('\u1e4d'): u('o'), # ṍ -> o
    u('\u1e4e'): u('o'), # Ṏ -> o
    u('\u1e4f'): u('o'), # ṏ -> o
    u('\u1e50'): u('o'), # Ṑ -> o
    u('\u1e51'): u('o'), # ṑ -> o
    u('\u1e52'): u('o'), # Ṓ -> o
    u('\u1e53'): u('o'), # ṓ -> o
    u('\u1e54'): u('p'), # Ṕ -> p
    u('\u1e55'): u('p'), # ṕ -> p
    u('\u1e56'): u('p'), # Ṗ -> p
    u('\u1e57'): u('p'), # ṗ -> p
    u('\u1e58'): u('r'), # Ṙ -> r
    u('\u1e59'): u('r'), # ṙ -> r
    u('\u1e5a'): u('r'), # Ṛ -> r
    u('\u1e5b'): u('r'), # ṛ -> r
    u('\u1e5c'): u('r'), # Ṝ -> r
    u('\u1e5d'): u('r'), # ṝ -> r
    u('\u1e5e'): u('r'), # Ṟ -> r
    u('\u1e5f'): u('r'), # ṟ -> r
    u('\u1e60'): u('s'), # Ṡ -> s
    u('\u1e61'): u('s'), # ṡ -> s
    u('\u1e62'): u('s'), # Ṣ -> s
    u('\u1e63'): u('s'), # ṣ -> s
    u('\u1e64'): u('s'), # Ṥ -> s
    u('\u1e65'): u('s'), # ṥ -> s
    u('\u1e66'): u('s'), # Ṧ -> s
    u('\u1e67'): u('s'), # ṧ -> s
    u('\u1e68'): u('s'), # Ṩ -> s
    u('\u1e69'): u('s'), # ṩ -> s
    u('\u1e6a'): u('t'), # Ṫ -> t
    u('\u1e6b'): u('t'), # ṫ -> t
    u('\u1e6c'): u('t'), # Ṭ -> t
    u('\u1e6d'): u('t'), # ṭ -> t
    u('\u1e6e'): u('t'), # Ṯ -> t
    u('\u1e6f'): u('t'), # ṯ -> t
    u('\u1e70'): u('t'), # Ṱ -> t
    u('\u1e71'): u('t'), # ṱ -> t
    u('\u1e72'): u('u'), # Ṳ -> u
    u('\u1e73'): u('u'), # ṳ -> u
    u('\u1e74'): u('u'), # Ṵ -> u
    u('\u1e75'): u('u'), # ṵ -> u
    u('\u1e76'): u('u'), # Ṷ -> u
    u('\u1e77'): u('u'), # ṷ -> u
    u('\u1e78'): u('u'), # Ṹ -> u
    u('\u1e79'): u('u'), # ṹ -> u
    u('\u1e7a'): u('u'), # Ṻ -> u
    u('\u1e7b'): u('u'), # ṻ -> u
    u('\u1e7c'): u('v'), # Ṽ -> v
    u('\u1e7d'): u('v'), # ṽ -> v
    u('\u1e7e'): u('v'), # Ṿ -> v
    u('\u1e7f'): u('v'), # ṿ -> v
    u('\u1e80'): u('w'), # Ẁ -> w
    u('\u1e81'): u('w'), # ẁ -> w
    u('\u1e82'): u('w'), # Ẃ -> w
    u('\u1e83'): u('w'), # ẃ -> w
    u('\u1e84'): u('w'), # Ẅ -> w
    u('\u1e85'): u('w'), # ẅ -> w
    u('\u1e86'): u('w'), # Ẇ -> w
    u('\u1e87'): u('w'), # ẇ -> w
    u('\u1e88'): u('w'), # Ẉ -> w
    u('\u1e89'): u('w'), # ẉ -> w
    u('\u1e8a'): u('x'), # Ẋ -> x
    u('\u1e8b'): u('x'), # ẋ -> x
    u('\u1e8c'): u('x'), # Ẍ -> x
    u('\u1e8d'): u('x'), # ẍ -> x
    u('\u1e8e'): u('y'), # Ẏ -> y
    u('\u1e8f'): u('y'), # ẏ -> y
    u('\u1e90'): u('z'), # Ẑ -> z
    u('\u1e91'): u('z'), # ẑ -> z
    u('\u1e92'): u('z'), # Ẓ -> z
    u('\u1e93'): u('z'), # ẓ -> z
    u('\u1e94'): u('z'), # Ẕ -> z
    u('\u1e95'): u('z'), # ẕ -> z
    u('\u1e96'): u('h'), # ẖ -> h
    u('\u1e97'): u('t'), # ẗ -> t
    u('\u1e98'): u('w'), # ẘ -> w
    u('\u1e99'): u('y'), # ẙ -> y
    u('\u1e9a'): u('a'), # ẚ -> a
    u('\u1e9b'): u('s'), # ẛ -> s
    u('\u1ea0'): u('a'), # Ạ -> a
    u('\u1ea1'): u('a'), # ạ -> a
    u('\u1ea2'): u('a'), # Ả -> a
    u('\u1ea3'): u('a'), # ả -> a
    u('\u1ea4'): u('a'), # Ấ -> a
    u('\u1ea5'): u('a'), # ấ -> a
    u('\u1ea6'): u('a'), # Ầ -> a
    u('\u1ea7'): u('a'), # ầ -> a
    u('\u1ea8'): u('a'), # Ẩ -> a
    u('\u1ea9'): u('a'), # ẩ -> a
    u('\u1eaa'): u('a'), # Ẫ -> a
    u('\u1eab'): u('a'), # ẫ -> a
    u('\u1eac'): u('a'), # Ậ -> a
    u('\u1ead'): u('a'), # ậ -> a
    u('\u1eae'): u('a'), # Ắ -> a
    u('\u1eaf'): u('a'), # ắ -> a
    u('\u1eb0'): u('a'), # Ằ -> a
    u('\u1eb1'): u('a'), # ằ -> a
    u('\u1eb2'): u('a'), # Ẳ -> a
    u('\u1eb3'): u('a'), # ẳ -> a
    u('\u1eb4'): u('a'), # Ẵ -> a
    u('\u1eb5'): u('a'), # ẵ -> a
    u('\u1eb6'): u('a'), # Ặ -> a
    u('\u1eb7'): u('a'), # ặ -> a
    u('\u1eb8'): u('e'), # Ẹ -> e
    u('\u1eb9'): u('e'), # ẹ -> e
    u('\u1eba'): u('e'), # Ẻ -> e
    u('\u1ebb'): u('e'), # ẻ -> e
    u('\u1ebc'): u('e'), # Ẽ -> e
    u('\u1ebd'): u('e'), # ẽ -> e
    u('\u1ebe'): u('e'), # Ế -> e
    u('\u1ebf'): u('e'), # ế -> e
    u('\u1ec0'): u('e'), # Ề -> e
    u('\u1ec1'): u('e'), # ề -> e
    u('\u1ec2'): u('e'), # Ể -> e
    u('\u1ec3'): u('e'), # ể -> e
    u('\u1ec4'): u('e'), # Ễ -> e
    u('\u1ec5'): u('e'), # ễ -> e
    u('\u1ec6'): u('e'), # Ệ -> e
    u('\u1ec7'): u('e'), # ệ -> e
    u('\u1ec8'): u('i'), # Ỉ -> i
    u('\u1ec9'): u('i'), # ỉ -> i
    u('\u1eca'): u('i'), # Ị -> i
    u('\u1ecb'): u('i'), # ị -> i
    u('\u1ecc'): u('o'), # Ọ -> o
    u('\u1ecd'): u('o'), # ọ -> o
    u('\u1ece'): u('o'), # Ỏ -> o
    u('\u1ecf'): u('o'), # ỏ -> o
    u('\u1ed0'): u('o'), # Ố -> o
    u('\u1ed1'): u('o'), # ố -> o
    u('\u1ed2'): u('o'), # Ồ -> o
    u('\u1ed3'): u('o'), # ồ -> o
    u('\u1ed4'): u('o'), # Ổ -> o
    u('\u1ed5'): u('o'), # ổ -> o
    u('\u1ed6'): u('o'), # Ỗ -> o
    u('\u1ed7'): u('o'), # ỗ -> o
    u('\u1ed8'): u('o'), # Ộ -> o
    u('\u1ed9'): u('o'), # ộ -> o
    u('\u1eda'): u('o'), # Ớ -> o
    u('\u1edb'): u('o'), # ớ -> o
    u('\u1edc'): u('o'), # Ờ -> o
    u('\u1edd'): u('o'), # ờ -> o
    u('\u1ede'): u('o'), # Ở -> o
    u('\u1edf'): u('o'), # ở -> o
    u('\u1ee0'): u('o'), # Ỡ -> o
    u('\u1ee1'): u('o'), # ỡ -> o
    u('\u1ee2'): u('o'), # Ợ -> o
    u('\u1ee3'): u('o'), # ợ -> o
    u('\u1ee4'): u('u'), # Ụ -> u
    u('\u1ee5'): u('u'), # ụ -> u
    u('\u1ee6'): u('u'), # Ủ -> u
    u('\u1ee7'): u('u'), # ủ -> u
    u('\u1ee8'): u('u'), # Ứ -> u
    u('\u1ee9'): u('u'), # ứ -> u
    u('\u1eea'): u('u'), # Ừ -> u
    u('\u1eeb'): u('u'), # ừ -> u
    u('\u1eec'): u('u'), # Ử -> u
    u('\u1eed'): u('u'), # ử -> u
    u('\u1eee'): u('u'), # Ữ -> u
    u('\u1eef'): u('u'), # ữ -> u
    u('\u1ef0'): u('u'), # Ự -> u
    u('\u1ef1'): u('u'), # ự -> u
    u('\u1ef2'): u('y'), # Ỳ -> y
    u('\u1ef3'): u('y'), # ỳ -> y
    u('\u1ef4'): u('y'), # Ỵ -> y
    u('\u1ef5'): u('y'), # ỵ -> y
    u('\u1ef6'): u('y'), # Ỷ -> y
    u('\u1ef7'): u('y'), # ỷ -> y
    u('\u1ef8'): u('y'), # Ỹ -> y
    u('\u1ef9'): u('y'), # ỹ -> y
    u('\u2c60'): u('l'), # Ⱡ -> l
    u('\u2c61'): u('l'), # ⱡ -> l
    u('\u2c62'): u('l'), # Ɫ -> l
    u('\u2c63'): u('p'), # Ᵽ -> p
    u('\u2c64'): u('r'), # Ɽ -> r
    u('\u2c65'): u('a'), # ⱥ -> a
    u('\u2c66'): u('t'), # ⱦ -> t
    u('\u2c67'): u('h'), # Ⱨ -> h
    u('\u2c68'): u('h'), # ⱨ -> h
    u('\u2c69'): u('k'), # Ⱪ -> k
    u('\u2c6a'): u('k'), # ⱪ -> k
    u('\u2c6b'): u('z'), # Ⱬ -> z
    u('\u2c6c'): u('z'), # ⱬ -> z
    u('\uff10'): u('0'), # ０ -> 0
    u('\uff11'): u('1'), # １ -> 1
    u('\uff12'): u('2'), # ２ -> 2
    u('\uff13'): u('3'), # ３ -> 3
    u('\uff14'): u('4'), # ４ -> 4
    u('\uff15'): u('5'), # ５ -> 5
    u('\uff16'): u('6'), # ６ -> 6
    u('\uff17'): u('7'), # ７ -> 7
    u('\uff18'): u('8'), # ８ -> 8
    u('\uff19'): u('9'), # ９ -> 9
    u('\uff21'): u('A'), # Ａ -> A
    u('\uff22'): u('B'), # Ｂ -> B
    u('\uff23'): u('C'), # Ｃ -> C
    u('\uff24'): u('D'), # Ｄ -> D
    u('\uff25'): u('E'), # Ｅ -> E
    u('\uff26'): u('F'), # Ｆ -> F
    u('\uff27'): u('G'), # Ｇ -> G
    u('\uff28'): u('H'), # Ｈ -> H
    u('\uff29'): u('I'), # Ｉ -> I
    u('\uff2a'): u('J'), # Ｊ -> J
    u('\uff2b'): u('K'), # Ｋ -> K
    u('\uff2c'): u('L'), # Ｌ -> L
    u('\uff2d'): u('M'), # Ｍ -> M
    u('\uff2e'): u('N'), # Ｎ -> N
    u('\uff2f'): u('O'), # Ｏ -> O
    u('\uff30'): u('P'), # Ｐ -> P
    u('\uff31'): u('Q'), # Ｑ -> Q
    u('\uff32'): u('R'), # Ｒ -> R
    u('\uff33'): u('S'), # Ｓ -> S
    u('\uff34'): u('T'), # Ｔ -> T
    u('\uff35'): u('U'), # Ｕ -> U
    u('\uff36'): u('V'), # Ｖ -> V
    u('\uff37'): u('W'), # Ｗ -> W
    u('\uff38'): u('X'), # Ｘ -> X
    u('\uff39'): u('Y'), # Ｙ -> Y
    u('\uff3a'): u('Z'), # Ｚ -> Z
    u('\uff41'): u('a'), # ａ -> a
    u('\uff42'): u('b'), # ｂ -> b
    u('\uff43'): u('c'), # ｃ -> c
    u('\uff44'): u('d'), # ｄ -> d
    u('\uff45'): u('e'), # ｅ -> e
    u('\uff46'): u('f'), # ｆ -> f
    u('\uff47'): u('g'), # ｇ -> g
    u('\uff48'): u('h'), # ｈ -> h
    u('\uff49'): u('i'), # ｉ -> i
    u('\uff4a'): u('j'), # ｊ -> j
    u('\uff4b'): u('k'), # ｋ -> k
    u('\uff4c'): u('l'), # ｌ -> l
    u('\uff4d'): u('m'), # ｍ -> m
    u('\uff4e'): u('n'), # ｎ -> n
    u('\uff4f'): u('o'), # ｏ -> o
    u('\uff50'): u('p'), # ｐ -> p
    u('\uff51'): u('q'), # ｑ -> q
    u('\uff52'): u('r'), # ｒ -> r
    u('\uff53'): u('s'), # ｓ -> s
    u('\uff54'): u('t'), # ｔ -> t
    u('\uff55'): u('u'), # ｕ -> u
    u('\uff56'): u('v'), # ｖ -> v
    u('\uff57'): u('w'), # ｗ -> w
    u('\uff58'): u('x'), # ｘ -> x
    u('\uff59'): u('y'), # ｙ -> y
    u('\uff5a'): u('z'), # ｚ -> z
}


def _read_non_empty_lines(path: str) -> Iterator[str]:
    with open(path, 'r', encoding='utf-8') as fr:
        for line in fr:
            x = line.strip()
            if not x:
                continue

            yield x

class TextLemmatiser:
    def __init__(self, lemma_file=None, sep='\t') -> None:
        assert lemma_file is not None
        self.lemma_dict = self.load_from_file(lemma_file, sep)
        logging.info("Load lemmatiser from {} over.".format(lemma_file))

    def lemmatise(self, token: str):
        lemma = token.lower()
        return self.lemma_dict.get(lemma, lemma)

    def load_from_file(self, lemma_file: str, sep='\t'):
        maps = {}
        for line in _read_non_empty_lines(lemma_file):
            items = [x.strip() for x in line.split(sep) if x.strip()]
            assert len(items) > 1
            for trans in items[1:]:
                maps[trans] = items[0]
        return maps

script_path = os.path.abspath(__file__)
script_directory = os.path.dirname(script_path)
_lemma_map_path = os.path.join(script_directory, "lemma.map.txt")
_lemmatiser = TextLemmatiser(_lemma_map_path)

_StopWords = { 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'do', 'does', 'doing', 'did', 'a', 'an', 'the', 'and', 'of' }

_Punctuations = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

def is_stopword(token: str):
    return token.lower() in _StopWords

def is_punctuation(token: str):
    return token.lower() in _Punctuations

def is_stopword_or_punctuation(token: str):
    return is_stopword(token) or is_punctuation(token)

@lru_cache(maxsize=MAX_CACHE_SIZE)
def lemmatise(token: str) -> str:
    return _lemmatiser.lemmatise(token)

def normalize_tokens(tokens: List[str], ignore_stopword=True, ignore_punctuation:bool=True) -> List[str]:
    norm_tokens = []
    for token in tokens:
        token = token.lower()
        token = ''.join([_Accent_Map.get(ch, ch) for ch in token])
        token = lemmatise(token)

        if ignore_stopword and is_stopword(token):
            continue

        if ignore_punctuation and is_punctuation(token):
            continue

        norm_tokens.append(token)

    return norm_tokens

def is_ip_address(s: str) -> bool:
    try:
        ipaddress.ip_address(s)
        return True
    except ValueError:
        pass
    return False

def is_uuid(s: str, fuzzy: bool=True) -> bool:
    try:
        uuid.UUID(s, version=4)
        return True
    except ValueError:
        pass

    if fuzzy and re.match(r'^[a-z0-9_-]+$', s) and len(s) >= 32:
        return True

    return False

def is_general_number(s: str) -> bool:
    s = s.replace(",", "").replace("-", "").replace(":", "").replace(" ", "").strip()
    if s and re.match(r'^[0-9]+$', s):
        return True
    return False
