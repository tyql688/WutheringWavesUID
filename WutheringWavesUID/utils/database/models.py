from typing import Any, List, Optional, Type, TypeVar

from sqlalchemy import and_, delete, null, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Field, col, select

from gsuid_core.utils.database.base_models import (
    Bind,
    Push,
    User,
    with_session,
)
from gsuid_core.utils.database.startup import exec_list
from gsuid_core.webconsole.mount_app import GsAdminModel, PageSchema, site

exec_list.extend(
    [
        'ALTER TABLE WavesUser ADD COLUMN platform TEXT DEFAULT ""',
        'ALTER TABLE WavesUser ADD COLUMN stamina_bg_value TEXT DEFAULT ""',
        'ALTER TABLE WavesUser ADD COLUMN bbs_sign_switch TEXT DEFAULT "off"',
    ]
)

T_WavesBind = TypeVar("T_WavesBind", bound="WavesBind")
T_WavesUser = TypeVar("T_WavesUser", bound="WavesUser")


class WavesBind(Bind, table=True):
    uid: Optional[str] = Field(default=None, title="鸣潮UID")

    @classmethod
    @with_session
    async def get_group_all_uid(
        cls: Type[T_WavesBind], session: AsyncSession, group_id: str
    ):
        """根据传入`group_id`获取该群号下所有绑定`uid`列表"""
        result = await session.scalars(
            select(cls).where(col(cls.group_id).contains(group_id))
        )
        return result.all()

    @classmethod
    async def insert_waves_uid(
        cls: Type[T_WavesBind],
        user_id: str,
        bot_id: str,
        uid: str,
        group_id: Optional[str] = None,
        lenth_limit: Optional[int] = None,
        is_digit: Optional[bool] = True,
        game_name: Optional[str] = None,
    ) -> int:
        """📝简单介绍:

            基础`Bind`类的扩展方法, 为给定的`user_id`和`bot_id`插入一条uid绑定数据

            可支持多uid的绑定, 如果绑定多个uid, 则数据库中uid列将会用`_`分割符相连接

            可以使用`cls.get_uid_list_by_game()`方法获取相应多绑定uid列表

            或者使用`cls.get_uid_by_game()`方法获得当前绑定uid（单个）

        🌱参数:

            🔹user_id (`str`):
                    传入的用户id, 例如QQ号, 一般直接取`event.user_id`

            🔹bot_id (`str`):
                    传入的bot_id, 例如`onebot`, 一般直接取`event.bot_id`

            🔹uid (`str`):
                    将要插入的uid数据

            🔹group_id (`Optional[str]`, 默认是 `None`):
                    将要插入的群组数据，为绑定uid提供群组绑定

            🔹lenth_limit (`Optional[int]`, 默认是 `None`):
                    如果有传该参数, 当uid位数不等于该参数、或uid位数为0的时候, 返回`-1`

            🔹is_digit (`Optional[bool]`, 默认是 `True`):
                    如果有传该参数, 当uid不为全数字的时候, 返回`-3`

            🔹game_name (`Optional[str]`, 默认是 `None`):
                    根据该入参寻找相应列名

        🚀使用范例:

            `await GsBind.insert_uid(qid, ev.bot_id, uid, ev.group_id, 9)`

        ✅返回值:

            🔸`int`: 如果该UID已绑定, 则返回`-2`, 成功则为`0`, 合法校验失败为`-3`或`-1`
        """
        if lenth_limit:
            if len(uid) != lenth_limit:
                return -1

        if is_digit:
            if not uid.isdigit():
                return -3
        if not uid:
            return -1

        # 第一次绑定
        if not await cls.bind_exists(user_id, bot_id):
            code = await cls.insert_data(
                user_id=user_id,
                bot_id=bot_id,
                **{"uid": uid, "group_id": group_id},
            )
            # result = await cls.select_data(user_id, bot_id)
            # await user_bind_cache.set(user_id, result)
            return code

        result = await cls.select_data(user_id, bot_id)
        # await user_bind_cache.set(user_id, result)

        uid_list = result.uid.split("_") if result and result.uid else []
        uid_list = [i for i in uid_list if i] if uid_list else []

        # 已经绑定了该UID
        res = 0 if uid not in uid_list else -2

        # 强制更新库表
        force_update = False
        if uid not in uid_list:
            uid_list.append(uid)
            force_update = True
        new_uid = "_".join(uid_list)

        group_list = result.group_id.split("_") if result and result.group_id else []
        group_list = [i for i in group_list if i] if group_list else []

        if group_id and group_id not in group_list:
            group_list.append(group_id)
            force_update = True
        new_group_id = "_".join(group_list)

        if force_update:
            await cls.update_data(
                user_id=user_id,
                bot_id=bot_id,
                **{"uid": new_uid, "group_id": new_group_id},
            )
        return res


