import asyncio

from gdo.base.Trans import t
from gdo.core.GDT_RestOfText import GDT_RestOfText
from gdo.form.GDT_Form import GDT_Form
from gdo.form.MethodForm import MethodForm


class cowsay(MethodForm):

    @classmethod
    def gdo_trigger(cls) -> str:
        return "cowsay"

    @classmethod
    def gdo_trig(cls) -> str:
        return "cow"

    def gdo_create_form(self, form: GDT_Form) -> None:
        form.add_field(GDT_RestOfText('text').not_null())
        super().gdo_create_form(form)

    async def form_submitted(self):
        try:
            proc = await asyncio.create_subprocess_exec(
                "cowsay", self.param_value('text'),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            out, err = await proc.communicate()
            if proc.returncode != 0:
                return self.err('%s', err.decode() if err else t('err_process_return_code', (proc.returncode,)))
            cowsay_output = out.decode("utf-8", "replace")
            return self.empty(cowsay_output)
        except FileNotFoundError:
            return self.err("err_cowsay_missing")
