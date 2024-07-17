from py_output_compare import highlight_diff


def test_no_difference():
    assert highlight_diff("hello", "hello") == "no different found"


def test_whitespace_difference():
    expect = "hello"
    got = "hello "
    expected_output = (
        " 🀄 White space error!\n"
        "--------------------------------------------------------------------------------\n"
        "💡 expect output: \nhello\n"
        "--------------------------------------------------------------------------------\n"
        "📃 your output is:\nhello \n"
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    )
    assert highlight_diff(expect, got) == expected_output


def test_character_difference():
    expect = "hello"
    got = "hallo"
    expected_output = (
        "--------------------------------------------------------------------------------\n"
        "diff>   👉[.#...]\n"
        "📩expect> [hello]\n"
        "🧒your's> [hallo]\n"
        "diff>   👉[.#...]\n"
        "--------------------------------------------------------------------------------\n"
        "💡 expect output: \nhello\n"
        "--------------------------------------------------------------------------------\n"
        "📃 your output is:\nhallo\n"
        "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
    )
    assert highlight_diff(expect, got).rstrip() == expected_output
