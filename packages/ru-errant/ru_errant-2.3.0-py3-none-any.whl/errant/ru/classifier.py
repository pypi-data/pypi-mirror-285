from pathlib import Path
import Levenshtein
from errant.en.lancaster import LancasterStemmer
import spacy
from nltk.stem.snowball import SnowballStemmer
import spacy.symbols as POS
import codecs
import json


# Load Hunspell word list
def load_word_list(path):
    with open(path) as word_list:
        return set([word.strip() for word in word_list])


def load_freq_dict(path):
    with codecs.open(path, 'r', encoding='utf-8') as fr:
        freq_dict = json.load(fr)
        return freq_dict


# First install errant editable
# pip install spacy==3.1.0
#  python3 -m spacy download ru_core_news_lg


# Classifier resources
base_dir = Path(__file__).resolve().parent
# Spacy
nlp = None
# Lancaster Stemmer
# stemmer = LancasterStemmer()
stemmer = SnowballStemmer("russian")
# GB English word list (inc -ise and -ize)
spell = load_word_list(base_dir / "resources" / "Russian.dic")
freq_dict = load_freq_dict(base_dir / "resources" / "freq_dict.json")
# Part of speech map file
# Open class coarse Spacy POS tags
open_pos1 = {POS.ADJ, POS.ADV, POS.NOUN, POS.VERB}
# Open class coarse Spacy POS tags (strings)
open_pos2 = {"ADJ", "ADV", "NOUN", "VERB", "NUM"}
# Rare POS tags that make uninformative error categories
rare_pos = {"INTJ", "SYM", "X"}

# Some dep labels that map to pos tags.
dep_map = {
    "acomp": "ADJ",
    "amod": "ADJ",
    "advmod": "ADV",
    "det": "DET",
    "prep": "PREP",
    "prt": "PART",
    "punct": "PUNCT"}


# Input: An Edit object
# Output: The same Edit object with an updated error type


def classify(edit):
    # Nothing to nothing is a detected but not corrected edit
    if not edit.o_toks and not edit.c_toks:
        edit.type = "UNK"
    # Missing
    elif not edit.o_toks and edit.c_toks:
        op = "M:"
        cat = get_one_sided_type(edit.c_toks)
        edit.type = op + cat
    # Unnecessary
    elif edit.o_toks and not edit.c_toks:
        op = "U:"
        cat = get_one_sided_type(edit.o_toks)
        edit.type = op + cat
    # Replacement and special cases
    else:
        # Same to same is a detected but not corrected edit
        if edit.o_str == edit.c_str:
            edit.type = "UNK"
        # Classify the edit as if the last token wasn't there
        elif edit.o_toks[-1].lower == edit.c_toks[-1].lower and \
                (len(edit.o_toks) > 1 or len(edit.c_toks) > 1):
            # Store a copy of the full orig and cor toks
            all_o_toks = edit.o_toks[:]
            all_c_toks = edit.c_toks[:]
            # Truncate the instance toks for classification
            edit.o_toks = edit.o_toks[:-1]
            edit.c_toks = edit.c_toks[:-1]
            # Classify the truncated edit
            edit = classify(edit)
            # Restore the full orig and cor toks
            edit.o_toks = all_o_toks
            edit.c_toks = all_c_toks
        # Replacement
        else:
            op = "R:"
            cat = get_two_sided_type(edit.o_toks, edit.c_toks)
            edit.type = op + cat
    return edit


# Input: Spacy tokens
# Output: A list of pos and dep tag strings


def get_edit_info(toks):
    pos = []
    dep = []
    morph = dict()
    for tok in toks:
        pos.append(tok.tag_)
        dep.append(tok.dep_)
        morphs = str(tok.morph).split('|')
        for m in morphs:
            if len(m.strip()):
                k, v = m.strip().split('=')
                morph[k] = v
    return pos, dep, morph


# Input: Spacy tokens
# Output: An error type string based on input tokens from orig or cor
# When one side of the edit is null, we can only use the other side


def get_one_sided_type(toks):
    # Extract pos tags and parse info from the toks
    pos_list, dep_list, _ = get_edit_info(toks)
    # Auxiliary verbs
    if set(dep_list).issubset({"aux", "auxpass"}):
        return "VERB:TENSE"
    # POS-based tags. Ignores rare, uninformative categories
    if len(set(pos_list)) == 1 and pos_list[0] not in rare_pos:
        return pos_list[0]
    # More POS-based tags using special dependency labels
    if len(set(dep_list)) == 1 and dep_list[0] in dep_map.keys():
        return dep_map[dep_list[0]]
    # To-infinitives and phrasal verbs
    if set(pos_list) == {"PART", "VERB"}:
        return "VERB"
    # Tricky cases
    else:
        return "OTHER"


