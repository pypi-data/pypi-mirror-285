"""
MIT License

Copyright (c) 20234 Isabelle Phoebe <izzy@uwu.gal>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Any, Final, TypedDict

from httpcord.enums import InteractionResponseType
from httpcord.func_protocol import AutocompleteFunc, CommandFunc
from httpcord.interaction import CommandResponse, Interaction
from httpcord.types import TYPE_CONVERSION_TABLE, AutocompleteChoice


__all__: Final[tuple[str, ...]] = (
    "Command",
)


class CommandOptionsDict(TypedDict):
    name: str
    description: str
    type: int  # TODO: types
    required: bool
    autocomplete: bool


class CommandDict(TypedDict):
    name: str
    type: int  # TODO: types
    intergration_types: list[int]  # TODO: types
    contexts: list[int]  # TODO: types
    description: str
    options: list[CommandOptionsDict]


class Command:
    __slots__: Final[tuple[str, ...]] = (
        "_func",
        "_name",
        "_description",
        "_autocompletes",
    )

    def __init__(
        self,
        func: CommandFunc,
        *,
        name: str,
        description: str | None = None,
        autocompletes: dict[str, AutocompleteFunc] | None = None,
    ) -> None:
        self._func: CommandFunc = func
        self._name: str = name
        self._description: str = description or "--"
        self._autocompletes: dict[str, AutocompleteFunc] = autocompletes or {}

    async def invoke(self, interaction: Interaction, **kwargs: Any) -> CommandResponse:
        return await self._func(interaction, **kwargs)

    def to_dict(self) -> CommandDict:
        raw_options = list(self._func.__annotations__.items())[1:-1]
        options: list[CommandOptionsDict] = []
        for raw_option in raw_options:
            required = raw_option[0] not in (getattr(self._func, "__kwdefaults__") or {}).keys()
            options.append(CommandOptionsDict(
                name=raw_option[0],
                description="...",
                type=TYPE_CONVERSION_TABLE[raw_option[1]],
                required=required,
                autocomplete=raw_option[0] in self._autocompletes.keys(),
            ))
        return CommandDict(
            name=self._name,
            type=1,
            intergration_types=[0, 1],
            contexts=[0, 1, 2],
            description=self._description,
            options=options,
        )


class CommandData:
    __slots__: Final[tuple[str, ...]] = (
        "command",
        "options",
        "options_formatted",
        "interaction",
    )

    def __init__(
        self,
        command: Command,
        options: list[dict[str, Any]],
        interaction: Interaction,
    ) -> None:
        self.command: Command = command
        self.options: dict[str, Any] = {o['name']: o for o in options}
        self.options_formatted: dict[str, Any] = {o['name']: o['value'] for o in options}
        self.interaction: Interaction = interaction


class AutocompleteResponse:
    __slotst__: Final[tuple[str, ...]] = (
        "choices",
    )

    def __init__(self, choices: list[AutocompleteChoice]) -> None:
        self.choices: list[AutocompleteChoice] = choices

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": InteractionResponseType.APPLICATION_COMMAND_AUTOCOMPLETE_RESULT,
            "data": {
                "choices": [
                    {
                        "name": choice["name"],
                        "value": choice["value"],
                    }
                    for choice in self.choices
                ][:25],
            },
        }
