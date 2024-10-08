from collections import Counter
from dataclasses import dataclass

from analysis import analyze

@dataclass
class Abstract:
    """Wikipedia abstract"""
    ID: int
    title: str
    body: str
    msg_id: str

    @property
    def fulltext(self):
        return ' '.join([self.title, self.body])

    def analyze(self):
        self.term_frequencies = Counter(analyze(self.fulltext))

    def term_frequency(self, term):
        return self.term_frequencies.get(term, 0)
