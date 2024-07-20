morphological_mapping = {
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
    "n": "noun",
    "v": "verb",
    "a": "adjective",
    "adj": "adjective",
    "d": "adverb",
    "adv": "adverb",
    "l": "article",
    "art": "article",
    "g": "particle",
    "c": "conjunction",
    "conj": "conjunction",
    "r": "preposition",
    "prep": "preposition",
    "pro": "pronoun",
    "pron": "pronoun",
    "m": "numeral",
    "num": "numeral",
    "i": "interjection",
    "intj": "interjection",
    "u": "punctuation",
    "punct": "punctuation",
    "x": "not available",
    "na": "not available",
    "1p": "first person",
    "2p": "second person",
    "3p": "third person",
    "sg": "singular",
    "sing": "singular",
    "s": "singular",
    "pl": "plural",
    "pres": "present",
    "impf": "imperfect",
    "perf": "perfect",
    "plup": "pluperfect",
    "futperf": "future perfect",
    "fut": "future",
    "aor": "aorist",
    "ind": "indicative",
    "subj": "subjunctive",
    "opt": "optative",
    "inf": "infinitive",
    "imp": "imperative",
    "part": "participle",
    "act": "active",
    "mid": "middle",
    "mp": "medio-passive",
    "masc": "masculine",
    "fem": "feminine",
    "neut": "neuter",
    "neu": "neuter",
    "nom": "nominative",
    "gen": "genitive",
    "dat": "dative",
    "acc": "accusative",
    "voc": "vocative",
    "loc": "locative",
    "comp": "comparative",
    "super": "superlative",
}


def form_to_long_form(form):
    """
    Given a short form, like 'v', return the long form, like 'verb'.
    Return the short form if the long form is not found.
    """
    return short_form_to_long_form.get(form, form)


def parse_morphology(morphology):
    """
    Parse the morphology field of a morphological code.
    """
    return [morphological_mapping[k].get(v, None) for k, v in enumerate(morphology)]


def produce_morphology(form):
    """
    Produce the morphology field of a grammatical form.
    From a form, like 'vocative', produce the position and short text, for example (7, 'v').
    """
    for k, v in morphological_mapping.items():
        for key, value in v.items():
            if value == form:
                return (k, key)
    return None


def produce_morphology_string(forms):
    """
    Given a list of forms, produce the morphology string to the best
    of our ability.
    For example, given ['noun', 'masculine', 'singular', 'nominative'],
    return 'n-s---mn-'.
    """
    morphology = ["-"] * 9
    for form in forms:
        result = produce_morphology(form_to_long_form(form))
        if result:
            position, value = result
            morphology[position] = value
    return "".join(morphology)
