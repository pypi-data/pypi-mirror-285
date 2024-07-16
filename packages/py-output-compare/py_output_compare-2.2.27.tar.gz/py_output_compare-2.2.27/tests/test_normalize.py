from py_output_compare import (
    normalize_output,
    remove_space_tab_newline,
)


def test_normalize_output():
    assert normalize_output(" Hello World \n") == "helloworld"
    assert normalize_output("  \tHello\nWorld\t ") == "helloworld"
    assert normalize_output("123 \t 456\n") == "123456"
    assert normalize_output("") == ""
    assert normalize_output("  ") == ""


def test_normalize_output_no_lower():
    assert remove_space_tab_newline(" Hello World \n") == "HelloWorld"
    assert remove_space_tab_newline("  \tHello\nWorld\t ") == "HelloWorld"
    assert remove_space_tab_newline("123 \t 456\n") == "123456"
    assert remove_space_tab_newline("") == ""
    assert remove_space_tab_newline("  ") == ""
