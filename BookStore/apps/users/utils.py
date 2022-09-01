# 自定义一个认证成功所返回的数据
def jwt_response_payload_handler(token, user=None, request=None):

    return {
        'token': token,
        'user_id': user.id,
        'username': user.username,
    }
