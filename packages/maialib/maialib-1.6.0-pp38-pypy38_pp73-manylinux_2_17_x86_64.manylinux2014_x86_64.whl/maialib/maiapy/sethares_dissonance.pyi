import pandas as pd
import plotly
import plotly.graph_objects as go
from maialib import maiacore as mc
from typing import Callable

__all__ = ['plotSetharesDissonanceCurve', 'plotScoreSetharesDissonance', 'plotChordDyadsSetharesDissonanceHeatmap']

def plotSetharesDissonanceCurve(fundamentalFreq: float = 440, numPartials: int = 6, ratioLowLimit: float = 1.0, ratioHighLimit: float = 2.3, ratioStepIncrement: float = 0.001, amplCallback: Callable[[list[float]], list[float]] | None = None) -> tuple[go.Figure, pd.DataFrame]: ...
def plotScoreSetharesDissonance(score: mc.Score, plotType: str = 'line', lineShape: str = 'linear', numPartialsPerNote: int = 6, useMinModel: bool = True, amplCallback: Callable[[list[float]], list[float]] | None = None, dissCallback: Callable[[list[float]], float] | None = None, **kwargs) -> tuple[go.Figure, pd.DataFrame]: ...
def plotChordDyadsSetharesDissonanceHeatmap(chord: mc.Chord, numPartialsPerNote: int = 6, useMinModel: bool = True, amplCallback: Callable[[list[float]], list[float]] | None = None, dissonanceThreshold: float = 0.1, dissonanceDecimalPoint: int = 2) -> tuple[plotly.graph_objs._figure.Figure, pd.DataFrame]: ...
