# 此文件里面写整个项目公用的函数


# view返回的JsonResponse
def return_json(func):
    def wrapper(*args, **kwargs):
        json_response = func(*args, **kwargs)
