"""Class to normalize TEI files from raw Adobe InDesign files.
"""
from xml.etree import ElementTree
import re
from typing import Tuple
from xml.sax.saxutils import unescape
from bidi.algorithm import get_display


class TEITransformer:
    """Base class to clean-up XML files to make them more compliant with TEI formatting rules."""

    def __init__(self, file_path: str) -> None:
        """Create a NormalizeTEI object object.

        Args:
            file_path (str): The path to the TEI file to load.
        """
        self.parsed_manuscript = ElementTree.parse(file_path).getroot()
        self.clean_manuscript = ElementTree.Element("root")

    def create_header(self):
        """Create the header for the clean manuscript."""

    @staticmethod
    def chap_normalizer(chapter_to_normalize: str) -> str:
        """Normalize the chapter numbers, in the case where they have been poorly formatted."""
        words_to_remove = ["siracide", "chapitre", "chapter"]
        for word in words_to_remove:
            if word in chapter_to_normalize.lower():
                return chapter_to_normalize.lower().replace(word, "").strip()
        return chapter_to_normalize.strip()

    @staticmethod
    def chap_verse_normalizer(verse_to_normalize: str) -> list[str]:
        """Normalize the chapter and verse numbers, in the case where they have been poorly formatted,
        as there are some inconsistencies in the TEI files.
        Verses are sometimes labelled as "chapter:verse", which should not be the case.
        """
        verse_to_normalize = verse_to_normalize.strip()
        if bool(re.compile(r'[A-Z]').search(verse_to_normalize)):
            verse_to_normalize = "".join(re.compile(r'[^A-Z]').findall(verse_to_normalize))
            verse_to_normalize = str(verse_to_normalize.encode('ascii',"strict")).replace("?", "").strip().lstrip("b'").rstrip("'").strip()
        if ":" in verse_to_normalize:
            return verse_to_normalize.split(":")
        return [verse_to_normalize]

    @staticmethod
    def add_XML_child(
        parent: ElementTree.Element, tag: str, text: str = None, attrib: dict = None
    ) -> ElementTree.Element:
        """Add an XML child to a parent, with different tags, text and attributes."""
        child = ElementTree.SubElement(parent, tag)
        if text:
            # Add text to child
            child.text = text.strip()
        if attrib:
            # Add attributes to child
            for key, value in attrib.items():
                child.set(key, value)
        return child

    @staticmethod
    def check_matched_bracket(word: str) -> bool:
        """Check if all opened bracket have been closed."""
        s = []
        balanced = True
        index = 0
        while index < len(word) and balanced:
            token = word[index]
            if token == "[":
                s.append(token)
            elif token == "]":
                if len(s) == 0:
                    balanced = False
                else:
                    s.pop()
            index += 1

        return balanced and len(s) == 0

    def reconstruct_word(self, word: str) -> str:
        """Given a partially available word displayed within brackets, wrap it around g
        reconstructed tags.
        """
        bracket_word = word
        nbr_closed_brackets = bracket_word.count("]")
        nbr_opened_brackets = bracket_word.count("[")

        if not "[" in word and not "]" in word:
            bracket_word = f"[{word}]"  # add brackets if they are missing
        elif nbr_closed_brackets < nbr_opened_brackets:  # if there is a missing closing
            bracket_word = f"{bracket_word}]"
        elif nbr_closed_brackets > nbr_opened_brackets:
            bracket_word = f"[{bracket_word}"
        elif not self.check_matched_bracket(word):
            bracket_word = f"[{word}]"  # add brackets if they are missing
        # If empty brackets, add a space between them
        if bracket_word == "[]":
            bracket_word = "[ ]"
        return bracket_word.replace("[", "<g type='reconstructed'>").replace(
            "]", "</g>"
        )

    @staticmethod
    def replace_spaces(match):
        """Given a match of regexp match, replace the match with its character length. 
        """
        return f"<blank orient='horizontal' span='{len(match.group())}'/>"

    def extract_blank_space(self, text):
        """Extract blank spaces of missing words from the manuscript."""
        pattern = r'\s{2,}'
        extracted_blank_space = re.sub(pattern, self.replace_spaces, text)
        return extracted_blank_space

    def compute_reconstructed_words(self, text: str) -> Tuple[list, list]:
        """Place the words contained within txt into <w> tags, and their reconstruction status
        within type attribute."""
        reconstructed = 0
        word_content_list = []
        reconstructed_list = []
        for subtext in re.split(r"(<blank.*?/>)", text):
            if subtext.startswith("<blank"):
                word_content_list.append(subtext)
                reconstructed_list.append(0)
            else:
                for word in re.split(r"(\t|\s)", subtext):
                    if word and word not in [" ", "[", "]"]:
                        if "[" in word:
                            # Enter reconstruction mode
                            reconstructed = 1
                        # Add word to list
                        if reconstructed:
                            word_content_list.append(self.reconstruct_word(word))
                        else:
                            word_content_list.append(word)
                        reconstructed_list.append(reconstructed)
                        # Leave reconstruction mode
                        if "]" in word:
                            reconstructed = 0

        return word_content_list, reconstructed_list

    def create_body(self):
        """Traverse the manuscript and clean it up."""
        current_folio = None
        current_col = None
        current_line = None
        for elem in self.parsed_manuscript.iter():
            if elem.text:
                txt = elem.text.strip()
                if txt:
                    if elem.tag == "ms":
                        ms_child = self.add_XML_child(
                            parent=self.clean_manuscript, tag=elem.tag, attrib={"name": txt}
                        )

                    elif elem.tag == "folio":
                        current_folio = txt.strip()
                    elif elem.tag == "col":
                        current_col = txt.strip()
                    elif elem.tag == "chap":
                        #TODO: put this in cleaner function
                        if "col." in txt.lower():
                            current_col = txt.lower().split("col.")[1].strip()
                        chapter_child = self.add_XML_child(
                            parent=ms_child,
                            tag="div",
                            attrib={
                                "type": elem.tag,
                                "n": self.chap_normalizer(txt),
                            },
                        )
                    elif elem.tag == "verse_nb":
                        normalized_verse = self.chap_verse_normalizer(txt.strip())
                        # If chapter and verses are specified within the same XML tag
                        if len(normalized_verse) > 1:
                            chapter_child = self.add_XML_child(
                                parent=ms_child,
                                tag="div",
                                attrib={"type": "chap", "n": normalized_verse[0]},
                            )
                            verse_child = self.add_XML_child(
                                parent=chapter_child,
                                tag="div",
                                attrib={"type": "verse", "n": normalized_verse[1]},
                            )
                        else:
                            verse_child = self.add_XML_child(
                                parent=chapter_child,
                                tag="div",
                                attrib={"type": "verse", "n": normalized_verse[0]},
                            )
                    elif elem.tag == "line":
                        current_line = txt.strip()
                        line_attrib = {"n": txt.strip()}
                        if current_folio:
                            line_attrib["folio"] = current_folio
                        if current_col:
                            line_attrib["col"] = current_col
                        try:     
                            self.add_XML_child(
                                parent=verse_child,
                                tag="line",
                                attrib=line_attrib,
                            )
                        except UnboundLocalError:
                            line_child = self.add_XML_child(
                                parent=chapter_child,
                                tag="line",
                                attrib=line_attrib,
                            )
                    elif elem.tag in ["margin",
                                      "margin_reconstructed",
                                      "margin_supralinear",
                                      "margin_infralinear"]:
                        margin_attrib = {"type": elem.tag}
                        if current_line:
                            margin_attrib["line"] = current_line
                        self.add_XML_child(
                            parent=chapter_child,
                            tag="margin",
                            attrib=margin_attrib,
                            text=txt.strip()
                        )

                    
            if elem.tail:
                txt = elem.tail.strip()

                if txt:
                    txt = self.extract_blank_space(txt)
                    (
                        word_content_list,
                        reconstructed_list,
                    ) = self.compute_reconstructed_words(txt)
                    for word, reconstruct in zip(word_content_list, reconstructed_list):
                        if word == "|":
                            self.add_XML_child(parent=verse_child, tag="stich")
                        else:
                            try:
                                self.add_XML_child(
                                    parent=verse_child,
                                    tag="w",
                                    attrib={"reconstructed": str(reconstruct)},
                                    text=word,
                                )
                            except UnboundLocalError:
                                self.add_XML_child(
                                    parent=line_child,
                                    tag="w",
                                    attrib={"reconstructed": str(reconstruct)},
                                    text=word,
                                )
        return unescape(
            ElementTree.tostring(
                self.clean_manuscript, encoding="unicode", method="xml"
            )
        )

    def dump(self, filename: str):
        """Parse the XML file and dump it to a XML file."""
        with open(filename, "w") as f:
            f.write(self.create_body())
