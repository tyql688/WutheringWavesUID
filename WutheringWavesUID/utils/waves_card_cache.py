from .char_info_utils import get_all_role_detail_info_list


async def get_card(uid: str):
    return await get_all_role_detail_info_list(uid)
