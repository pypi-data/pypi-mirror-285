def get_score_emoji(score, max_score):
    if score < 0 or max_score < 0:
        return "error: score less than zero!"
    if max_score < score:
        return "error: max_score less than score!"
    result = []
    for i in range(max_score):
        if i < score:
            result.append("🟢")
        else:
            result.append("🔴")

    final_score = "".join(result)
    return final_score


def main():
    print(get_score_emoji(5, 10))


if __name__ == "__main__":
    main()
