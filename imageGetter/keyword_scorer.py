# ABOUTME: Scores keywords based on proximity to image URLs in message text
# ABOUTME: Uses exponential decay, subject bonus, frequency and length multipliers

import re
import math
from collections import defaultdict


class KeywordScorer:
    def __init__(self, message_body, subject, image_url_position):
        self.body = message_body
        self.subject = subject
        self.body_lower = message_body.lower()
        self.subject_lower = subject.lower()

        # Use provided image URL position
        self.url_position = image_url_position

        # Pre-compute word positions and character indices
        self.words = message_body.split()
        self.word_positions = {}  # word -> [positions]
        self.word_count = len(self.words)

        # Build word position index
        char_pos = 0
        for i, word in enumerate(self.words):
            word_lower = word.lower()
            if word_lower not in self.word_positions:
                self.word_positions[word_lower] = []
            self.word_positions[word_lower].append((i, char_pos))
            char_pos += len(word) + 1  # +1 for space

    def score_keywords_batch(self, keywords):
        """Score all keywords efficiently in one pass"""
        scores = {}

        for keyword in keywords:
            keyword_lower = keyword.lower()

            # Fast check for existence
            if keyword_lower not in self.body_lower and keyword_lower not in self.subject_lower:
                scores[keyword] = 0
                continue

            # Calculate score
            scores[keyword] = self._calculate_score(keyword_lower)

        return scores

    def _calculate_score(self, keyword_lower):
        score = 0

        # Find all occurrences efficiently
        positions = []

        # Check for exact word matches first (fastest)
        if keyword_lower in self.word_positions:
            positions.extend([pos for _, pos in self.word_positions[keyword_lower]])

        # For multi-word keywords or partial matches
        if ' ' in keyword_lower or keyword_lower not in self.word_positions:
            start = 0
            while True:
                pos = self.body_lower.find(keyword_lower, start)
                if pos == -1:
                    break
                positions.append(pos)
                start = pos + 1

        # Calculate proximity scores using exponential decay
        if positions:
            for pos in positions:
                distance = abs(pos - self.url_position)
                # Exponential decay scoring: e^(-0.001 * distance)
                score += 100 * math.exp(-0.001 * distance)

        # Subject bonus (highest weight)
        subject_count = self.subject_lower.count(keyword_lower)
        score += subject_count * 200

        # Length and frequency multipliers
        total_occurrences = len(positions) + subject_count
        if total_occurrences > 0:
            frequency_bonus = math.sqrt(total_occurrences)
            # Natural logarithm of (1 + word_count)
            length_multiplier = 1 + math.log1p(self.word_count) / 10
            return score * frequency_bonus * length_multiplier

        return 0
