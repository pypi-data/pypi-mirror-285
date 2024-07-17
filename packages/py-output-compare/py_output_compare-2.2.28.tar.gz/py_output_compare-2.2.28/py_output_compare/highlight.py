from py_output_compare.normalize_file_output import (
    remove_space_tab_newline,
    replace_space_tab_newline,
)


def spot_char_diff(expect_input, got_input):
    # have error when spot thai character like ชี will make it go .. so, it will not be fully align
    max_len = max(len(expect_input), len(got_input))
    result = []

    result.append("diff>   👉[")
    for i in range(max_len):
        char1 = expect_input[i] if i < len(expect_input) else ""
        char2 = got_input[i] if i < len(got_input) else ""
        if char1 == char2:
            result.append(".")
        else:
            result.append("#")
    result.append("]")

    diff_result = "".join(result)
    return diff_result


def highlight_diff(expect_input, got_input):

    if expect_input == got_input:
        return "no different found"

    norm_expect_input = remove_space_tab_newline(expect_input)
    norm_got_input = remove_space_tab_newline(got_input)

    final_word = []
    final_word.append("-" * 80)

    file_have_error_in_space = norm_expect_input == norm_got_input

    if file_have_error_in_space:
        final_word.append("👾: space/newline error! ⚪:space 😶:tab 🌍:newline")
        norm_expect_input = replace_space_tab_newline(expect_input)
        norm_got_input = replace_space_tab_newline(got_input)

    diff_result = spot_char_diff(norm_expect_input, norm_got_input)

    # print compare normalize text
    final_word.append(diff_result)
    final_word.append(f"📩expect> [{norm_expect_input}]")
    final_word.append(f"🧒your's> [{norm_got_input}]")
    final_word.append(diff_result)

    # print real output
    final_word.append("-" * 80)
    final_word.append("💡 expect output: ")
    final_word.append(expect_input)
    final_word.append("-" * 80)
    final_word.append("📃 your output is:")
    final_word.append(got_input)
    final_word.append("~" * 80)
    final_output = "\n".join(final_word)
    return final_output


def main():
    print(highlight_diff("he llo", "hello"))
    print(highlight_diff("hello\n", "hello"))
    print(highlight_diff("\nhello", "hello"))
    print(highlight_diff("hell o", "h ell o"))


if __name__ == "__main__":
    main()
