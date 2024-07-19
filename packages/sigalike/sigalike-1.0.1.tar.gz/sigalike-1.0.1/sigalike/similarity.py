import string
from collections.abc import Collection, Mapping
from typing import Any, Dict, NamedTuple, Union

import numpy as np

from sigalike.utils import check_content, check_input_type


def _preprocess(s: str) -> str:

    # replace punctuation with whitespace
    s = s.translate(str.maketrans(string.punctuation, " " * len(string.punctuation)))

    s = s.lower()
    s = s.strip()

    return s


def shifted_sigmoid_similarity(str1: str, str2: str, shift: int = 4, preprocess: bool = True) -> float:
    """Calculates the shifted sigmoid similarity score between two strings.

    The shifted sigmoid similarity score acts as a fuzzy string matching
    metric. It begins with the ratio of unique tokens from the shorter
    string that are present in the longer string and then subtracts a penalty
    using a shifted sigmoid function (the logistic function) and the difference
    in length between the two token sets.

    Parameters
    ----------
    str1 : str
        The first string to compare.
    str2 : str
        The second string to compare.
    shift : int, default 4
        Amount to shift sigmoid curve.
    preprocess : bool, default True
        Whether or not to run built-in preprocessing.

    Raises
    ------
    ValueError
        If the input strings are empty after preprocessing.

    Returns
    -------
    float
        Shifted sigmoid similarity score.

    Examples
    --------
    >>> shifted_sigmoid_similarity('apple', 'banana')
    0.0
    >>> shifted_sigmoid_similarity('apple', 'apple apple')
    1.0
    """
    check_input_type(str1, str)
    check_input_type(str2, str)
    check_input_type(shift, int)
    check_input_type(preprocess, bool)
    check_content(str1)
    check_content(str2)

    if preprocess is True:
        str1 = _preprocess(str1)
        str2 = _preprocess(str2)

        # re-check contents
        check_content(str1)
        check_content(str2)

    set_str1 = set(str1.split())
    set_str2 = set(str2.split())
    smaller_set = min(len(set_str1), len(set_str2))
    larger_set = max(len(set_str1), len(set_str2))

    num_matched = len(set_str1.intersection(set_str2))
    match_ratio = num_matched / smaller_set
    num_extra = larger_set - num_matched

    score = match_ratio
    # Penalize if non-perfect match
    if score > 0 and num_extra > 0:
        score -= 1 / (1 + np.exp(-num_extra + shift))

    return max(score, 0)


class BestMatch(NamedTuple):
    """
    Named tuple to represent the best match.
    """

    match: str
    score: float


def best_match(
    collection1: Union[Collection, Mapping, str],
    collection2: Union[Collection, Mapping],
    shift: int = 4,
    preprocess: bool = True,
) -> Union[BestMatch, Dict[str, BestMatch]]:
    """
    Returns the best match(es) between two collections or a string and a collection.

    Parameters
    ----------
    collection1 : Collection, Mapping, or str
        The first collection to compare or a single string.
    collection2 : Collection or Mapping
        The second collection to compare.
    shift : int, optional
        The shift parameter for the shifted sigmoid similarity metric.
    preprocess : bool, optional
        Whether to preprocess the input strings.

    Returns
    -------
    BestMatch or Dict[str, BestMatch]
        If both inputs are collections, returns a dictionary where the keys are the
        strings from the first collection and the values are the named tuples with the best
        string match and its associated score from the second collection. If collection1 is
        a string and collection2 is a collection, returns a named tuple with the best matching
        string and its associated score.

    Raises
    ------
    ValueError
        If either of the input collections are empty.
    TypeError
        If one or more inputs are not of the correct type (str, Collection, or Mapping).

    Examples
    --------
    >>> best_match("hello", ["hello", "world", "foo"])
    BestMatch(match='hello', score=1.0)
    >>> best_match(["hello", "world"], ["hello", "world", "foo"])
    {'hello': BestMatch(match='hello', score=1.0), 'world': BestMatch(match='world', score=1.0)}
    >>> best_match(["hello", "world"], ["foo", "bar"])
    {'hello': BestMatch(match='', score=0.0), 'world': BestMatch(match='', score=0.0)}
    """
    if not isinstance(collection1, (str, Collection, Mapping)):
        raise TypeError("The first input is not of the correct type. Expected str, Collection, or Mapping.")
    if not isinstance(collection2, (Collection, Mapping)):
        raise TypeError("The second input is not of the correct type. Expected Collection or Mapping.")

    if len(collection1) == 0 or len(collection2) == 0:
        raise ValueError("Input collections cannot be empty")

    if isinstance(collection1, str):
        if isinstance(collection2, Mapping):
            return _best_match_string_collection(collection1, collection2.keys(), shift, preprocess)
        elif isinstance(collection2, Collection):
            return _best_match_string_collection(collection1, collection2, shift, preprocess)
    elif isinstance(collection1, Mapping):
        if isinstance(collection2, Mapping):
            return _best_match_collections(collection1.keys(), collection2.keys(), shift, preprocess)
        elif isinstance(collection2, Collection):
            return _best_match_collections(collection1.keys(), collection2, shift, preprocess)
    elif isinstance(collection1, Collection):
        if isinstance(collection2, Mapping):
            return _best_match_collections(collection1, collection2.keys(), shift, preprocess)
        elif isinstance(collection2, Collection):
            return _best_match_collections(collection1, collection2, shift, preprocess)


def _best_match_string_collection(string1: str, collection: Collection, shift: int, preprocess: bool) -> BestMatch:
    """
    Returns the best match between a string and a collection.

    Parameters
    ----------
    string1 : str
        The string to compare.
    collection : Collection
        The collection to compare against the string.
    shift : int
        The shift parameter for the shifted sigmoid similarity metric.
    preprocess : bool
        Whether to preprocess the input strings.

    Returns
    -------
    BestMatch
        A named tuple with the best matching string from the collection and its associated score.
    """
    best_match = BestMatch(match="", score=0.0)
    for item in collection:
        score = shifted_sigmoid_similarity(string1, item, shift, preprocess)
        if score > best_match.score:
            best_match = BestMatch(match=item, score=score)
    return best_match


def _best_match_collections(
    collection1: Collection, collection2: Collection, shift: int, preprocess: bool
) -> Dict[str, BestMatch]:
    """
    Returns the best match(es) between two collections.

    Parameters
    ----------
    collection1 : Collection
        The first collection to compare.
    collection2 : Collection
        The second collection to compare.
    shift : int
        The shift parameter for the shifted sigmoid similarity metric.
    preprocess : bool
        Whether to preprocess the input strings.

    Returns
    -------
    Dict[Any, BestMatch]
        A dictionary where the keys are the strings from the first collection and the values
        are the named tuples with the best string match and its associated score from the
        second collection.
    """
    best_matches = {}
    for item1 in collection1:
        best_matches[item1] = _best_match_string_collection(item1, collection2, shift, preprocess)

    return best_matches
