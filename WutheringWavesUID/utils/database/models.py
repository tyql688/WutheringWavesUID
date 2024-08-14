from typing import Optional, Any, Type, List

from sqlalchemy import and_, or_, null
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, select

from gsuid_core.utils.database.base_models import Bind, User, T_User, with_session
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
    @with_session
    async def get_waves_all_user(
        cls: Type[T_User], session: AsyncSession
    ) -> List[T_User]:
        sql = select(cls).where(
            and_(
                or_(
                    cls.status == null(),
                    cls.status == ''
                ), cls.cookie != null(), cls.cookie != ''
            )
        )
        result = await session.execute(sql)
        data = result.scalars().all()
        return data


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
