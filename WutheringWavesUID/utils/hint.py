from .waves_prefix import PREFIX

BIND_UID_HINT = f'你还没有添加ck哦, 请使用 {PREFIX}添加CK 完成绑定！'

WAVES_ERROR_CODE = {}


def error_reply(retcode: int = 0, msg: str = '') -> str:
    msg_list = [f'❌错误代码为: {retcode}']
    if msg:
        msg_list.append(f'📝错误信息: {msg}')
    elif retcode in WAVES_ERROR_CODE:
        msg_list.append(f'📝错误信息: {WAVES_ERROR_CODE[retcode]}')
    return '\n'.join(msg_list)
