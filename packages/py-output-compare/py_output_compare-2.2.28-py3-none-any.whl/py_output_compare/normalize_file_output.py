def normalize_output(output):
    return output.strip().lower().replace("\n", "").replace(" ", "").replace("\t", "")


def remove_space_tab_newline(output):
    return output.replace(" ", "").replace("\t", "").replace("\n", "")


def replace_space_tab_newline(output):
    return output.replace(" ", "⚪").replace("\t", "😶").replace("\n", "🌍")
