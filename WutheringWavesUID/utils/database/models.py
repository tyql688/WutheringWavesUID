import random
from typing import Optional, Any, Type, Literal

from sqlmodel import Field

from gsuid_core.utils.database.base_models import Bind, User, T_User
from gsuid_core.webconsole.mount_app import PageSchema, GsAdminModel, site


class WavesBind(Bind, table=True):
    uid: Optional[str] = Field(default=None, title='鸣潮UID')


class WavesUser(User, table=True):
    cookie: str = Field(default='', title='Cookie')
    uid: Optional[str] = Field(default=None, title='鸣潮UID')
    record_id: Optional[str] = Field(default=None, title='鸣潮记录ID')

    @classmethod
    async def get_user_by_attr(
        cls: Type[T_User],
        user_id: str,
        bot_id: str,
        attr_key: str,
        attr_value: str,
    ) -> Optional[Any]:
        user_list = await cls.select_data_list(user_id=user_id, bot_id=bot_id)
        if not user_list:
            return None
        for user in user_list:
            if getattr(user, attr_key) != attr_value:
                continue
            return user

    @classmethod
    async def get_waves_random_cookie(cls: Type[T_User], uid: str) -> Optional[str]:
        # 有绑定自己CK 并且该CK有效的前提下，优先使用自己CK
        ck = await WavesUser.get_user_cookie_by_uid(uid)
        if ck:
            return ck

        # 公共ck 随机一个
        user_list = await cls.get_all_user()
        ck_list = [user.cookie for user in user_list if user.cookie]
        if len(ck_list) > 0:
            return random.choices(ck_list, k=1)[0]

    @classmethod
    async def get_ck(cls: Type[T_User], uid: str, mode: Literal['OWNER', 'RANDOM'] = 'RANDOM') -> Optional[str]:
        if mode == 'RANDOM':
            return await cls.get_waves_random_cookie(uid)
        else:
            return await cls.get_user_cookie_by_uid(uid)


@site.register_admin
class WavesBindAdmin(GsAdminModel):
    pk_name = 'id'
    page_schema = PageSchema(
        label='鸣潮绑定管理',
        icon='fa fa-users',
    )  # type: ignore

    # 配置管理模型
    model = WavesBind


@site.register_admin
class WavesUserAdmin(GsAdminModel):
    pk_name = 'id'
    page_schema = PageSchema(
        label='鸣潮用户管理',
        icon='fa fa-users',
    )  # type: ignore

    # 配置管理模型
    model = WavesUser
