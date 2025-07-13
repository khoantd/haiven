# © 2024 Thoughtworks, Inc. | Licensed under the Apache License, Version 2.0  | See LICENSE.md file for permissions.
import os

from haiven_cli.services.file_service import FileService
from unittest.mock import patch, MagicMock, PropertyMock


class TestFileService:
    @patch("haiven_cli.services.file_service.PdfReader")
    def test_get_text_and_metadata_from_pdf(self, mock_pdf_reader):
        pdf_title = "pdf title"
        pdf_author = "pdf author"
        pdf_metadata = MagicMock()
        type(pdf_metadata).title = PropertyMock(return_value=pdf_title)
        type(pdf_metadata).author = PropertyMock(return_value=pdf_author)
        pdf_file_name = "pdf_file_path.pdf"
        pdf_file = MagicMock()
        type(pdf_file).name = PropertyMock(return_value=pdf_file_name)
        first_text = "first text"
        first_page = MagicMock()
        first_page.extract_text.return_value = first_text
        second_text = "second text"
        second_page = MagicMock()
        second_page.extract_text.return_value = second_text
        pages = [first_page, second_page]
        pdf_reader = MagicMock()
        type(pdf_reader).pages = PropertyMock(return_value=pages)
        type(pdf_reader).metadata = PropertyMock(return_value=pdf_metadata)
        mock_pdf_reader.return_value = pdf_reader
        file_service = FileService()

        text, metadas = file_service.get_text_and_metadata_from_pdf(pdf_file)

        mock_pdf_reader.assert_called_once_with(pdf_file)
        first_metadata = metadas[0]
        assert first_metadata["page"] == 1
        assert first_metadata["source"] == pdf_file_name
        assert first_metadata["title"] == pdf_title
        assert first_metadata["authors"] == [pdf_author]

        second_metadata = metadas[1]
        assert second_metadata["page"] == 2
        assert second_metadata["source"] == pdf_file_name
        assert second_metadata["title"] == pdf_title
        assert second_metadata["authors"] == [pdf_author]

        assert first_text in text
        assert second_text in text

    @patch("haiven_cli.services.file_service.PdfReader")
    def test_get_text_and_metadata_from_pdf_use_provided_pdf_source_link(
        self, mock_pdf_reader
    ):
        pdf_metadata = MagicMock()

        pdf_file_name = "pdf_file_path.pdf"
        pdf_file = MagicMock()
        type(pdf_file).name = PropertyMock(return_value=pdf_file_name)

        pages = [MagicMock()]
        pdf_reader = MagicMock()
        type(pdf_reader).pages = PropertyMock(return_value=pages)
        type(pdf_reader).metadata = PropertyMock(return_value=pdf_metadata)
        mock_pdf_reader.return_value = pdf_reader
        file_service = FileService()

        pdf_source_link = "https://pdf-source-link.com/pdf.pdf"

        text, metadas = file_service.get_text_and_metadata_from_pdf(
            pdf_file, pdf_source_link
        )

        mock_pdf_reader.assert_called_once_with(pdf_file)
        first_metadata = metadas[0]
        assert first_metadata["source"] == pdf_source_link

    @patch("haiven_cli.services.file_service.PdfReader")
    def test_get_text_and_metadata_from_pdf_use_default_title_and_authors_if_pdf_has_no_metadata(
        self, mock_pdf_reader
    ):
        pdf_file_name = "pdf_file_path.pdf"
        pdf_file = MagicMock()
        type(pdf_file).name = PropertyMock(return_value=pdf_file_name)
        first_text = "first text"
        first_page = MagicMock()
        first_page.extract_text.return_value = first_text
        second_text = "second text"
        second_page = MagicMock()
        second_page.extract_text.return_value = second_text
        pages = [first_page, second_page]
        pdf_reader = MagicMock()
        type(pdf_reader).pages = PropertyMock(return_value=pages)
        type(pdf_reader).metadata = PropertyMock(return_value=None)
        mock_pdf_reader.return_value = pdf_reader
        file_service = FileService()

        text, metadata = file_service.get_text_and_metadata_from_pdf(pdf_file)

        mock_pdf_reader.assert_called_once_with(pdf_file)
        first_metadata = metadata[0]
        assert first_metadata["page"] == 1
        assert first_metadata["source"] == pdf_file_name
        assert first_metadata["title"] == "Pdf File Path"
        assert first_metadata["authors"] == []

        second_metadata = metadata[1]
        assert second_metadata["page"] == 2
        assert second_metadata["source"] == pdf_file_name
        assert second_metadata["title"] == "Pdf File Path"
        assert second_metadata["authors"] == []

        assert first_text in text
        assert second_text in text

    @patch("haiven_cli.services.file_service.PdfReader")
    def test_get_text_and_metadata_from_pdf_use_default_title_and_authors_if_pdf_has_no_tile_nor_authors(
        self, mock_pdf_reader
    ):
        pdf_file_name = "pdf_file_path.pdf"
        pdf_file = MagicMock()
        type(pdf_file).name = PropertyMock(return_value=pdf_file_name)
        first_text = "first text"
        first_page = MagicMock()
        first_page.extract_text.return_value = first_text
        second_text = "second text"
        second_page = MagicMock()
        second_page.extract_text.return_value = second_text
        pages = [first_page, second_page]
        pdf_reader = MagicMock()
        type(pdf_reader).pages = PropertyMock(return_value=pages)
        pdf_metadata = MagicMock()
        type(pdf_metadata).title = PropertyMock(return_value=None)
        type(pdf_metadata).author = PropertyMock(return_value=None)
        type(pdf_reader).metadata = PropertyMock(return_value=pdf_metadata)
        mock_pdf_reader.return_value = pdf_reader
        file_service = FileService()

        text, metadata = file_service.get_text_and_metadata_from_pdf(pdf_file)

        mock_pdf_reader.assert_called_once_with(pdf_file)
        first_metadata = metadata[0]
        assert first_metadata["page"] == 1
        assert first_metadata["source"] == pdf_file_name
        assert first_metadata["title"] == "Pdf File Path"
        assert first_metadata["authors"] == []

        second_metadata = metadata[1]
        assert second_metadata["page"] == 2
        assert second_metadata["source"] == pdf_file_name
        assert second_metadata["title"] == "Pdf File Path"
        assert second_metadata["authors"] == []

        assert first_text in text
        assert second_text in text

    @patch("haiven_cli.services.file_service.os")
    def test_get_files_path_from_directory(self, mock_os):
        source_dir = "source_dir"
        file_path = "file_path"
        mock_os.walk.return_value = [(source_dir, [], [file_path])]
        mock_os.path.join.return_value = os.path.join(source_dir, file_path)
        file_service = FileService()

        files = file_service.get_files_path_from_directory(source_dir)

        assert len(files) == 1
        assert files[0] == f"{source_dir}/{file_path}"
        mock_os.walk.assert_called_once_with(source_dir)

    def test_write_metadata_file(self):
        key = "a key"
        title = "a title"
        description = "a description"
        source = "a source"
        path = "a path"
        provider = "a provider"
        sample_question = "a sample question"

        metadata = {
            "key": key,
            "title": title,
            "description": description,
            "source": source,
            "path": path,
            "provider": provider,
            "sample_question": sample_question,
        }
        metadata_file_path = "test_metadata.yml"

        file_service = FileService()
        file_service.write_metadata_file(metadata, metadata_file_path)

        expected_metadata_file_content = f"""---
key: {key}
title: {title}
description: {description}
source: {source}
path: {path}
provider: {provider}
sample_question: {sample_question}
---
"""
        with open(metadata_file_path, "r") as f:
            metadata_file_content = f.read()
            assert metadata_file_content == expected_metadata_file_content

        os.remove(metadata_file_path)
