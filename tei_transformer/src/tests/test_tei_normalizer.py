"""Tests that the TEI transformer behaves as expected.

RTL displays is broken on VS Code, so if you're working with VSCode, expect to be confused
regarding the order of the hebrew letter (I am very confused as well).
"""
import unittest
from pathlib import Path
from tei_transformer import TEITransformer


TEST_FOLDER_DATA = Path(__file__).resolve().parent / "test_data"


class TestNormalizeTEIParser(unittest.TestCase):
    """Tests that the normalization of the TEI parser works as expected.
    """
    def setUp(self) -> None:
        """Set up the test.
        """
        self.tei_transformer = TEITransformer(TEST_FOLDER_DATA / "ms_to_clean_standard_verse.xml")

    def test_extract_blank_spaces(self):
        """Given a text with blank spaces, tests that the blank spaces are properly extracted.
        """
        text = "[    ]ב̊שער̊"
        self.assertEqual(self.tei_transformer.extract_blank_space(text),
                        "<blank orient='horizontal' span='4'/>ב̊שער̊")

    def test_extract_reconstructed_text(self):
        """Given a text with blank spaces, tests that the blank spaces are properly extracted.
        """
        text = "[    ב̊שער̊]"
        print(self.tei_transformer.extract_blank_space(text))
        self.assertEqual(self.tei_transformer.extract_blank_space(text),
                        "<blank orient='horizontal' span='4'/>ב̊שער̊")

    def test_reconstruct_word(self):
        """Given that there is no bracket, tests that the word is wrapped correctly.
        """
        word = "אני"
        expected_reconstructed_word = f"<g type='reconstructed'>אני</g>"
        self.assertEqual(
            self.tei_transformer.reconstruct_word(word),
            expected_reconstructed_word
        )

    def test_checked_match_bracket(self):
        """Check that in the case where brackets are not matched, False is returned.
        """
        word = "כ]ל[ה"
        self.assertFalse(self.tei_transformer.check_matched_bracket(word))

    def test_reconstruct_word_bracket_left(self):
        """Given a word with a bracket on the left, tests that the word is wrapped correctly."""
        word = "[אני"
        expected_reconstructed_word = f"<g type='reconstructed'>אני</g>"
        self.assertEqual(
            self.tei_transformer.reconstruct_word(word),
            expected_reconstructed_word)
        
    def test_reconstruct_word_bracket_right(self):
        """Given a word with a bracket on the right, tests that the word is wrapped correctly."""
        word = "אני]"
        expected_reconstructed_word = f"<g type='reconstructed'>אני</g>"
        self.assertEqual(
            self.tei_transformer.reconstruct_word(word),
            expected_reconstructed_word)
        
    def test_reconstruct_word_bracket_within_reconstruct(self):
        """Given a word with several reconstructed letters, tests that the word is wrapped correctly."""
        word = "ב]ת̊ו̊[רת]"
        expected_reconstructed_word = f"<g type='reconstructed'>ב</g>ת̊ו̊<g type='reconstructed'>רת</g>"
        self.assertEqual(
            self.tei_transformer.reconstruct_word(word),
            expected_reconstructed_word)
        
    def test_reconstruct_word_external_reconstruct(self):
        """Given a word with several reconstructed letters, tests that the word is wrapped correctly.
        """
        word = "כ]ל[ה"
        expected_reconstructed_word = f"<g type='reconstructed'>כ</g>ל<g type='reconstructed'>ה</g>"
        self.assertEqual(
            self.tei_transformer.reconstruct_word(word),
            expected_reconstructed_word)
        
    def test_reconstruct_text_blank(self):
        """Given a text with an empy blank, test that the word is wrapped correctly.
        """
        words = """<blank orient='horizontal' span='6'/>ב̊שער̊[∙]"""
        parsed_words = self.tei_transformer.compute_reconstructed_words(words)[0]
        self.assertEqual(
            "".join(parsed_words),
            "<blank orient='horizontal' span='6'/>ב̊שער̊<g type='reconstructed'>∙</g>"
        )

    def test_chapter_normalizer(self):
        """Given a chapter number with the string 'Siracide', test that the chapter number is
        properly extracted.
        """
        chapter_to_normalize = "Siracide 1"
        expected_normalized_chapter = '1'
        self.assertEqual(
            self.tei_transformer.chap_normalizer(chapter_to_normalize),
            expected_normalized_chapter)

    def test_verse_normalizer_verse_num(self):
        """Given a verse number, tests that the verse normalizer behaves as expected.
        """
        verse_to_normalize = "1"
        expected_normalized_verse = ['1']
        self.assertEqual(
            self.tei_transformer.chap_verse_normalizer(verse_to_normalize),
            expected_normalized_verse)
        
    # def test_verse_normalizer_verse_letter(self):
    #     """Given a verse in the format number_letter (such as 1a), tests that the verse normalizer
    #     behaves as expected.
    #     """
    #     verse_to_normalize = "1a"
    #     expected_normalized_verse = '1a'
    #     self.assertEqual(
    #         self.tei_transformer.chap_verse_normalizer(verse_to_normalize),
    #         expected_normalized_verse)

    def test_verse_normalizer_chapter_verse(self):
        """Given a verse in the format chapter:number (such as 1:1), tests that the
        verse normalizer behaves as expected.
        """
        verse_to_normalize = "1:2"
        expected_normalized_verse = ["1", "2"]
        self.assertEqual(
            self.tei_transformer.chap_verse_normalizer(verse_to_normalize),
            expected_normalized_verse)
        
    # def test_verse_normalizer_chapter_verse_letter(self):
    #     """Given a verse in the format chapter:number_letter (such as 1:1a), tests that the
    #     verse normalizer behaves as expected.
    #     """
    #     verse_to_normalize = "1:2a"
    #     expected_normalized_verse = ["1", "2a"]
    #     self.assertEqual(
    #         self.tei_transformer.chap_verse_normalizer(verse_to_normalize),
    #         expected_normalized_verse
    #     )

    def test_create_body_standard_verse(self):
        """Given a poorly formatted XML file, tests it is properly cleaned up.
        """
        expected_body = """<root><ms>Manuscript 11QPs<div type="chap" n="11Q5, col. XXI"><div type="verse" n="13"><line n="11" /><w reconstructed="0">אני</w><w reconstructed="0">נער</w><w reconstructed="0">בטרם</w><w reconstructed="0">תעיתי</w><w reconstructed="0">ובקשתיה</w></div></div></ms></root>"""
        manuscript = TEITransformer(TEST_FOLDER_DATA / "ms_to_clean_standard_verse.xml")
        created_body = manuscript.create_body()
        self.assertEqual(
            expected_body,
            created_body
        )

    def test_create_body_chapter_verse_combined(self):
        """Tests that creating the body of the manuscript behaves as expected when chapters and verses
        are specified within the same XML tag.
        """
        expected_body = """<root><ms>Manuscript C<div type="folio" n="TS 12.867 recto"><div type="chap" n="3"><div type="verse" n="14"><line n="1" /><w reconstructed="0">צדקת</w><w reconstructed="0">אב</w><w reconstructed="0">אל</w><w reconstructed="0">תשכח</w><stych /><w reconstructed="0">ו̇תחת</w><line n="2" /><w reconstructed="0">ענו̇תו</w><w reconstructed="1">תתנצ̇<g type='reconstructed'>ב:</g></w></div></div></div></ms></root>"""
        manuscript = TEITransformer(TEST_FOLDER_DATA / "ms_to_clean_combined_chapter_verse.xml")
        created_body = manuscript.create_body()
        self.assertEqual(
            expected_body,
            created_body
        )

    def test_create_body_blank_space(self):
        """Given a manuscript with blank space, tests that the body is properly created.
        """
        expected_body = """<root><ms>Manuscript F<div type="chap" n="31"><div type="folio" n="TS AS 213.17 recto"><div type="verse" n="24"><line n="5" /><w reconstructed="0"><blank orient='horizontal' span='28'/></w><w reconstructed="1">ב̊שער̊<g type='reconstructed'>∙</g></w><stych /><w reconstructed="0"><blank orient='horizontal' span='36'/></w></div></div></div></ms></root>"""
        manuscript = TEITransformer(TEST_FOLDER_DATA / "ms_to_clean_blank_space.xml")
        # created_body = manuscript.create_body()
        manuscript.dump("test.xml")
        # self.assertEqual(
        #     expected_body,
        #     created_body
        # )   

    def test_create_body_complex_reconstructed(self):
        """Given a manuscript with a complex reconstruction pattern, tests that the body is
        properly created.
        """
        expected_body = """<root><ms>Manuscript M<div type="chap" n="39"><div type="verse" n="4ab"><line n="4" /><w reconstructed="0">זה</w><w reconstructed="0">קץ</w><w reconstructed="0">כל</w><w reconstructed="1"><g type='reconstructed'>בני</g></w><w reconstructed="1"><g type='reconstructed'>אד</g>ם̊</w><stych /><stych /><w reconstructed="1"><g type='reconstructed'>ומה</g></w><w reconstructed="1"><g type='reconstructed'>תמאס</g></w><w reconstructed="1"><g type='reconstructed'>ב</g>ת̊ו̊<g type='reconstructed'>רת</g></w><w reconstructed="1">עליו<g type='reconstructed'>ן</g></w></div></div></ms></root>"""
        manuscript = TEITransformer(TEST_FOLDER_DATA / "ms_to_clean_reconstructed.xml")
        created_body = manuscript.create_body()
        self.assertEqual(expected_body, created_body)

    def test_create_body_nested_folios(self):
        """Given a manuscript with complex nested folios, tests that the body is properly created.
        """
        expected_body = """<root><ms>Manuscript F<div type="chap" n="32"><div type="verse" n="1"><line n="16" folio="TS AS 213.17 recto" /><w reconstructed="0">ראש</w><w reconstructed="0">סמוך</w><w reconstructed="0">א‍ל</w><w reconstructed="0">תותר׃</w><w reconstructed="0">ובראש</w><w reconstructed="0">עשירים</w><w reconstructed="0">א‍ל</w><w reconstructed="0">תסתורה</w><w reconstructed="0">והיה</w><w reconstructed="0">לך</w><w reconstructed="0" /><w reconstructed="0">כאחד</w><w reconstructed="0">מהם׃</w></div><div type="verse" n="16"><line n="11" folio="TS AS 213.17 verso" /><w reconstructed="1"><g type='reconstructed'>ירא</g></w><w reconstructed="1"><g type='reconstructed'>ייי</g></w><w reconstructed="1"><g type='reconstructed'>י</g>ב̊ין</w><w reconstructed="0">משפט∙</w><w reconstructed="0">ות{ת}חבולות</w><w reconstructed="1">מנ̇ש̊ף̊<g type='reconstructed'></g></w><w reconstructed="1"><g type='reconstructed'>
</g></w><w reconstructed="1"><g type='reconstructed'>יוציא׃</g></w></div></div><div type="chap" n="33"><div type="verse" n="2"><line n="21" folio="TS AS 213.17 verso" /><w reconstructed="0">לא</w><w reconstructed="0">יחכם</w><w reconstructed="0">שונא</w><w reconstructed="0">תורה∙</w><w reconstructed="0">ומתמוטט</w><w reconstructed="0">כמסערה</w><w reconstructed="0">׃</w></div></div></ms></root>"""
        manuscript = TEITransformer(TEST_FOLDER_DATA / "ms_to_clean_several_folio.xml")
        created_body = manuscript.create_body()
        self.assertEqual(expected_body, created_body)


if __name__ == "__main__":
    unittest.main()