import maialib.maiacore as mc
from enum import Enum

__all__ = ['getSampleScorePath', 'SampleScore', 'setScoreEditorApp', 'getScoreEditorApp', 'openScore', 'getXmlSamplesDirPath']

def setScoreEditorApp(executableFullPath: str) -> None: ...
def getScoreEditorApp() -> str: ...
def openScore(score: mc.Score) -> None: ...

class SampleScore(Enum):
    Bach_Cello_Suite_1: str
    Beethoven_Symphony_5th: str
    Chopin_Fantasie_Impromptu: str
    Dvorak_Symphony_9_mov_4: str
    Mahler_Symphony_8_Finale: str
    Mozart_Requiem_Introitus: str
    Strauss_Also_Sprach_Zarathustra: str

def getSampleScorePath(sampleEnum: SampleScore) -> str: ...
def getXmlSamplesDirPath() -> str: ...
