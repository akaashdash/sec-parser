from __future__ import annotations

from typing import TYPE_CHECKING, Callable

from sec_parser.parsing_engine.abstract_parser import (
    AbstractSemanticElementParser,
)
from sec_parser.parsing_engine.html_parsers.root_tag_parser import (
    AbstractHtmlTagParser,
    RootTagParser,
)
from sec_parser.parsing_plugins.irrelevant_element_plugin import IrrelevantElementPlugin
from sec_parser.parsing_plugins.root_section_plugin import RootSectionPlugin
from sec_parser.parsing_plugins.text_plugin import TextPlugin
from sec_parser.parsing_plugins.title_plugin import TitlePlugin
from sec_parser.semantic_elements.semantic_elements import (
    UndeterminedElement,
)

if TYPE_CHECKING:
    from sec_parser.parsing_plugins.abstract_parsing_plugin import AbstractParsingPlugin
    from sec_parser.semantic_elements.abstract_semantic_elements import (
        AbstractSemanticElement,
    )


class SecParser(AbstractSemanticElementParser):
    def __init__(
        self,
        create_plugins: Callable[[], list[AbstractParsingPlugin]] | None = None,
        *,
        root_tag_parser: AbstractHtmlTagParser | None = None,
        max_iterations: int | None = None,
    ) -> None:
        self.create_plugins: Callable = create_plugins or self.create_default_plugins
        self._root_tag_parser = root_tag_parser or RootTagParser()
        self._max_iterations = max_iterations or 10

    def create_default_plugins(
        self,
    ) -> list[AbstractParsingPlugin]:
        return [
            RootSectionPlugin(),
            TitlePlugin(),
            TextPlugin(),
            IrrelevantElementPlugin(),
        ]

    def parse(self, html: str) -> list[AbstractSemanticElement]:
        plugins = self.create_plugins()

        # The parsing process is designed to handle the primarily
        # flat structure of SEC filings. Hence, our focus is on
        # the root tags of the HTML document.
        root_tags = self._root_tag_parser.parse(html)

        elements: list[AbstractSemanticElement] = [
            UndeterminedElement(tag) for tag in root_tags
        ]

        for plugin in plugins:
            elements = plugin.transform(elements)

        return elements