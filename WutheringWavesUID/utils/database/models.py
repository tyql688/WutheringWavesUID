from typing import Optional

from sqlmodel import Field

from gsuid_core.utils.database.base_models import Bind, User
from gsuid_core.webconsole.mount_app import PageSchema, GsAdminModel, site


class WavesBind(Bind, table=True):
    uid: Optional[str] = Field(default=None, title='鸣潮UID')


class WavesUser(User, table=True):
    uid: Optional[str] = Field(default=None, title='鸣潮UID')
    tap_uid: Optional[str] = Field(default=None, title='TapTapUID')


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
