import tiktoken

ENC = tiktoken.get_encoding("o200k_base")


def count_token(text: str) -> int:
    ids = ENC.encode(text)
    return len(ids)


def clean_text(text: str) -> str:
    text = text.strip()
    while "  " in text:
        text = text.replace("  ", " ")
    while "\n\n" in text:
        text = text.replace("\n\n", "\n")
    return text


def sub_tokenize(text: str, from_idx: int, end_idx: int) -> str:
    ids = ENC.encode(text)
    ret = try_decode(text, ids, from_idx, end_idx)
    return ret


def try_decode(text, ids, s, t):
    for i in range(min(max(1, t - s - 1), 100)):
        try:
            ret = ENC.decode(ids[s : t - i])
            assert ret in text
            return (s, t - i), ret
        except:
            pass
