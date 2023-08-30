# tetris_module.py
class Tetris:
    def __init__(self):
        self._notScoring = True

    @property
    def notScoring(self):
        return self._notScoring

    @notScoring.setter
    def notScoring(self, value):
        self._notScoring = value
