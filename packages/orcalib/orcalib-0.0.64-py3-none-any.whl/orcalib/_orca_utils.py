from collections import defaultdict

import torch
from torch import Tensor


def compute_lps_array(pattern) -> list[int]:
    """Compute the longest prefix that is also a suffix (lps) array used in KMP algorithm.

    Args:
        pattern: Pattern

    Returns:
        lps array
    """
    lps = [0] * len(pattern)
    length = 0  # length of the previous longest prefix suffix

    # Loop calculates lps[i] for i = 1 to M-1
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
                # Note that we do not increment i here
            else:
                lps[i] = 0
                i += 1

    return lps


def find_suffixes_in_sequence(S, M, S_min, S_max) -> list[tuple[int, int, str]]:
    """Find the starting indexes where the suffixes of S of lengths between S_min and S_max are contained in M.

    Args:
        S: Sequence
        M: Subsequence
        S_min: Minimum length of suffix
        S_max: Maximum length of suffix
    """
    occurrences = []

    # Iterate through the range of lengths for suffixes of S
    for suffix_length in range(S_min, S_max + 1):
        # Get the suffix of S of length suffix_length
        suffix = S[-suffix_length:]

        # Preprocess the suffix to get the lps array
        lps = compute_lps_array(suffix)

        # Start searching for the suffix in M
        i = j = 0  # i is index for M, j is index for suffix
        while i < len(M):
            if suffix[j] == M[i]:
                i += 1
                j += 1

            if j == len(suffix):
                # If we found a complete match, record the index where it starts in M
                if i < len(M):
                    occurrences.append((i - j, len(suffix), M[i]))
                else:
                    occurrences.append((i - j, len(suffix), None))
                j = lps[j - 1]

            # Mismatch after j matches
            elif i < len(M) and suffix[j] != M[i]:
                # Do not match lps[0..lps[j-1]] characters, they will match anyway
                if j != 0:
                    j = lps[j - 1]
                else:
                    i += 1

    return occurrences


def extract_occurance_ranks(occurrences, ref_length) -> dict:
    """Extract the scores of the occurrences of the suffixes in the reference sequence.

    Args:
        occurrences: Occurrences
        ref_length: Length of reference sequence

    Returns:
        Scores
    """
    scores = defaultdict(int)
    for _, length, next_token in occurrences:
        if next_token is None:
            continue
        if length > scores[next_token]:
            scores[next_token] = length / ref_length
    return dict(scores)


def bag_of_words_scores(bag_of_words: list[tuple[list[int], float]], vocab_size: int) -> Tensor:
    """Compute the scores of the bag of words.

    Args:
        bag_of_words: Bag of words
        vocab_size: Vocabulary size

    Returns:
        Scores
    """
    res = torch.zeros(vocab_size)
    for bag, score in bag_of_words:
        for token in bag:
            res[token] += score
    return Tensor(res)
