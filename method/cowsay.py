import asyncio
import re

from gdo.base.Trans import t
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm
from gdo.fun.GDT_CowsayType import GDT_CowsayType


class cowsay(MethodForm):

    BLOCK_RE = re.compile(r'\x1b\[48;5;\d+m {2}')
    RESET_RE = re.compile(r'\x1b\[[0-9;]*m')

    @classmethod
    def gdo_trigger(cls) -> str:
        return "cowsay"

    @classmethod
    def gdo_trig(cls) -> str:
        return "cow"

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_CowsayType('img'))
        form.add_field(GDT_RestOfText('text').not_null())
        super().gdo_create_form(form)

    def strip_ansi(self, text: str) -> str:
        text = self.BLOCK_RE.sub('##', text)
        text = self.RESET_RE.sub('', text)
        return text

    async def form_submitted(self):
        try:
            if file := self.param_value('img'):
                args = ['-f', file, self.param_value('text')]
            else:
                args = [self.param_value('text')]
            proc = await asyncio.create_subprocess_exec(
                "cowsay", *args,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            out, err = await proc.communicate()
            if proc.returncode != 0:
                return self.err('%s', err.decode() if err else t('err_process_return_code', (proc.returncode,)))
            cowsay_output = out.decode("utf-8", "replace")
            if not self._env_server.get_connector_name() in ('bash', 'tcp'):
                cowsay_output = self.strip_ansi(cowsay_output)
            return self.empty(cowsay_output)
        except FileNotFoundError:
            return self.err("err_cowsay_missing")
