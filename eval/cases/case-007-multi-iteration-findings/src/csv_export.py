"""CSV export utilities."""


class CsvExporter:
    """Export data rows as CSV text."""

    def __init__(self):
        self._headers = None
        self._rows = []

    def add_row(self, row: dict) -> None:
        """Add a data row to the export.

        Args:
            row: Dictionary mapping column names to values.
        """
        if self._headers is None:
            self._headers = list(row.keys())
        self._rows.append(row)

    def export(self) -> str:
        """Export all rows as a CSV string.

        Returns:
            CSV-formatted string.
        """
        if not self._headers:
            return ""
        lines = [",".join(self._headers)]
        for row in self._rows:
            values = [str(row.get(h, "")) for h in self._headers]
            lines.append(",".join(values))
        return "\n".join(lines) + "\n"

    def export_to_file(self, path: str) -> None:
        """Write CSV output to a file.

        Args:
            path: Destination file path.
        """
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.export())
