from functools import lru_cache

name_mapping = {
    0: {
        "n": "noun",
        "v": "verb",
        "a": "adjective",
        "d": "adverb",
        "l": "article",
        "g": "particle",
        "c": "conjunction",
        "r": "preposition",
        "p": "pronoun",
        "m": "numeral",
        "i": "interjection",
        "u": "punctuation",
        "x": "not available",
    },
    1: {
        "1": "first person",
        "2": "second person",
        "3": "third person",
    },
    2: {
        "s": "singular",
        "p": "plural",
        "d": "dual",
    },
    3: {
        "p": "present",
        "i": "imperfect",
        "r": "perfect",
        "l": "pluperfect",
        "t": "future perfect",
        "f": "future",
        "a": "aorist",
    },
    4: {
        "i": "indicative",
        "s": "subjunctive",
        "o": "optative",
        "n": "infinitive",
        "m": "imperative",
        "p": "participle",
    },
    5: {"a": "active", "p": "passive", "m": "middle", "e": "medio-passive"},
    6: {"m": "masculine", "f": "feminine", "n": "neuter"},
    7: {
        "n": "nominative",
        "g": "genitive",
        "d": "dative",
        "a": "accusative",
        "v": "vocative",
        "l": "locative",
    },
    8: {"c": "comparative", "s": "superlative"},
}

short_form_to_long_form = {
    "1p": "first person",
    "2p": "second person",
    "3p": "third person",
    "a": "adjective",
    "acc": "accusative",
    "act": "active",
    "adj": "adjective",
    "adv": "adverb",
    "aor": "aorist",
    "art": "article",
    "c": "conjunction",
    "comp": "comparative",
    "conj": "conjunction",
    "d": "adverb",
    "dat": "dative",
    "fem": "feminine",
    "fut": "future",
    "futperf": "future perfect",
    "g": "particle",
    "gen": "genitive",
    "i": "interjection",
    "imp": "imperative",
    "impf": "imperfect",
    "ind": "indicative",
    "inf": "infinitive",
    "intj": "interjection",
    "l": "article",
    "loc": "locative",
    "m": "numeral",
    "masc": "masculine",
    "mediopassive": "medio-passive",
    "mid": "middle",
    "mp": "medio-passive",
    "n": "noun",
    "na": "not available",
    "neu": "neuter",
    "neut": "neuter",
    "nom": "nominative",
    "num": "numeral",
    "opt": "optative",
    "part": "participle",
    "pas": "passive",
    "pass": "passive",
    "perf": "perfect",
    "pl": "plural",
    "plup": "pluperfect",
    "prep": "preposition",
    "pres": "present",
    "pro": "pronoun",
    "pron": "pronoun",
    "punct": "punctuation",
    "r": "preposition",
    "s": "singular",
    "sg": "singular",
    "sing": "singular",
    "subj": "subjunctive",
    "super": "superlative",
    "u": "punctuation",
    "v": "verb",
    "voc": "vocative",
    "x": "not available",
}


def form_to_long_form(form):
    """
    Given a short form, like 'v', return the long form, like 'verb'.
    Return the short form if the long form is not found.
    Utility function.
    """
    return short_form_to_long_form.get(form.lower(), form.lower())


def parse_morphology(morphology):
    """
    Parse the morphology field of a morphological code.
    >>> parse_morphology("v3sasm---")
    ['verb', 'third person', 'singular', 'aorist', 'subjunctive', 'middle', None, None, None]
    >>> parse_morphology("n-s---mn-")
    ['noun', None, 'singular', None, None, None, 'masculine', 'nominative', None]
    """
    if len(morphology) != 9:
        raise ValueError("Morphology must be 9 characters long.")
    return [
        name_mapping[k].get(v, None) for k, v in enumerate(morphology.strip().lower())
    ]


@lru_cache(maxsize=128)
def produce_morphology(form):
    """
    Produce the morphology field of a grammatical form.
    From a form, like 'vocative', produce the position and short text, for example (7, 'v').
    Utility function.
    """
    lowered_form = form.lower()
    for k, v in name_mapping.items():
        for key, value in v.items():
            if value == lowered_form:
                return (k, key)
    return None


def morphology_string(forms):
    """
    Given a list of forms, produce the morphology string to the best
    of our ability.
    >>> morphology_string(['noun', 'masculine', 'singular', 'nominative'])
    'n-s---mn-'
    >>> morphology_string(sorted(['noun', 'masculine', 'singular', 'nominative']))
    'n-s---mn-'
    >>> morphology_string(['masc', 'sing', 'nom', 'n'])
    'n-s---mn-'
    >>> morphology_string(['verb', 'third person', 'singular', 'aorist', 'subjunctive', 'middle', None, None, None])
    'v3sasm---'
    >>> morphology_string(['verb', 'third person', 'singular', 'aorist', 'subjunctive', 'middle'])
    'v3sasm---'
    """
    morphology = ["-"] * 9
    for form in forms:
        if not form:
            continue
        result = produce_morphology(form_to_long_form(form))
        if result:
            position, value = result
            morphology[position] = value
    return "".join(morphology)


position_map = {
    1: "part_of_speech",
    2: "person",
    3: "number",
    4: "tense",
    5: "mood",
    6: "voice",
    7: "gender",
    8: "case",
    9: "degree",
}

position_name_map = {
    "pos": "part_of_speech",
    "part of speech": "part_of_speech",
    "per": "person",
    "pers": "person",
    "num": "number",
    "ten": "tense",
    "gen": "gender",
    "deg": "degree",
}


def short_form_to_position_name(short_form):
    """
    Given a short form, like 'pos', return the long form, like 'part of speech'.
    Return the short form if the long form is not found.
    Utility function.
    """
    return position_name_map.get(short_form.lower(), short_form.lower())


def position_to_name(position):
    """
    Given a 0-based position, return the name of the position.
    >>> position_to_name(0)
    'part_of_speech'
    >>> position_to_name(8)
    'degree'
    """
    return position_map.get(position + 1, None)


@lru_cache(maxsize=128)
def name_to_position(name):
    """
    Given a name, return the 0-based position.
    >>> name_to_position('part_of_speech')
    0
    >>> name_to_position('pos')
    0
    >>> name_to_position('degree')
    8
    """
    form = short_form_to_position_name(name)
    for k, v in position_map.items():
        if v == form:
            return k - 1
    return None


if __name__ == "__main__":
    import doctest

    doctest.testmod()
