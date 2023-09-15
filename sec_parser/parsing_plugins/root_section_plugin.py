from __future__ import annotations

import bs4

from sec_parser.parsing_plugins.abstract_parsing_plugin import AbstractParsingPlugin
from sec_parser.semantic_elements.semantic_elements import (
    AbstractSemanticElement,
    RootSectionElement,
)


class RootSectionPlugin(AbstractParsingPlugin):
    def transform(
        self,
        elements: list[AbstractSemanticElement],
    ) -> list[AbstractSemanticElement]:
        """
        RootSectionPlugin replaces matching elements with
        RootSection class instances.
        """
        to_be_returned: list[AbstractSemanticElement] = []
        skip_next_element = False

        for i, element in enumerate(elements):
            if skip_next_element:
                skip_next_element = False
                continue

            if self._is_document_root_section(element.html_tag.bs4):
                root_section_element = self._handle_document_root_section(
                    elements,
                    i,
                )
                to_be_returned.append(root_section_element)
                skip_next_element = True
            elif self._contains_document_root_section(element.html_tag.bs4):
                modified_element = self._remove_inner_document_root_section(element)
                to_be_returned.append(modified_element)
            else:
                to_be_returned.append(element)

        return to_be_returned

    def _is_document_root_section(self, tag: bs4.Tag) -> bool:
        return tag.name == "document-root-section"

    def _contains_document_root_section(self, tag: bs4.Tag) -> bool:
        return tag.find("document-root-section") is not None

    def _handle_document_root_section(
        self,
        elements: list[AbstractSemanticElement],
        index: int,
    ) -> AbstractSemanticElement:
        # Handle the case where the document root section is the last element
        if index + 1 >= len(elements):
            msg = "Document root section tag found but no following element."
            raise RuntimeError(msg)

        return RootSectionElement(elements[index + 1].html_tag)

    def _remove_inner_document_root_section(
        self,
        element: AbstractSemanticElement,
    ) -> AbstractSemanticElement:
        found_tag = element.html_tag.bs4.find("document-root-section")
        if not isinstance(found_tag, bs4.Tag):
            msg = f"Expected Tag, got {type(found_tag)}"
            raise TypeError(msg)
        found_tag.decompose()
        return RootSectionElement(element.html_tag)