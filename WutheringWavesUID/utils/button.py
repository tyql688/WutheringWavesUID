from typing import List, Literal, Optional

from gsuid_core.message_models import Button


class WavesButton(Button):
    @classmethod
    def create(
        cls,
        text: str,
        data: str,
        pressed_text: Optional[str] = None,
        style: Literal[0, 1] = 1,
        action: Literal[-1, 0, 1, 2] = -1,
        permisson: Literal[0, 1, 2, 3] = 2,
        specify_role_ids: List[str] = [],
        specify_user_ids: List[str] = [],
        unsupport_tips: str = "您的客户端暂不支持该功能, 请升级后适配...",
    ):
        from ..wutheringwaves_config import PREFIX

        # 向数据中添加前缀
        data = f"{PREFIX}{data}"

        # 创建并返回Button实例
        return cls(
            text=text,
            data=data,
            pressed_text=pressed_text,
            style=style,
            action=action,
            permisson=permisson,
            specify_role_ids=specify_role_ids,
            specify_user_ids=specify_user_ids,
            unsupport_tips=unsupport_tips,
        )


def safe(buttons: List[WavesButton]):
    button_list: List[Button] = [button for button in buttons]
    return button_list
