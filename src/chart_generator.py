"""Chart generator service that uses AI to suggest and create visualizations."""

import base64
import io
import json
import re
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from .gemini_client import GeminiClient


# Dark theme colors matching the UI
DARK_THEME = {
    'background': '#161b22',
    'card_bg': '#21262d',
    'text': '#e6edf3',
    'text_secondary': '#8b949e',
    'accent_colors': ['#58a6ff', '#3fb950', '#a371f7', '#f0883e', '#f85149'],
    'grid': '#30363d'
}


def apply_dark_theme():
    """Apply dark theme to matplotlib."""
    plt.rcParams.update({
        'figure.facecolor': DARK_THEME['background'],
        'axes.facecolor': DARK_THEME['card_bg'],
        'axes.edgecolor': DARK_THEME['grid'],
        'axes.labelcolor': DARK_THEME['text'],
        'text.color': DARK_THEME['text'],
        'xtick.color': DARK_THEME['text_secondary'],
        'ytick.color': DARK_THEME['text_secondary'],
        'grid.color': DARK_THEME['grid'],
        'legend.facecolor': DARK_THEME['card_bg'],
        'legend.edgecolor': DARK_THEME['grid'],
        'font.family': 'sans-serif',
        'font.size': 10,
    })


def fig_to_base64(fig) -> str:
    """Convert matplotlib figure to base64 string."""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=120, bbox_inches='tight', 
                facecolor=DARK_THEME['background'], edgecolor='none')
    buf.seek(0)
    img_base64 = base64.b64encode(buf.read()).decode('utf-8')
    plt.close(fig)
    return f"data:image/png;base64,{img_base64}"


