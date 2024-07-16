# source: https://github.com/seadavis/StoryNode/blob/main/src/core/relation_extraction.py
import sys

import spacy
from spacy.matcher import Matcher

nlp = spacy.load("en_core_web_sm")
from spacy.matcher import Matcher

matcher = Matcher(nlp.vocab)

VERB_PATTERN = [[{"POS": "VERB"}]]

matcher.add("VERB_PATTERN", VERB_PATTERN)

# RELATION_PATTERN = [[{"POS": "VERB"}, {"POS": "PART", "OP": "*"}, {"POS": "ADV", "OP": "*"}],
#                     [{"POS": "VERB"}, {"POS": "ADP", "OP": "*"}, {"POS": "DET", "OP": "*"},
#                      {"POS": "AUX", "OP": "*"},
#                      {"POS": "ADJ", "OP": "*"}, {"POS": "ADV", "OP": "*"}]]
RELATION_PATTERN = pattern = [[
    {"POS": "AUX", "OP": "*"},  # Optional auxiliary verbs
    {"POS": "VERB"},            # Main verb
    {"POS": "ADV", "OP": "*"},  # Optional adverbs
    {"POS": "PART", "OP": "*"}, # Optional particles
    {"POS": "ADP", "OP": "*"},  # Optional prepositions
]]
matcher.add("RELATION_PATTERN", RELATION_PATTERN)


class TextSpan:

    def __init__(self, span):
        self.span = span

    @property
    def length(self):
        return self.end_index - self.start_index

    @property
    def sentence(self):
        return self.span.text

    @property
    def start_index(self):
        return self.span.start

    @property
    def end_index(self):
        return self.span.end

    def __eq__(self, other):
        return self.sentence == other.sentence and self.start_index == self.start_index and self.end_index == self.end_index

    def join(self, other):

        if not self.intersects(other):
            return None

        min_start = min(self.start_index, other.start_index)
        max_end = max(self.end_index, other.end_index)

        return TextSpan(self.span.doc[min_start:max_end])

    """
    Takes the subset of the start_index, end_index
    start_index - the starting index of the subset, relative
    to the spans parent document

    end_index - the ending index of the subset, relative 
    to the spans partner document
    """

    def subset(self, start_index, end_index):
        return TextSpan(self.span.doc[start_index:end_index])

    """
    Returns true if the given span intersects with this span.
    False otherwise.
    """

    def intersects(self, other):
        if self.start_index >= other.start_index and self.start_index <= other.end_index:
            return True
        if self.end_index >= other.start_index and self.end_index <= other.end_index:
            return True
        if other.start_index >= self.start_index and other.start_index <= self.end_index:
            return True
        if other.end_index >= self.start_index and other.end_index <= self.end_index:
            return True
        return False


class Relation:

    def __init__(self, left_phrase, relation_phrase, right_phrase):
        """Constructs a relation of the form
        (left_phrase, relation_phrase, right_phrase)

        Examples:
        (Sean, runs to, mall), 
        (Gandalf, shall not, pass), 
        (the dog, flies, at midnight)

        Args:
            left_phrase (TextSpan): the leftside phrse
            relation_phrase (TextSpan): the relation phrase
            right_phrase (TextSpan): the right-side phrase of the relation
        """
        self.left_phrase = left_phrase
        self.relation_phrase = relation_phrase
        self.right_phrase = right_phrase

    def __eq__(self, other):
        return self.left_phrase == other.left_phrase and self.relation_phrase == other.relation_phrase and self.right_phrase == other.right_phrase

    def __str__(self):
        return str(repr)

    def __repr__(self):
        return str((self.left_phrase.text, self.relation_phrase.text, self.right_phrase.text))


class RelationCollection:

    def __init__(self, relations):
        self.relations = relations

    @property
    def left_phrases(self):
        return None

    @property
    def right_phrases(self):
        return None

    @property
    def relation_phrases(self):
        return None

    def join(self, other):
        return None


def construct_text_spans(doc, matches):
    ret_spans = []
    for match_id, start, end in matches:
        ret_spans.append(doc[start:end])
    return ret_spans


def extract_relations(doc):
    """extracts the complete relations from the doc

    Args:
        doc ([type]): [description]

    Returns:
        [Relation]: the complete set of relations found from the documentation
    """
    if isinstance(doc, str):
        doc = nlp(doc)

    relation_spans = get_relation_spans(doc)

    # noun_phrase_pattern = [[{"POS": "NOUN", "OP": "+"}], [{"POS": "PROPN", "OP": "+"}], [{"POS": "PRON", "OP": "+"}]]
    noun_phrase_pattern = [[
        {"POS": "DET", "OP": "?"},  # Optional determiner
        {"POS": "ADJ", "OP": "*"},  # Optional adjectives
        {"POS": {"IN": ["PROPN", "NOUN"]}},  # "NOUN"},  # Main noun
        {"POS": {"IN": ["PROPN", "NOUN"]}, "OP": "*"}  # Optional consecutive nouns
    ]]
    matcher.add("noun_phrase_pattern", noun_phrase_pattern, greedy="LONGEST")

    relations = []

    for span in relation_spans:
        matches = matcher(doc.doc)
        entity_matches = [match for match in matches if nlp.vocab.strings[match[0]] == "noun_phrase_pattern"]
        left_noun = find_nearest_pattern(doc, entity_matches, span, True)
        right_noun = find_nearest_pattern(doc, entity_matches, span, False)

        if (not left_noun is None) and (not right_noun is None):
            relations.append({"head": left_noun.text, "type": span.text, "tail": right_noun.text})
    return relations