# Input 1: Spacy orig tokens
# Input 2: Spacy cor tokens
# Output: An error type string based on orig AND cor
def get_two_sided_type(o_toks, c_toks):
    # Extract pos tags and parse info from the toks as lists
    o_pos, o_dep, o_morph = get_edit_info(o_toks)
    c_pos, c_dep, c_morph = get_edit_info(c_toks)

    # Orthography; i.e. whitespace and/or case errors.
    if only_orth_change(o_toks, c_toks):
        return "ORTH"
    # Word Order; only matches exact reordering.
    if exact_reordering(o_toks, c_toks):
        return "WO"

    # 1:1 replacements (very common)
    if len(o_toks) == len(c_toks) == 1:
        # 2. SPELLING AND INFLECTION
        # if lemmas are not in spell -- not tokens -- TODO: change here
        # Only check alphabetical strings on the original side
        # Spelling errors take precedence over POS errors; this rule is ordered
        if o_toks[0].text.isalpha():
            if o_toks.text not in spell and \
                    o_toks.text.lower() not in spell and o_toks.text.lower() not in freq_dict:
                # Check if both sides have a common lemma
                if o_toks[0].lemma == c_toks[0].lemma:
                    if o_pos == c_pos and o_pos[0] in {"NOUN", "VERB", "ADJ", 'PRON', 'NUM'}:
                        return o_pos[0] + ":INFL"
                    elif o_pos != c_pos:
                        return "MORPH"
                    # Use string similarity to detect true spelling errors.
                else:
                    char_ratio = Levenshtein.ratio(o_toks[0].text, c_toks[0].text)
                    # Ratio > 0.5 means both side share at least half the same chars.
                    # WARNING: THIS IS AN APPROXIMATION.
                    if char_ratio > 0.5:
                        return "SPELL"
                    # If ratio is <= 0.5, the error is more complex e.g. tolk -> say
                    else:
                        # If POS is the same, this takes precedence over spelling.
                        if o_pos == c_pos and \
                                o_pos[0] not in rare_pos:
                            return "SPELL:" + o_pos[0]
                        # Tricky cases.
                        else:
                            return "SPELL:OTHER"

        # 3. MORPHOLOGY
        # Only ADJ, ADV, NOUN and VERB can have inflectional changes.
        #
        # print(o_toks[0].lemma, o_toks)
        # print(c_toks[0].lemma, c_toks)
        # print(o_pos[0])
        # print(c_pos[0])
        # print(o_toks[0].tag_, o_toks[0])
        # print(c_toks[0].tag_, c_toks[0])
        # print(o_morph, o_dep)
        # print(c_morph, c_dep)
        if o_toks[0].lemma == c_toks[0].lemma and \
                o_pos[0] in open_pos2 and \
                c_pos[0] in open_pos2:
            # Same POS on both sides
            if o_pos == c_pos:
                tag_d = {'Number': 'NUM', 'Gender': 'GEN', 'Case': 'CASE'}
                # Adjective form; e.g. comparatives
                if o_pos[0] == "ADJ":
                    if 'Degree' in o_morph and 'Degree' in c_morph:
                        if o_morph['Degree'] != c_morph['Degree']:
                            return "ADJ:COMP_FORM"
                    if 'StyleVariant' in o_morph or 'StyleVariant' in c_morph and\
                            not ('StyleVariant' in o_morph and 'StyleVariant' in c_morph):
                        return "ADJ:FULL/SHORT"
                    # Adj number
                    common_tag = []
                    result_tags = []
                    for k, v in tag_d.items():
                        if k in o_morph and k in c_morph:
                            for ko, vo in o_morph.items():
                                if ko in c_morph and ko != k and vo == c_morph[ko]:
                                    common_tag.append(True)
                            if all(common_tag) and o_morph[k] != c_morph[k]:
                                result_tags.append(v)
                    if len(result_tags):
                        return "ADJ:" + ':'.join(result_tags)
                    else:
                        return 'ADJ:INFL'
                # Noun number
                if o_pos[0] in ["NOUN", "PRON", 'NUM']:
                    common_tag = []
                    tag_n = {'Number': 'NUM', 'Case': 'CASE'}
                    noun_result_tags = []
                    for k, v in tag_n.items():
                        if k in o_morph and k in c_morph:
                            for ko, vo in o_morph.items():
                                if ko in c_morph and ko != k and vo == c_morph[ko]:
                                    common_tag.append(True)
                            if all(common_tag) and o_morph[k] != c_morph[k]:
                                noun_result_tags.append(v)
                    if len(noun_result_tags):
                        return o_pos[0] + ':' + ':'.join(noun_result_tags)
                    else:
                        return o_pos[0] + ':INFL'
                # Verbs - various types
                # Maybe make hierarchy -- verb form, then tense, then aspect, then everything else
                # for tense and voice need a parser info maybe
                if o_pos[0] == "VERB":
                    if 'VerbForm' in o_morph and 'VerbForm' in c_morph and o_morph['VerbForm'] != c_morph['VerbForm']:
                        return o_pos[0] + ':FORM'
                    elif 'Tense' in o_morph and 'Tense' in c_morph and o_morph['Tense'] != c_morph['Tense']:
                        return o_pos[0] + ':TENSE'
                    elif 'Aspect' in o_morph and 'Aspect' in c_morph and o_morph['Aspect'] != c_morph['Aspect']:
                        return o_pos[0] + ':ASPECT'
                    else:
                        common_verb_tag = []
                        tag_v = {'Number': 'NUM', 'Gender': 'GEN', 'Voice': 'VOICE',
                                 'Mood': 'MOOD'}
                        verb_result_tags = []
                        for k, v in tag_v.items():
                            if k in o_morph and k in c_morph:
                                for ko, vo in o_morph.items():
                                    if ko in c_morph and ko != k and vo == c_morph[ko]:
                                        common_verb_tag.append(True)
                                if all(common_verb_tag) and o_morph[k] != c_morph[k]:
                                    verb_result_tags.append(v)
                        if len(verb_result_tags):
                            return o_pos[0] + ':' + ':'.join(verb_result_tags)
                        else:
                            return o_pos[0] + ':INFL'
                if o_pos[0] == 'VERB' and 'VerbForm' in o_morph and o_morph['VerbForm'] == 'Part':
                    if c_pos == 'ADJ':
                        return o_pos[0] + ':INFL'
                elif c_pos[0] == 'VERB' and 'VerbForm' in c_morph and c_morph['VerbForm'] == 'Part':
                    if o_pos == 'ADJ':
                        return c_pos[0] + ':INFL'
        if o_toks[0].lemma != c_toks[0].lemma and \
                o_pos[0] in open_pos2 and \
                c_pos[0] in open_pos2 and o_pos[0] == c_pos[0] == 'VERB':
            if len(o_morph) == len(c_morph) and \
                    all([o_morph[k] == c_morph[k] for k, v in o_morph.items() if (k != 'Aspect' and k in c_morph)]):
                return o_pos[0] + ':ASPECT'
        # Derivational morphology.
        if stemmer.stem(o_toks[0].text) == stemmer.stem(c_toks[0].text) and \
                o_pos[0] in open_pos2 and \
                c_pos[0] in open_pos2 and o_pos[0] != c_pos[0]:
            return "MORPH"
        # POS-based tags. Some of these are context sensitive mispellings.
        if o_pos == c_pos and o_pos[0] not in rare_pos:
            return o_pos[0]
        # Some dep labels map to POS-based tags.
        if o_dep == c_dep and o_dep[0] in dep_map.keys():
            return dep_map[o_dep[0]]
        if set(o_pos + c_pos) == {"PART", "PREP"} or \
                set(o_dep + c_dep) == {"prt", "prep"}:
            return "PART"
        else:
            return "OTHER"

    if set(o_dep + c_dep) == {"aux", "ROOT"}:
        return "VERB:TENSE"
    # All same special dep labels.
    if len(set(o_dep + c_dep)) == 1 and \
            o_dep[0] in dep_map.keys():
        return dep_map[o_dep[0]]
    else:
        return "OTHER"