class ChartGenerator:
    """Generates charts based on AI suggestions."""
    
    SUGGESTION_PROMPT = """You are a data visualization expert. Analyze this dataset and suggest exactly 3 charts that would provide the most valuable insights.

Dataset Information:
- Columns: {columns}
- Column Types: {column_types}
- Row Count: {row_count}
- Sample Data (first 5 rows): {sample_data}
- Basic Statistics: {statistics}

Return ONLY a valid JSON object with this exact structure (no markdown, no explanation):
{{
  "charts": [
    {{
      "type": "bar|line|histogram|scatter|pie",
      "title": "Descriptive title",
      "x": "column_name_for_x_axis",
      "y": "column_name_for_y_axis",
      "description": "One sentence explaining the insight"
    }}
  ]
}}

Rules:
1. For histogram, only provide "column" instead of x/y
2. For pie, provide "column" for categories and "values" for the values column
3. Only use columns that exist in the dataset
4. Choose chart types that match the data types (categorical, numerical, temporal)
5. Prioritize charts that reveal meaningful patterns or distributions"""

    def __init__(self, df: pd.DataFrame, analyzer):
        """Initialize with a DataFrame and its analyzer."""
        self.df = df
        self.analyzer = analyzer
        self.client = GeminiClient()
        apply_dark_theme()
    
    def get_ai_suggestions(self) -> list:
        """Ask AI for chart suggestions."""
        summary = self.analyzer.get_summary()
        
        # Prepare sample data
        sample = self.df.head(5).to_dict('records')
        
        prompt = self.SUGGESTION_PROMPT.format(
            columns=list(self.df.columns),
            column_types=summary['column_types'],
            row_count=summary['row_count'],
            sample_data=sample,
            statistics=summary.get('basic_stats', {})
        )
        
        try:
            response = self.client.chat(prompt, temperature=0.3)
            
            # Extract JSON from response
            # Try to find JSON in the response
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                suggestions = json.loads(json_match.group())
                return suggestions.get('charts', [])[:3]
        except Exception as e:
            print(f"AI suggestion error: {e}")
        
        # Fallback: generate default suggestions based on data types
        return self._fallback_suggestions()
    
    def _fallback_suggestions(self) -> list:
        """Generate fallback chart suggestions if AI fails."""
        charts = []
        numeric_cols = self.df.select_dtypes(include=[np.number]).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object', 'category']).columns.tolist()
        
        # Histogram for first numeric column
        if numeric_cols:
            charts.append({
                'type': 'histogram',
                'column': numeric_cols[0],
                'title': f'Distribution of {numeric_cols[0]}',
                'description': f'Shows the distribution of {numeric_cols[0]} values'
            })
        
        # Bar chart if we have categorical and numeric
        if categorical_cols and numeric_cols:
            charts.append({
                'type': 'bar',
                'x': categorical_cols[0],
                'y': numeric_cols[0],
                'title': f'{numeric_cols[0]} by {categorical_cols[0]}',
                'description': f'Compares {numeric_cols[0]} across {categorical_cols[0]} categories'
            })
        
        # Scatter plot if we have 2+ numeric columns
        if len(numeric_cols) >= 2:
            charts.append({
                'type': 'scatter',
                'x': numeric_cols[0],
                'y': numeric_cols[1],
                'title': f'{numeric_cols[0]} vs {numeric_cols[1]}',
                'description': f'Shows relationship between {numeric_cols[0]} and {numeric_cols[1]}'
            })
        
        return charts[:3]
    
    def generate_chart(self, config: dict) -> dict:
        """Generate a single chart based on configuration."""
        chart_type = config.get('type', 'histogram')
        title = config.get('title', 'Chart')
        description = config.get('description', '')
        
        try:
            fig, ax = plt.subplots(figsize=(8, 5))
            colors = DARK_THEME['accent_colors']
            
            if chart_type == 'bar':
                self._create_bar_chart(ax, config, colors[0])
            elif chart_type == 'line':
                self._create_line_chart(ax, config, colors[1])
            elif chart_type == 'histogram':
                self._create_histogram(ax, config, colors[2])
            elif chart_type == 'scatter':
                self._create_scatter_chart(ax, config, colors[3])
            elif chart_type == 'pie':
                self._create_pie_chart(ax, config, colors)
            else:
                # Default to histogram of first numeric column
                numeric_cols = self.df.select_dtypes(include=[np.number]).columns
                if len(numeric_cols) > 0:
                    ax.hist(self.df[numeric_cols[0]].dropna(), bins=20, color=colors[0], edgecolor=DARK_THEME['grid'])
                    ax.set_xlabel(numeric_cols[0])
                    ax.set_ylabel('Frequency')
            
            ax.set_title(title, fontsize=12, fontweight='bold', color=DARK_THEME['text'], pad=10)
            
            # Style adjustments
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            
            plt.tight_layout()
            
            return {
                'image': fig_to_base64(fig),
                'title': title,
                'description': description,
                'type': chart_type
            }
            
        except Exception as e:
            print(f"Chart generation error: {e}")
            return None
    
    def _create_bar_chart(self, ax, config, color):
        """Create a bar chart."""
        x_col = config.get('x')
        y_col = config.get('y')
        
        if x_col and y_col and x_col in self.df.columns and y_col in self.df.columns:
            # Group and aggregate
            grouped = self.df.groupby(x_col)[y_col].mean().head(15)  # Limit to 15 bars
            bars = ax.bar(range(len(grouped)), grouped.values, color=color, edgecolor=DARK_THEME['grid'])
            ax.set_xticks(range(len(grouped)))
            ax.set_xticklabels(grouped.index, rotation=45, ha='right')
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
    
    def _create_line_chart(self, ax, config, color):
        """Create a line chart."""
        x_col = config.get('x')
        y_col = config.get('y')
        
        if x_col and y_col and x_col in self.df.columns and y_col in self.df.columns:
            data = self.df[[x_col, y_col]].dropna().head(100)  # Limit points
            ax.plot(data[x_col], data[y_col], color=color, linewidth=2, marker='o', markersize=4)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.grid(True, alpha=0.3)
    
    def _create_histogram(self, ax, config, color):
        """Create a histogram."""
        column = config.get('column') or config.get('x')
        
        if column and column in self.df.columns:
            data = self.df[column].dropna()
            if pd.api.types.is_numeric_dtype(data):
                ax.hist(data, bins=25, color=color, edgecolor=DARK_THEME['grid'], alpha=0.8)
                ax.set_xlabel(column)
                ax.set_ylabel('Frequency')
    
    def _create_scatter_chart(self, ax, config, color):
        """Create a scatter plot."""
        x_col = config.get('x')
        y_col = config.get('y')
        
        if x_col and y_col and x_col in self.df.columns and y_col in self.df.columns:
            data = self.df[[x_col, y_col]].dropna().head(500)  # Limit points
            ax.scatter(data[x_col], data[y_col], c=color, alpha=0.6, edgecolors='none', s=30)
            ax.set_xlabel(x_col)
            ax.set_ylabel(y_col)
            ax.grid(True, alpha=0.3)
    
    def _create_pie_chart(self, ax, config, colors):
        """Create a pie chart."""
        column = config.get('column') or config.get('x')
        values_col = config.get('values') or config.get('y')
        
        if column and column in self.df.columns:
            if values_col and values_col in self.df.columns:
                data = self.df.groupby(column)[values_col].sum().head(8)
            else:
                data = self.df[column].value_counts().head(8)
            
            wedges, texts, autotexts = ax.pie(
                data.values, 
                labels=data.index, 
                colors=colors[:len(data)],
                autopct='%1.1f%%',
                pctdistance=0.8,
                textprops={'color': DARK_THEME['text'], 'fontsize': 9}
            )
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(8)
    
    def generate_charts(self) -> list:
        """Generate all suggested charts."""
        suggestions = self.get_ai_suggestions()
        charts = []
        
        for config in suggestions:
            chart = self.generate_chart(config)
            if chart:
                charts.append(chart)
        
        return charts
