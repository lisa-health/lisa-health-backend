from django.http import JsonResponse
import functools


def to_json(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return JsonResponse(func(*args, **kwargs))

    return wrapper


def with_code(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        code, res = func(*args, **kwargs)
        if code and isinstance(res, str):
            return dict(code=code, msg=res)
        if not code and not isinstance(res, dict):
            return dict(code=code, data=res)
        return dict(code=code, **res)

    return wrapper


def edit_dist(word1, word2):
    m, n = map(len, (word1, word2))
    dp = [range(n + 1)] + [[i] + [0] * n for i in range(1, m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            dp[i][j] = min(
                dp[i][j - 1] + 1,
                dp[i - 1][j] + 1,
                dp[i - 1][j - 1] + (word1[i - 1].lower() != word2[j - 1].lower())
            )
    return dp[m][n]


def catch_exception(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            return 500, "Internal Server Error"

    return wrapper
