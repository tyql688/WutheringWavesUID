from ..utils.damage.register_char import register_char
from ..utils.damage.register_echo import register_echo
from ..utils.damage.register_weapon import register_weapon
from ..utils.map.damage.register import register_damage, register_rank
from ..utils.queues import init_queues
from .start import all_start  # noqa: F401

register_weapon()
register_echo()
register_damage()
register_rank()
register_char()

init_queues()
