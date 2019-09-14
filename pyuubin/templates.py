from typing import Any, Dict
from uuid import uuid4

from jinja2 import DictLoader
from jinja2.exceptions import TemplateNotFound
from jinja2.sandbox import ImmutableSandboxedEnvironment


class Templates:
    """Helper for rendering templates."""

    _templates_dict: Dict[str, str]
    _environment: ImmutableSandboxedEnvironment

    def __init__(self, templates_dict: Dict[str, str]):
        self._templates_dict = templates_dict
        self._environment = ImmutableSandboxedEnvironment(loader=DictLoader(self._templates_dict), enable_async=True)

    def __setitem__(self, key: str, template: str):
        self._templates_dict[key] = template

    def __delitem__(self, key: str):
        del self._templates_dict[key]

    def _html_template_out_of_parameters(self, parameters: Dict[str, Any]):
        body = "\n".join("<dt>{key}</dt><dd>{{{{ {key} }}}}</dd>".format(key=key) for key in parameters.keys())
        return f'<!DOCTYPE html><html><head><meta charset="UTF-8"></head><body><dl>{body}</dl></body></html>'

    async def _render_without_template(self, parameters: Dict[str, Any]) -> str:
        template_id = str(uuid4())
        self[template_id] = self._html_template_out_of_parameters(parameters)

        rendered = await self.render(template_id, parameters)

        del self[template_id]
        return rendered

    async def render(self, template_id: str, parameters: Dict[str, Any]) -> str:
        """Render the template with given template_id

        Args:
            template_id (str): template id
            parameters (Dict[str, Any]): dictionary of variables to be put in the template

        Returns:
            str: [description]
        """
        try:
            template = self._environment.get_template(template_id)
            return await template.render_async(**parameters)
        except TemplateNotFound:
            new_params = {"missing_template_id": template_id, **parameters}
            return await self._render_without_template(new_params)
