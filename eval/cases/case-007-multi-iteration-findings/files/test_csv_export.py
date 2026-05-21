"""Tests for CSV export utilities."""

from csv_export import CsvExporter


def test_export_single_row_simple_values():
    exporter = CsvExporter()
    exporter.add_row({"name": "Alice", "age": "30"})
    result = exporter.export()
    assert result == "name,age\nAlice,30\n"


def test_export_multiple_rows():
    exporter = CsvExporter()
    exporter.add_row({"name": "Alice", "age": "30"})
    exporter.add_row({"name": "Bob", "age": "25"})
    result = exporter.export()
    assert "Alice,30" in result
    assert "Bob,25" in result


def test_export_empty():
    exporter = CsvExporter()
    assert exporter.export() == ""


def test_export_missing_field_uses_empty():
    exporter = CsvExporter()
    exporter.add_row({"name": "Alice", "age": "30"})
    exporter.add_row({"name": "Bob"})
    result = exporter.export()
    assert "Bob," in result
