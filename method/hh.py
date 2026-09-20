from gdo.base.GDT import GDT
from gdo.base.Method import Method
from gdo.base.Trans import tiso


class hh(Method):
    """Explain the Hatted Hacker abbreviation in the room's language."""

    @classmethod
    def gdo_trigger(cls) -> str:
        return 'hh'

    def gdo_parameters(self) -> list[GDT]:
        return []

    def language(self) -> str:
        if self._env_channel:
            return self._env_channel.get_lang_iso()
        if self._env_server:
            return self._env_server.get_lang_iso()
        return 'en'

    async def gdo_execute(self) -> GDT:
        return self.empty(tiso(self.language().lower(), 'msg_fun_hh'))
