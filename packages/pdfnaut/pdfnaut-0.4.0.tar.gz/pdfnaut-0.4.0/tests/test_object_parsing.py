# Unit tests for tokenizing the COS syntax in PDFs.

from __future__ import annotations

from typing import cast

from pdfnaut.cos import PdfTokenizer
from pdfnaut.objects import PdfName, PdfIndirectRef, PdfHexString, PdfNull, PdfComment


def test_null_and_boolean() -> None:
    lexer = PdfTokenizer(b"null true false")
    tokens = list(lexer)

    assert isinstance(tokens[0], PdfNull)
    assert tokens[1] is True and tokens[2] is False


def test_numeric() -> None:
    lexer = PdfTokenizer(b"-1 +25 46 -32.591 +52.871 3.1451")
    tokens = list(lexer)

    assert tokens == [-1, 25, 46, -32.591, 52.871, 3.1451]


def test_name_object() -> None:
    lexer = PdfTokenizer(b"/Type /SomeR@ndomK*y /Lime#20Green / /F#23")
    tokens = list(lexer)
    assert tokens == [PdfName(b"Type"), PdfName(b"SomeR@ndomK*y"), PdfName(b"Lime Green"), 
                      PdfName(b""), PdfName(b"F#")]


def test_literal_string() -> None:
    # Basic string
    lexer = PdfTokenizer(b"(The quick brown fox jumps over the lazy dog.)")
    assert lexer.next_token() == b"The quick brown fox jumps over the lazy dog."

    # String with nested parentheses
    lexer = PdfTokenizer(b"(This is a string with a (few) nested ((parentheses)))")
    assert lexer.next_token() == b"This is a string with a (few) nested ((parentheses))"

    # String continued in next line
    lexer = PdfTokenizer(b"(This is a string that is \r\n"
                                b"continued on the next line)")
    assert lexer.next_token() == b"This is a string that is \r\ncontinued on the next line"

    # String ending with a \ at the EOL and followed next line
    lexer = PdfTokenizer(b"(This is a string \\\r\nwith no newlines.)")
    assert lexer.next_token() == b"This is a string with no newlines."

    # String with escape characters
    lexer = PdfTokenizer(b"(This is a string with a \\t tab character and a \\053 plus.))")
    assert lexer.next_token() == b"This is a string with a \t tab character and a + plus."


def test_hex_string() -> None:
    lexer = PdfTokenizer(b"<A5B2FF><6868ADE>")
    tokens = cast("list[PdfHexString]", list(lexer))

    assert tokens[0].raw == b"A5B2FF" and tokens[1].raw == b"6868ADE0" 


def test_dictionary() -> None:
    lexer = PdfTokenizer(b"""<< /Type /Catalog /Metadata 2 0 R /Pages 3 0 R >>""")
    assert lexer.next_token() == { 
        "Type": PdfName(b"Catalog"), 
        "Metadata": PdfIndirectRef(2, 0), 
        "Pages": PdfIndirectRef(3, 0) 
    }


def test_comment() -> None:
    # This also counts as an EOL test
    lexer = PdfTokenizer(b"% This is a comment\r\n"
                                b"12 % This is another comment\r"
                                b"25\n")
    assert isinstance(com := next(lexer), PdfComment) \
        and com.value == b" This is a comment"
    assert next(lexer) == 12
    assert isinstance(com := next(lexer), PdfComment) and \
        com.value == b" This is another comment"
    assert next(lexer) == 25

    lexer = PdfTokenizer(b"% This is a comment ending with \\r\r")
    assert isinstance(com := lexer.next_token(), PdfComment) \
        and com.value == b" This is a comment ending with \\r"


def test_array() -> None:
    # Simple array
    lexer = PdfTokenizer(b"[45 <</Size 40>> (42)]") 
    assert lexer.next_token() == [45, {"Size": 40}, b"42"]
    
    # Nested array
    lexer = PdfTokenizer(b"[/XYZ [45 32 76] /Great]")
    assert lexer.next_token() == [PdfName(b"XYZ"), [45, 32, 76], PdfName(b"Great")]

def test_indirect_reference() -> None:
    lexer = PdfTokenizer(b"2 0 R")
    assert lexer.next_token() == PdfIndirectRef(2, 0)
