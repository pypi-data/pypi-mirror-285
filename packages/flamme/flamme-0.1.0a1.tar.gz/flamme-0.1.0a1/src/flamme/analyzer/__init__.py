r"""Contain DataFrame analyzers."""

from __future__ import annotations

__all__ = [
    "BaseAnalyzer",
    "ChoiceAnalyzer",
    "ColumnContinuousAdvancedAnalyzer",
    "ColumnContinuousAnalyzer",
    "ColumnContinuousTemporalDriftAnalyzer",
    "ColumnDiscreteAnalyzer",
    "ColumnSubsetAnalyzer",
    "ColumnTemporalContinuousAnalyzer",
    "ColumnTemporalDiscreteAnalyzer",
    "ColumnTemporalDriftDiscreteAnalyzer",
    "ColumnTemporalNullValueAnalyzer",
    "ContentAnalyzer",
    "DataFrameSummaryAnalyzer",
    "DataTypeAnalyzer",
    "DuplicatedRowAnalyzer",
    "MappingAnalyzer",
    "MarkdownAnalyzer",
    "MostFrequentValuesAnalyzer",
    "NullValueAnalyzer",
    "TableOfContentAnalyzer",
    "TemporalNullValueAnalyzer",
    "TemporalRowCountAnalyzer",
    "TransformAnalyzer",
    "is_analyzer_config",
    "setup_analyzer",
]

from flamme.analyzer.base import BaseAnalyzer, is_analyzer_config, setup_analyzer
from flamme.analyzer.choice import ChoiceAnalyzer
from flamme.analyzer.column import ColumnSubsetAnalyzer
from flamme.analyzer.content import ContentAnalyzer
from flamme.analyzer.continuous import ColumnContinuousAnalyzer
from flamme.analyzer.continuous_advanced import ColumnContinuousAdvancedAnalyzer
from flamme.analyzer.continuous_drift import ColumnContinuousTemporalDriftAnalyzer
from flamme.analyzer.continuous_temp import ColumnTemporalContinuousAnalyzer
from flamme.analyzer.count_rows import TemporalRowCountAnalyzer
from flamme.analyzer.discrete import ColumnDiscreteAnalyzer
from flamme.analyzer.discrete_drift import ColumnTemporalDriftDiscreteAnalyzer
from flamme.analyzer.discrete_temp import ColumnTemporalDiscreteAnalyzer
from flamme.analyzer.dtype import DataTypeAnalyzer
from flamme.analyzer.duplicate import DuplicatedRowAnalyzer
from flamme.analyzer.frame_summary import DataFrameSummaryAnalyzer
from flamme.analyzer.mapping import MappingAnalyzer
from flamme.analyzer.markdown import MarkdownAnalyzer
from flamme.analyzer.most_frequent import MostFrequentValuesAnalyzer
from flamme.analyzer.null import NullValueAnalyzer
from flamme.analyzer.null_temp import TemporalNullValueAnalyzer
from flamme.analyzer.null_temp_col import ColumnTemporalNullValueAnalyzer
from flamme.analyzer.toc import TableOfContentAnalyzer
from flamme.analyzer.transform import TransformAnalyzer
