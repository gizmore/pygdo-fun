import random

from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.core.GDT_RestOfText import GDT_RestOfText


class world_domination(Method):
    """A harmless port of GWF3 Dog's world-domination joke."""

    RESPONSES = (
        'msg_fun_world_domination_bizarro',
        'msg_fun_world_domination_failed',
        'msg_fun_world_domination_syntax',
        'msg_fun_world_domination_no_contact',
        'msg_fun_world_domination_running',
        'msg_fun_world_domination_slots',
    )

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'world_domination'

    def gdo_parameters(self) -> list[GDT]:
        return [
            GDT_RestOfText('evil_plan').not_null(),
        ]

    def gdo_execute(self) -> GDT:
        # The submitted plan is deliberately never parsed or evaluated. The
        # old Dog command was a joke, and this port keeps it that way.
        response = random.choice(self.RESPONSES)
        if response == 'msg_fun_world_domination_slots':
            return self.reply(response, (self._env_user.render_name(),))
        return self.reply(response)