def get_relation_spans(doc):
    """extracts the complete relations from the doc

    Args:
        doc (Document): the document we are using to gather
        the middle portion of the relations

    Returns:
        [Relation]: the complete set of relations found from the documentation
    """

    verbs = get_verbs(doc)

    matches = matcher(doc.doc)
    relation_matches = [match for match in matches if nlp.vocab.strings[match[0]] == "RELATION_PATTERN"]

    syntactical_constraint_matches = construct_text_spans(doc, relation_matches)
    print("relation_matches", syntactical_constraint_matches)

    relation_spans = []
    for verb in verbs:
        verb_spans = [span for span in syntactical_constraint_matches if is_span_subset(verb, span)]
        joined_spans = merge_spans(verb_spans)
        longest_span = find_longest_span(joined_spans)
        relation_spans.append(longest_span)
    return relation_spans


def is_span_subset(span1, span2):
    return span1.start >= span2.start and span1.end <= span2.end


def get_verbs(doc):
    matches = matcher(doc.doc)
    verbs = []
    for match_id, start, end in matches:
        if nlp.vocab.strings[match_id] == "VERB_PATTERN":
            verbs.append(doc.doc[start:end])
    return verbs


def find_nearest_pattern(doc, matches, text_span, search_before):
    """Find in doc, the nearest pattern to the given text_span,
    returns the result as a TextSpan

    Args:
        doc (spacy Document) the document in spacy we are looking for
        pattern (the pattern array to search for): the array of patterns we are
        looking for
        text_span (TextSpan): describes where in the document the word or phrase is
        search_before (bool): if true, then we want to find the nearest pattern that occurs,
                before text_span. Otherwise finds the nearest pattern after text_span
    """
    # matcher.add("PatternNear", pattern)
    # matches = matcher(doc.doc)
    nearest_pattern = None
    # pattern_near_matches = [match for match in matches if nlp.vocab.strings[match[0]] == "PatternNear"]
    # print(f"pattern_near_matches: {pattern_near_matches}")
    spans = construct_text_spans(doc, matches)
    # spans = merge_spans(spans)
    sorted_spans = sorted(spans, key=lambda s: s.start)

    spans_to_search = []
    if search_before:
        spans_to_search = [span for span in sorted_spans if span.start < text_span.start]
        spans_to_search.reverse()

    else:
        spans_to_search = [span for span in sorted_spans if span.start > text_span.start]

    if len(spans_to_search) == 0:
        return None
    # print(f"spans_to_search: {spans_to_search}")
    return spans_to_search[0]


def merge_spans(text_spans):
    """
    if spans are consecutive or overlapping, combine them
    """
    merged_spans = []
    sorted_spans = sorted(text_spans, key=lambda s: (s.start, s.end))

    for span in sorted_spans:
        if len(merged_spans) > 0:
            last_span = merged_spans[-1]
            if last_span.end == span.start:
                last_span.end = span.end
            else:
                merged_spans.append(span)
        else:
            merged_spans.append(span)

    return merged_spans


def find_latest_span(text_spans):
    """Finds the latest occuring span in given 
    set of text_spans

    Args:
        text_spans (TextSpan): the span of text according to some document
    """
    if len(text_spans) == 0:
        return None

    sorted_spans = sorted(text_spans, key=lambda s: s.end_index, reverse=True)
    return sorted_spans[0]


def find_earliest_span(text_spans):
    """Finds the span that is the "earliest occuriing", i.e. the 
    smallest start index

    Args:
        text_spans ([type]): the smallest match on the text span
    """
    if len(text_spans) == 0:
        return None

    sorted_spans = sorted(text_spans, key=lambda s: s.start_index)
    return sorted_spans[0]


def find_longest_span(text_spans):
    """find the longest match

    Args:
        text_spans ([TextSpan]): the set of matches we are filtering
    """
    if len(text_spans) == 0:
        return None

    sorted_spans = sorted(text_spans, key=lambda s: len(s), reverse=True)
    return sorted_spans[0]


if __name__ == '__main__':
    # nlp = spacy.load('en_core_web_sm')
    text = "Iraq halts Oil Exports from Main Southern Pipeline (Reuters) Reuters - Authorities have halted oil export\flows from the main pipeline in southern Iraq after\intelligence showed a rebel militia could strike\infrastructure, an oil official said on Saturday."
    # Triplet: Authorities,halted,oil
    print(text)
    doc = nlp(text)
    rel = extract_relations(doc)
    print(rel)