# Input 1: Spacy orig tokens
# Input 2: Spacy cor tokens
# Output: Boolean; the difference between orig and cor is only whitespace or case

def only_orth_change(o_toks, c_toks):
    o_join = "".join([o.lower_ for o in o_toks])
    c_join = "".join([c.lower_ for c in c_toks])
    if o_join == c_join:
        return True
    return False


# Input 1: Spacy orig tokens
# Input 2: Spacy cor tokens
# Output: Boolean; the tokens are exactly the same but in a different order
def exact_reordering(o_toks, c_toks):
    # Sorting lets us keep duplicates.
    o_set = sorted([o.lower_ for o in o_toks])
    c_set = sorted([c.lower_ for c in c_toks])
    if o_set == c_set:
        return True
    return False


# Input 1: An original text spacy token.
# Input 2: A corrected text spacy token.
# Output: Boolean; both tokens have a dependant auxiliary verb.
def preceded_by_aux(o_tok, c_tok):
    # If the toks are aux, we need to check if they are the first aux.
    if o_tok[0].dep_.startswith("aux") and c_tok[0].dep_.startswith("aux"):
        # Find the parent verb
        o_head = o_tok[0].head
        c_head = c_tok[0].head
        # Find the children of the parent
        o_children = o_head.children
        c_children = c_head.children
        # Check the orig children.
        for o_child in o_children:
            # Look at the first aux...
            if o_child.dep_.startswith("aux"):
                # Check if the string matches o_tok
                if o_child.text != o_tok[0].text:
                    # If it doesn't, o_tok is not first so check cor
                    for c_child in c_children:
                        # Find the first aux in cor...
                        if c_child.dep_.startswith("aux"):
                            # If that doesn't match either, neither are first aux
                            if c_child.text != c_tok[0].text:
                                return True
                            # Break after the first cor aux
                            break
                # Break after the first orig aux.
                break
    # Otherwise, the toks are main verbs so we need to look for any aux.
    else:
        o_deps = [o_dep.dep_ for o_dep in o_tok[0].children]
        c_deps = [c_dep.dep_ for c_dep in c_tok[0].children]
        if "aux" in o_deps or "auxpass" in o_deps:
            if "aux" in c_deps or "auxpass" in c_deps:
                return True
    return False