class WavesUser(User, table=True):
    cookie: str = Field(default="", title="Cookie")
    uid: str = Field(default=None, title="鸣潮UID")
    record_id: Optional[str] = Field(default=None, title="鸣潮记录ID")
    platform: str = Field(default="", title="ck平台")
    stamina_bg_value: str = Field(default="", title="体力背景")
    bbs_sign_switch: str = Field(default="off", title="自动社区签到")

    @classmethod
    @with_session
    async def select_cookie(
        cls: Type[T_WavesUser],
        session: AsyncSession,
        user_id: str,
        uid: str,
    ) -> Optional[str]:
        sql = select(cls).where(cls.user_id == user_id, cls.uid == uid)
        result = await session.execute(sql)
        data = result.scalars().all()
        return data[0].cookie if data else None

    @classmethod
    @with_session
    async def select_data_by_cookie(
        cls: Type[T_WavesUser], session: AsyncSession, cookie: str
    ) -> Optional[T_WavesUser]:
        sql = select(cls).where(cls.cookie == cookie)
        result = await session.execute(sql)
        data = result.scalars().all()
        return data[0] if data else None

    @classmethod
    async def get_user_by_attr(
        cls: Type[T_WavesUser],
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
        cls: Type[T_WavesUser], session: AsyncSession
    ) -> List[T_WavesUser]:
        sql = select(cls).where(
            and_(
                or_(cls.status == null(), cls.status == ""),
                cls.cookie != null(),
                cls.cookie != "",
            )
        )
        result = await session.execute(sql)
        data = result.scalars().all()
        return data

    @classmethod
    @with_session
    async def get_waves_all_user2(
        cls: Type[T_WavesUser], session: AsyncSession
    ) -> List[T_WavesUser]:
        """
        获取有token的玩家。
        """
        sql = select(cls).where(
            and_(
                cls.cookie != null(),
                cls.cookie != "",
                cls.user_id != null(),
                cls.user_id != "",
            )
        )
        result = await session.execute(sql)
        data = result.scalars().all()
        return data

    @classmethod
    async def get_all_push_user_list(cls: Type[T_WavesUser]) -> List[T_WavesUser]:
        data = await cls.get_waves_all_user()
        return [user for user in data if user.push_switch != "off"]

    @classmethod
    @with_session
    async def delete_all_invalid_cookie(cls, session: AsyncSession):
        """删除所有无效缓存"""
        # 先查数量
        sql = select(cls).where(and_(or_(cls.status == "无效", cls.cookie == "")))
        result = await session.execute(sql)
        query = result.scalars().all()
        if len(query) == 0:
            return 0

        sql = delete(cls).where(and_(or_(cls.status == "无效", cls.cookie == "")))
        await session.execute(sql)
        return len(query)

    @classmethod
    @with_session
    async def delete_group_sign_switch(cls, session: AsyncSession, param_id: str):
        """删除自动签到"""
        # 先查数量
        sql = select(cls).where(and_(cls.sign_switch == param_id))
        result = await session.execute(sql)
        query = result.scalars().all()
        if len(query) == 0:
            return 0

        sql = (
            update(cls)
            .where(and_(cls.sign_switch == param_id))
            .values({"sign_switch": "off"})
        )
        await session.execute(sql)
        return len(query)


class WavesPush(Push, table=True):
    __table_args__ = {"extend_existing": True}
    bot_id: str = Field(title="平台")
    uid: str = Field(default=None, title="鸣潮UID")
    resin_push: Optional[str] = Field(
        title="体力推送",
        default="off",
        schema_extra={"json_schema_extra": {"hint": "ww开启体力推送"}},
    )
    resin_value: Optional[int] = Field(title="体力阈值", default=180)
    resin_is_push: Optional[str] = Field(title="体力是否已推送", default="off")


@site.register_admin
class WavesBindAdmin(GsAdminModel):
    pk_name = "id"
    page_schema = PageSchema(
        label="鸣潮绑定管理",
        icon="fa fa-users",
    )  # type: ignore

    # 配置管理模型
    model = WavesBind


@site.register_admin
class WavesUserAdmin(GsAdminModel):
    pk_name = "id"
    page_schema = PageSchema(
        label="鸣潮用户管理",
        icon="fa fa-users",
    )  # type: ignore

    # 配置管理模型
    model = WavesUser


@site.register_admin
class WavesPushAdmin(GsAdminModel):
    pk_name = "id"
    page_schema = PageSchema(label="鸣潮推送管理", icon="fa fa-bullhorn")  # type: ignore

    # 配置管理模型
    model = WavesPush
