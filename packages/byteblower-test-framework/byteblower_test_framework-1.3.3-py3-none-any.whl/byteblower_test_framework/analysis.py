"""Interfaces for traffic analysis."""
# TODO: For later:
# from ._analysis.analyseraggregator import (
#     HtmlAnalyserAggregator,
#     JsonAnalyserAggregator,
# )
from ._analysis.bufferanalyser import BufferAnalyser

# `FlowAnalyser` is not really needed, but is useful for type hinting:
from ._analysis.flow_analyser import (  # noqa: F401, pylint: disable=unused-import
    FlowAnalyser,
)
from ._analysis.framelossanalyser import FrameLossAnalyser
from ._analysis.helpers import (  # noqa: F401, pylint: disable=unused-import
    include_ethernet_overhead,
)
from ._analysis.httpanalyser import HttpAnalyser, L4SHttpAnalyser
from ._analysis.latencyanalyser import (
    LatencyCDFFrameLossAnalyser,
    LatencyFrameLossAnalyser,
)
from ._analysis.voiceanalyser import VoiceAnalyser

# Export the user interfaces.
#
# Outcomes:
# * Limits import on `from byteblower_test_framework.analysis import *`
# * Exposes the interfaces in the (Sphinx) documentation
#
# NOTE
#   Exporting imported variables does not introduce them in the (Sphinx) docs.
#   For example 'DEFAULT_LOSS_PERCENTAGE', ...
#   It does introduce their name and value in `help()` of this module though.
#
__all__ = (
    # `FrameBlastingFlow`-related analysers:
    FrameLossAnalyser.__name__,
    LatencyFrameLossAnalyser.__name__,
    LatencyCDFFrameLossAnalyser.__name__,
    VoiceAnalyser.__name__,
    # `TcpFlow`-related analysers:
    HttpAnalyser.__name__,
    L4SHttpAnalyser.__name__,
    BufferAnalyser.__name__,
    # Helper functions
    include_ethernet_overhead.__name__,  # exported to include in docs
)
