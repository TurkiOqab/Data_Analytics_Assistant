"""Dataset analyzer for generating summaries and statistics."""

import pandas as pd


class DatasetAnalyzer:
    """Analyzes a pandas DataFrame and generates summaries."""

    def __init__(self, dataframe: pd.DataFrame):
        """
        Initialize the analyzer with a DataFrame.

        Args:
            dataframe: The pandas DataFrame to analyze.
        """
        self.df = dataframe
        self._summary_cache = None

    @property
    def row_count(self) -> int:
        """Get the number of rows in the dataset."""
        return len(self.df)

    @property
    def column_count(self) -> int:
        """Get the number of columns in the dataset."""
        return len(self.df.columns)

    @property
    def columns(self) -> list:
        """Get the list of column names."""
        return list(self.df.columns)

    def get_empty_data_stats(self) -> dict:
        """
        Get statistics about empty/null values in the dataset.

        Returns:
            Dictionary with column names as keys and empty count info as values.
        """
        empty_stats = {}
        for col in self.df.columns:
            null_count = self.df[col].isnull().sum()
            empty_count = 0
            
            # Check for empty strings in string columns
            if self.df[col].dtype == "object":
                empty_count = (self.df[col] == "").sum()
            
            total_empty = null_count + empty_count
            empty_stats[col] = {
                "null_count": int(null_count),
                "empty_string_count": int(empty_count),
                "total_empty": int(total_empty),
                "percentage": round(total_empty / self.row_count * 100, 2) if self.row_count > 0 else 0,
            }
        return empty_stats

    def get_column_types(self) -> dict:
        """
        Get the data type of each column.

        Returns:
            Dictionary mapping column names to their data types.
        """
        return {col: str(dtype) for col, dtype in self.df.dtypes.items()}

    def get_basic_stats(self) -> dict:
        """
        Get basic statistics for numerical columns.

        Returns:
            Dictionary with statistics for each numerical column.
        """
        numeric_df = self.df.select_dtypes(include=["number"])
        if numeric_df.empty:
            return {}
        
        stats = numeric_df.describe().to_dict()
        # Convert numpy types to native Python types for JSON compatibility
        for col in stats:
            stats[col] = {k: float(v) if pd.notna(v) else None for k, v in stats[col].items()}
        return stats

    def get_summary(self) -> dict:
        """
        Get a complete summary of the dataset.

        Returns:
            Dictionary containing all summary information.
        """
        if self._summary_cache is None:
            self._summary_cache = {
                "row_count": self.row_count,
                "column_count": self.column_count,
                "columns": self.columns,
                "column_types": self.get_column_types(),
                "empty_data": self.get_empty_data_stats(),
                "basic_stats": self.get_basic_stats(),
                "sample_data": self.df.head(5).to_dict(orient="records"),
            }
        return self._summary_cache

    def get_summary_text(self) -> str:
        """
        Get a formatted text summary suitable for LLM context.

        Returns:
            A formatted string describing the dataset.
        """
        summary = self.get_summary()
        
        lines = [
            "=== DATASET SUMMARY ===",
            f"Total Rows: {summary['row_count']}",
            f"Total Columns: {summary['column_count']}",
            "",
            "=== COLUMNS AND TYPES ===",
        ]
        
        for col, dtype in summary["column_types"].items():
            empty_info = summary["empty_data"][col]
            lines.append(
                f"- {col} ({dtype}): {empty_info['total_empty']} empty values "
                f"({empty_info['percentage']}%)"
            )
        
        # Add sample data
        lines.extend([
            "",
            "=== SAMPLE DATA (first 5 rows) ===",
        ])
        
        if summary["sample_data"]:
            # Create a simple text table
            cols = summary["columns"]
            lines.append(" | ".join(str(c) for c in cols))
            lines.append("-" * 50)
            for row in summary["sample_data"]:
                lines.append(" | ".join(str(row.get(c, "")) for c in cols))
        
        # Add basic stats if available
        if summary["basic_stats"]:
            lines.extend([
                "",
                "=== NUMERICAL COLUMN STATISTICS ===",
            ])
            for col, stats in summary["basic_stats"].items():
                lines.append(f"\n{col}:")
                for stat, value in stats.items():
                    if value is not None:
                        lines.append(f"  {stat}: {value:.2f}")
        
        return "\n".join(lines)
