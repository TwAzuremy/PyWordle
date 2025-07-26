from colorama import *
import argparse
import config
from wordle import Wordle
from ui import UI
import random
import time
from collections import Counter
import math

init(autoreset=True)


class AIPlayer:
    """Base AI player class"""
    
    def __init__(self, name, difficulty, word_list):
        self.name = name
        self.difficulty = difficulty
        self.word_list = word_list
        self.guess_history = []
        self.constraints = {
            'confirmed_positions': {},
            'required_letters': set(),
            'forbidden_letters': set(),
            'wrong_positions': {},
            'letter_counts': {}
        }
    
    def reset(self):
        """Reset AI state"""
        self.guess_history = []
        self.constraints = {
            'confirmed_positions': {},
            'required_letters': set(),
            'forbidden_letters': set(),
            'wrong_positions': {},
            'letter_counts': {}
        }
    
    def make_guess(self, word_length, remaining_attempts):
        """Make guess based on difficulty strategy"""
        raise NotImplementedError
    
    def update_constraints(self, guess, result):
        """Update constraints based on guess result"""
        self.guess_history.append(guess)
        
        letter_feedback = {}
        for i, letter_result in enumerate(result):
            letter = list(letter_result.keys())[0]
            color = list(letter_result.values())[0]
            
            if letter not in letter_feedback:
                letter_feedback[letter] = {'positions': [], 'colors': []}
            letter_feedback[letter]['positions'].append(i)
            letter_feedback[letter]['colors'].append(color)
        
        for letter, feedback in letter_feedback.items():
            green_positions = [pos for pos, color in zip(feedback['positions'], feedback['colors']) if color == Fore.GREEN]
            yellow_positions = [pos for pos, color in zip(feedback['positions'], feedback['colors']) if color == Fore.YELLOW]
            red_positions = [pos for pos, color in zip(feedback['positions'], feedback['colors']) if color == Fore.RED]
            
            # Handle green letters (confirmed positions)
            for pos in green_positions:
                self.constraints['confirmed_positions'][pos] = letter
                self.constraints['required_letters'].add(letter)
            
            # Handle yellow letters (wrong position but letter exists)
            if yellow_positions:
                self.constraints['required_letters'].add(letter)
                if letter not in self.constraints['wrong_positions']:
                    self.constraints['wrong_positions'][letter] = set()
                self.constraints['wrong_positions'][letter].update(yellow_positions)
            
            # Handle red letters
            if red_positions and not green_positions and not yellow_positions:
                self.constraints['forbidden_letters'].add(letter)
            elif red_positions:
                if letter not in self.constraints['wrong_positions']:
                    self.constraints['wrong_positions'][letter] = set()
                self.constraints['wrong_positions'][letter].update(red_positions)


class BeginnerAI(AIPlayer):
    """Easy AI: Simple word guessing"""
    
    def __init__(self, word_list):
        super().__init__("Easy AI", "beginner", word_list)
    
    def make_guess(self, word_length, remaining_attempts):
        """Basic AI strategy: fundamental reasoning with hint algorithm"""
        if not self.guess_history:
            # First guess, choose words with common letter combinations
            common_starters = [word for word in self.word_list[word_length] 
                             if self._has_common_letters(word)]
            return random.choice(common_starters) if common_starters else random.choice(self.word_list[word_length])
        
        # Filter candidate words based on constraints
        candidates = []
        for word in self.word_list[word_length]:
            if word in self.guess_history:
                continue
            if self._is_valid_candidate(word):
                candidates.append(word)
        
        if not candidates:
            remaining_words = [w for w in self.word_list[word_length] if w not in self.guess_history]
            return random.choice(remaining_words) if remaining_words else random.choice(self.word_list[word_length])
        
        # Simple scoring: prioritize words containing more unknown letters
        scored_candidates = []
        for word in candidates:
            score = self._calculate_basic_score(word)
            scored_candidates.append((word, score))
        
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        top_candidates = [word for word, _ in scored_candidates[:max(1, len(scored_candidates) // 3)]]
        return random.choice(top_candidates)
    
    def _has_common_letters(self, word):
        """Check if word contains common letters"""
        common_letters = set('ETAOINSHRDL')
        return len(set(word) & common_letters) >= 3
    
    def _is_valid_candidate(self, word):
        """Check if word satisfies all constraints"""
        # Check confirmed positions
        for pos, letter in self.constraints['confirmed_positions'].items():
            if word[pos] != letter:
                return False
        
        # Check required letters
        word_letters = set(word)
        if not self.constraints['required_letters'].issubset(word_letters):
            return False
        
        # Check forbidden letters
        if word_letters.intersection(self.constraints['forbidden_letters']):
            return False
        
        # Check wrong positions
        for letter, forbidden_positions in self.constraints['wrong_positions'].items():
            for pos in forbidden_positions:
                if pos < len(word) and word[pos] == letter:
                    return False
        
        return True
    
    def _calculate_basic_score(self, word):
        """Calculate basic score"""
        score = 0
        unique_letters = len(set(word))
        score += unique_letters * 10
        
        # Prioritize common letters
        common_letters = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'
        for letter in word:
            if letter in common_letters:
                score += (26 - common_letters.index(letter))
        
        return score


class IntermediateAI(AIPlayer):
    """Medium AI: Smart word picking"""
    
    def __init__(self, word_list):
        super().__init__("Medium AI", "intermediate", word_list)
        self.letter_frequency = self._calculate_letter_frequency(word_list)
    
    def _calculate_letter_frequency(self, word_list):
        """Calculate letter frequency"""
        frequency = Counter()
        for length_words in word_list.values():
            for word in length_words:
                frequency.update(word)
        return frequency
    
    def make_guess(self, word_length, remaining_attempts):
        """Intermediate AI strategy: information theory and frequency analysis"""
        if not self.guess_history:
            # First guess, choose word with maximum information value
            return self._get_max_info_word(word_length)
        
        candidates = self._get_valid_candidates(word_length)
        
        if not candidates:
            remaining_words = [w for w in self.word_list[word_length] if w not in self.guess_history]
            return random.choice(remaining_words) if remaining_words else random.choice(self.word_list[word_length])
        
        # If few candidates remain, choose directly
        if len(candidates) <= 2:
            return random.choice(candidates)
        
        # Use information gain to select best guess
        if remaining_attempts > 2:
            # Enough attempts remaining, prioritize high information gain words
            return self._get_max_info_gain_word(candidates, word_length)
        else:
            # Few attempts left, prioritize possible answers
            return self._get_best_answer_candidate(candidates)
    
    def _get_max_info_word(self, word_length):
        """Get word with maximum information value"""
        # Select words with most common and non-repeating letters
        best_word = None
        best_score = -1
        
        for word in self.word_list[word_length]:
            if len(set(word)) == len(word):  # No repeat letters
                score = sum(self.letter_frequency[letter] for letter in word)
                if score > best_score:
                    best_score = score
                    best_word = word
        
        return best_word if best_word else random.choice(self.word_list[word_length])
    
    def _get_valid_candidates(self, word_length):
        """Get all valid candidate words"""
        candidates = []
        for word in self.word_list[word_length]:
            if word in self.guess_history:
                continue
            if self._is_valid_candidate_advanced(word):
                candidates.append(word)
        return candidates
    
    def _is_valid_candidate_advanced(self, word):
        """Advanced candidate validation"""
        # Basic validations
        if not self._is_valid_candidate_basic(word):
            return False
        
        # Letter count validations
        for letter, count_constraint in self.constraints['letter_counts'].items():
            actual_count = word.count(letter)
            min_count = count_constraint.get('min', 0)
            max_count = count_constraint.get('max', float('inf'))
            if actual_count < min_count or actual_count > max_count:
                return False
        
        return True
    
    def _is_valid_candidate_basic(self, word):
        """Basic candidate validation"""
        # Check confirmed positions
        for pos, letter in self.constraints['confirmed_positions'].items():
            if word[pos] != letter:
                return False
        
        # Check required letters
        word_letters = set(word)
        if not self.constraints['required_letters'].issubset(word_letters):
            return False
        
        # Check forbidden letters
        if word_letters.intersection(self.constraints['forbidden_letters']):
            return False
        
        # Check wrong positions
        for letter, forbidden_positions in self.constraints['wrong_positions'].items():
            for pos in forbidden_positions:
                if pos < len(word) and word[pos] == letter:
                    return False
        
        return True
    
    def _get_max_info_gain_word(self, candidates, word_length):
        """Select word with maximum information gain"""
        if len(candidates) <= 5:
            return random.choice(candidates)
        
        # Simplified information gain calculation
        best_word = None
        best_score = -1
        
        # From all words, not limited to candidates only
        test_words = self.word_list[word_length]
        
        for test_word in test_words[:min(50, len(test_words))]:  # Limit computation
            if test_word in self.guess_history:
                continue
            
            score = self._calculate_info_gain(test_word, candidates)
            if score > best_score:
                best_score = score
                best_word = test_word
        
        return best_word if best_word else random.choice(candidates)
    
    def _calculate_info_gain(self, test_word, candidates):
        """Calculate information gain (simplified)"""
        # Simulate this word's partition of the candidate set
        pattern_groups = {}
        
        for candidate in candidates[:min(20, len(candidates))]:  # Limit computation
            pattern = self._get_pattern(test_word, candidate)
            pattern_key = str(pattern)
            if pattern_key not in pattern_groups:
                pattern_groups[pattern_key] = 0
            pattern_groups[pattern_key] += 1
        
        # Calculate entropy
        total = sum(pattern_groups.values())
        entropy = 0
        for count in pattern_groups.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        
        return entropy
    
    def _get_pattern(self, guess, target):
        """Get pattern of guess word against target word"""
        pattern = []
        target_chars = list(target)
        
        # First pass: mark exact matches
        for i in range(len(guess)):
            if guess[i] == target[i]:
                pattern.append('G')  # Green
                target_chars[i] = None
            else:
                pattern.append('?')
        
        # Second pass: mark partial matches
        for i in range(len(guess)):
            if pattern[i] == '?':
                if guess[i] in target_chars:
                    pattern[i] = 'Y'  # Yellow
                    target_chars[target_chars.index(guess[i])] = None
                else:
                    pattern[i] = 'R'  # Red
        
        return pattern
    
    def _get_best_answer_candidate(self, candidates):
        """Select most likely answer candidate"""
        # Based on letter frequency and position probability
        scored_candidates = []
        for word in candidates:
            score = self._calculate_answer_score(word)
            scored_candidates.append((word, score))
        
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[0][0]
    
    def _calculate_answer_score(self, word):
        """Calculate answer score"""
        score = 0
        
        # Letter frequency score
        for letter in word:
            score += self.letter_frequency.get(letter, 0)
        
        # Position score (confirmed position letters get high score)
        for pos, letter in self.constraints['confirmed_positions'].items():
            if pos < len(word) and word[pos] == letter:
                score += 100
        
        # Score for containing required letters
        for letter in self.constraints['required_letters']:
            if letter in word:
                score += 50
        
        return score


class AdvancedAI(AIPlayer):
    """Hard AI: Very smart word picking with advanced algorithms"""
    
    def __init__(self, word_list):
        super().__init__("Hard AI", "advanced", word_list)
        self.letter_frequency = self._calculate_letter_frequency(word_list)
        self.position_frequency = self._calculate_position_frequency(word_list)
        self.bigram_frequency = self._calculate_bigram_frequency(word_list)
        self.word_scores = self._precompute_word_scores(word_list)
        self.opponent_patterns = []  # Record opponent's guess patterns
        self.entropy_cache = {}  # Cache for entropy calculations
        self.simulation_depth = 3  # Depth for minimax-like simulations
    
    def _calculate_letter_frequency(self, word_list):
        """Calculate letter frequency with position weighting"""
        frequency = Counter()
        position_weighted = Counter()
        
        for length_words in word_list.values():
            for word in length_words:
                for i, letter in enumerate(word):
                    frequency[letter] += 1
                    # Weight letters by position importance (middle positions slightly less important)
                    position_weight = 1.0 if i == 0 or i == len(word)-1 else 0.9
                    position_weighted[letter] += position_weight
        
        # Combine raw frequency with position weighting
        combined = Counter()
        for letter in frequency:
            combined[letter] = frequency[letter] * 0.7 + position_weighted[letter] * 0.3
        
        return combined
    
    def _calculate_position_frequency(self, word_list):
        """Calculate letter frequency at each position with normalization"""
        position_freq = {}
        for length_words in word_list.values():
            for word in length_words:
                for i, letter in enumerate(word):
                    if i not in position_freq:
                        position_freq[i] = Counter()
                    position_freq[i][letter] += 1
        
        # Normalize frequencies to probabilities
        for pos in position_freq:
            total = sum(position_freq[pos].values())
            for letter in position_freq[pos]:
                position_freq[pos][letter] = position_freq[pos][letter] / total
        
        return position_freq
    
    def _calculate_bigram_frequency(self, word_list):
        """Calculate bigram (two-letter combination) frequency"""
        bigram_freq = Counter()
        for length_words in word_list.values():
            for word in length_words:
                for i in range(len(word) - 1):
                    bigram = word[i:i+2]
                    bigram_freq[bigram] += 1
        return bigram_freq
    
    def _precompute_word_scores(self, word_list):
        """Precompute base scores for all words"""
        word_scores = {}
        for length, words in word_list.items():
            word_scores[length] = {}
            for word in words:
                score = self._calculate_base_word_score(word)
                word_scores[length][word] = score
        return word_scores
    
    def _calculate_base_word_score(self, word):
        """Calculate base score for a word considering multiple factors"""
        score = 0
        
        # Letter frequency score
        unique_letters = set(word)
        for letter in unique_letters:
            score += self.letter_frequency.get(letter, 0) * 0.3
        
        # Position frequency score
        for i, letter in enumerate(word):
            if i in self.position_frequency:
                score += self.position_frequency[i].get(letter, 0) * 100
        
        # Bigram score
        for i in range(len(word) - 1):
            bigram = word[i:i+2]
            score += self.bigram_frequency.get(bigram, 0) * 0.1
        
        # Diversity bonus (prefer words with unique letters)
        diversity_bonus = len(unique_letters) * 5
        score += diversity_bonus
        
        # Common word patterns bonus
        if self._has_good_patterns(word):
            score += 10
        
        return score
    
    def _has_good_patterns(self, word):
        """Check if word has linguistically good patterns"""
        good_patterns = ['ST', 'ER', 'ED', 'ING', 'ION', 'TH', 'HE', 'AN', 'RE', 'ND']
        return any(pattern in word for pattern in good_patterns)
    
    def make_guess(self, word_length, remaining_attempts):
        """Advanced AI strategy: multi-layered decision making with adaptive algorithms"""
        if not self.guess_history:
            # First guess: use sophisticated opening strategy
            return self._get_optimal_opening(word_length)
        
        candidates = self._get_valid_candidates_advanced(word_length)
        
        if not candidates:
            remaining_words = [w for w in self.word_list[word_length] if w not in self.guess_history]
            return random.choice(remaining_words) if remaining_words else random.choice(self.word_list[word_length])
        
        # Adaptive strategy based on game state
        if len(candidates) == 1:
            return candidates[0]
        elif len(candidates) <= 3:
            return self._get_endgame_guess(candidates, remaining_attempts)
        elif remaining_attempts > 3:
            # Early/mid game: maximize information gain with strategic considerations
            return self._get_strategic_midgame_guess(candidates, word_length, remaining_attempts)
        elif remaining_attempts > 1:
            # Late game: balance between information and direct guessing
            return self._get_lategame_guess(candidates, word_length, remaining_attempts)
        else:
            # Final attempt: must guess the answer
            return self._get_best_final_guess(candidates)
    
    def _get_optimal_opening(self, word_length):
        """Sophisticated opening strategy using multiple criteria"""
        # Get top candidates based on precomputed scores
        scored_words = []
        for word in self.word_list[word_length]:
            base_score = self.word_scores[word_length].get(word, 0)
            
            # Additional opening-specific scoring
            opening_bonus = 0
            
            # Prefer words with no repeated letters for maximum information
            if len(set(word)) == len(word):
                opening_bonus += 50
            
            # Prefer words with vowels in good positions
            vowels = set('AEIOU')
            for i, letter in enumerate(word):
                if letter in vowels:
                    if i == 1 or i == 2:  # Good vowel positions
                        opening_bonus += 15
                    elif i == 0:  # Starting vowel
                        opening_bonus += 10
            
            # Prefer words with common consonant clusters
            consonant_clusters = ['ST', 'TR', 'CR', 'BR', 'FL', 'PL', 'CL']
            for cluster in consonant_clusters:
                if cluster in word:
                    opening_bonus += 8
            
            # Avoid overly common words that might be too obvious
            common_words = ['ABOUT', 'HOUSE', 'WORLD', 'PLACE', 'THINK', 'GREAT', 'FIRST']
            if word in common_words:
                opening_bonus -= 20
            
            total_score = base_score + opening_bonus
            scored_words.append((word, total_score))
        
        # Sort and select from top candidates with some randomness
        scored_words.sort(key=lambda x: x[1], reverse=True)
        top_count = min(10, max(3, len(scored_words) // 20))
        top_words = [word for word, _ in scored_words[:top_count]]
        
        return random.choice(top_words)
    
    def _get_strategic_midgame_guess(self, candidates, word_length, remaining_attempts):
        """Strategic midgame decision using enhanced algorithms"""
        # Use improved Monte Carlo Tree Search with deeper analysis
        best_guess = self._enhanced_monte_carlo_search(candidates, word_length, remaining_attempts)
        
        if best_guess:
            return best_guess
        
        # Fallback to information theory approach
        return self._get_max_information_gain_word(candidates, word_length)
    
    def _enhanced_monte_carlo_search(self, candidates, word_length, remaining_attempts):
        """Enhanced Monte Carlo Tree Search with better evaluation"""
        if len(candidates) > 50:  # Limit computation for large candidate sets
            candidates = candidates[:50]
        
        # Consider both candidate words and non-candidate words for guessing
        possible_guesses = list(set(candidates + 
                                  [w for w in self.word_list[word_length][:100] 
                                   if w not in self.guess_history]))
        
        best_guess = None
        best_score = float('-inf')
        simulations_per_guess = max(20, min(100, 1000 // len(possible_guesses)))
        
        for guess in possible_guesses:
            total_score = 0
            
            # Run multiple simulations for this guess
            for _ in range(simulations_per_guess):
                score = self._simulate_guess_with_lookahead(guess, candidates, remaining_attempts)
                total_score += score
            
            avg_score = total_score / simulations_per_guess
            
            # Add bonus for words that are actual candidates
            if guess in candidates:
                avg_score += 50
            
            if avg_score > best_score:
                best_score = avg_score
                best_guess = guess
        
        return best_guess
    
    def _simulate_guess_with_lookahead(self, guess, candidates, remaining_attempts):
        """Simulate guess outcome with lookahead"""
        if not candidates:
            return 0
        
        # Randomly select a candidate as the "true answer"
        true_answer = random.choice(candidates)
        pattern = self._get_detailed_pattern(guess, true_answer)
        
        # Calculate how this pattern would narrow down candidates
        new_candidates = []
        for candidate in candidates:
            if self._pattern_matches(guess, candidate, pattern):
                new_candidates.append(candidate)
        
        # Base score: reduction in candidate space
        reduction_score = len(candidates) - len(new_candidates)
        
        # Perfect guess bonus
        if guess == true_answer:
            return 1000
        
        # Penalty for last attempt without correct guess
        if remaining_attempts == 1 and guess != true_answer:
            return -1000
        
        # Lookahead: consider what happens after this guess
        if remaining_attempts > 1 and len(new_candidates) > 1:
            # Simulate one more level
            future_score = self._evaluate_future_position(new_candidates, remaining_attempts - 1)
            reduction_score += future_score * 0.3
        
        return reduction_score
    
    def _evaluate_future_position(self, candidates, remaining_attempts):
        """Evaluate the quality of a future position"""
        if len(candidates) <= 1:
            return 100  # Good position
        
        if remaining_attempts == 0:
            return -100  # Bad position
        
        # Estimate how many guesses needed to solve from this position
        estimated_guesses = math.log2(len(candidates)) if len(candidates) > 1 else 1
        
        if estimated_guesses <= remaining_attempts:
            return 50  # Solvable position
        else:
            return -50  # Difficult position
    
    def _get_max_information_gain_word(self, candidates, word_length):
        """Get word with maximum information gain using improved entropy calculation"""
        if len(candidates) <= 3:
            return random.choice(candidates)
        
        best_word = None
        best_entropy = -1
        
        # Test both candidates and some non-candidates
        test_words = list(set(candidates + 
                            [w for w in self.word_list[word_length][:50] 
                             if w not in self.guess_history]))
        
        for test_word in test_words:
            entropy = self._calculate_entropy_fast(test_word, candidates)
            
            # Bonus for being a candidate
            if test_word in candidates:
                entropy += 0.5
            
            if entropy > best_entropy:
                best_entropy = entropy
                best_word = test_word
        
        return best_word if best_word else random.choice(candidates)
    
    def _calculate_entropy_fast(self, guess, candidates):
        """Fast entropy calculation with caching"""
        cache_key = (guess, tuple(sorted(candidates)))
        if cache_key in self.entropy_cache:
            return self.entropy_cache[cache_key]
        
        # Group candidates by their response patterns
        pattern_groups = {}
        for candidate in candidates:
            pattern = self._get_pattern_signature(guess, candidate)
            if pattern not in pattern_groups:
                pattern_groups[pattern] = 0
            pattern_groups[pattern] += 1
        
        # Calculate entropy
        total = len(candidates)
        entropy = 0
        for count in pattern_groups.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        
        # Cache result
        if len(self.entropy_cache) < 1000:  # Limit cache size
            self.entropy_cache[cache_key] = entropy
        
        return entropy
    
    def _get_pattern_signature(self, guess, target):
        """Get a compact signature for the pattern"""
        pattern = []
        target_chars = list(target)
        
        # Mark exact matches first
        for i in range(len(guess)):
            if guess[i] == target[i]:
                pattern.append('G')
                target_chars[i] = None
            else:
                pattern.append('?')
        
        # Mark partial matches
        for i in range(len(guess)):
            if pattern[i] == '?':
                if guess[i] in target_chars:
                    pattern[i] = 'Y'
                    target_chars[target_chars.index(guess[i])] = None
                else:
                    pattern[i] = 'R'
        
        return ''.join(pattern)
    
    def _get_endgame_guess(self, candidates, remaining_attempts):
        """Endgame strategy when few candidates remain"""
        if len(candidates) == 1:
            return candidates[0]
        
        if remaining_attempts == 1:
            # Must guess - pick the most likely candidate
            return self._get_most_likely_candidate(candidates)
        
        # With 2-3 candidates and multiple attempts, use minimax-like approach
        best_guess = None
        best_score = float('-inf')
        
        for guess in candidates:
            worst_case_score = float('inf')
            
            # For each possible answer, see worst case scenario
            for true_answer in candidates:
                if guess == true_answer:
                    score = 1000  # Perfect
                else:
                    # See how many candidates remain after this guess
                    pattern = self._get_detailed_pattern(guess, true_answer)
                    remaining = sum(1 for c in candidates 
                                  if self._pattern_matches(guess, c, pattern))
                    score = -remaining  # Fewer remaining is better
                
                worst_case_score = min(worst_case_score, score)
            
            if worst_case_score > best_score:
                best_score = worst_case_score
                best_guess = guess
        
        return best_guess if best_guess else random.choice(candidates)
    
    def _get_most_likely_candidate(self, candidates):
        """Get the most likely candidate based on linguistic patterns"""
        scored_candidates = []
        
        for candidate in candidates:
            score = self.word_scores[len(candidate)].get(candidate, 0)
            
            # Additional scoring based on constraints satisfaction
            constraint_score = 0
            
            # Bonus for perfectly fitting confirmed positions
            for pos, letter in self.constraints['confirmed_positions'].items():
                if pos < len(candidate) and candidate[pos] == letter:
                    constraint_score += 100
            
            # Bonus for containing all required letters
            if self.constraints['required_letters'].issubset(set(candidate)):
                constraint_score += 50
            
            # Penalty for common letters in wrong positions
            for letter, wrong_positions in self.constraints['wrong_positions'].items():
                for pos in wrong_positions:
                    if pos < len(candidate) and candidate[pos] == letter:
                        constraint_score -= 200  # Heavy penalty
            
            total_score = score + constraint_score
            scored_candidates.append((candidate, total_score))
        
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[0][0]
    
    def _get_lategame_guess(self, candidates, word_length, remaining_attempts):
        """Late game strategy balancing information and direct guessing"""
        if len(candidates) <= remaining_attempts:
            # Can afford to guess directly
            return self._get_most_likely_candidate(candidates)
        
        # Need to narrow down more - use information gain but prefer candidates
        info_guess = self._get_max_information_gain_word(candidates, word_length)
        
        # If the info gain guess is a candidate, use it
        if info_guess in candidates:
            return info_guess
        
        # Otherwise, balance between info gain and direct guessing
        if random.random() < 0.7:  # 70% chance to use info gain
            return info_guess
        else:
            return self._get_most_likely_candidate(candidates)
    
    def _get_valid_candidates_advanced(self, word_length):
        """Get advanced valid candidate words"""
        candidates = []
        for word in self.word_list[word_length]:
            if word in self.guess_history:
                continue
            if self._is_valid_candidate_expert(word):
                candidates.append(word)
        return candidates
    
    def _is_valid_candidate_expert(self, word):
        """Expert-level candidate validation"""
        # All basic validations
        if not self._is_valid_candidate_comprehensive(word):
            return False
        
        # Advanced pattern matching validation
        return self._advanced_pattern_check(word)
    
    def _is_valid_candidate_comprehensive(self, word):
        """Comprehensive candidate validation"""
        # Check confirmed positions
        for pos, letter in self.constraints['confirmed_positions'].items():
            if word[pos] != letter:
                return False
        
        # Check required letters
        word_letters = set(word)
        if not self.constraints['required_letters'].issubset(word_letters):
            return False
        
        # Check forbidden letters
        if word_letters.intersection(self.constraints['forbidden_letters']):
            return False
        
        # Check wrong positions
        for letter, forbidden_positions in self.constraints['wrong_positions'].items():
            for pos in forbidden_positions:
                if pos < len(word) and word[pos] == letter:
                    return False
        
        # Check letter counts
        for letter, count_constraint in self.constraints['letter_counts'].items():
            actual_count = word.count(letter)
            min_count = count_constraint.get('min', 0)
            max_count = count_constraint.get('max', float('inf'))
            if actual_count < min_count or actual_count > max_count:
                return False
        
        return True
    
    def _advanced_pattern_check(self, word):
        """Advanced pattern check"""
        # Here can add more complex pattern matching logic
        # For example: check reasonableness of letter combinations, linguistic rules, etc.
        return True
    
    def _get_detailed_pattern(self, guess, target):
        """Get detailed matching pattern"""
        pattern = []
        target_chars = list(target)
        
        # First pass: mark exact matches
        for i in range(len(guess)):
            if guess[i] == target[i]:
                pattern.append(('G', i, guess[i]))  # Green, position, letter
                target_chars[i] = None
            else:
                pattern.append(('?', i, guess[i]))
        
        # Second pass: mark partial matches
        for i in range(len(guess)):
            if pattern[i][0] == '?':
                if guess[i] in target_chars:
                    pattern[i] = ('Y', i, guess[i])  # Yellow
                    target_chars[target_chars.index(guess[i])] = None
                else:
                    pattern[i] = ('R', i, guess[i])  # Red
        
        return pattern
    
    def _pattern_matches(self, guess, candidate, pattern):
        """Check if candidate matches given pattern"""
        candidate_chars = list(candidate)
        
        # Check green matches
        for color, pos, letter in pattern:
            if color == 'G':
                if candidate[pos] != letter:
                    return False
                candidate_chars[pos] = None
        
        # Check yellow and red matches
        for color, pos, letter in pattern:
            if color == 'Y':
                if candidate[pos] == letter:  # Should not be at this position
                    return False
                if letter not in candidate_chars:  # But should be at other positions
                    return False
                candidate_chars[candidate_chars.index(letter)] = None
            elif color == 'R':
                if letter in candidate_chars:  # Should not exist
                    return False
        
        return True
    
    def _get_best_candidate_with_game_theory(self, candidates):
        """Use game theory to select best candidate"""
        if len(candidates) == 1:
            return candidates[0]
        
        # Calculate game theory value for each candidate
        scored_candidates = []
        for candidate in candidates:
            game_score = self._calculate_game_theory_score(candidate, candidates)
            scored_candidates.append((candidate, game_score))
        
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        # Randomly select among top candidates to increase unpredictability
        top_count = min(3, len(scored_candidates))
        return random.choice([word for word, _ in scored_candidates[:top_count]])
    
    def _calculate_game_theory_score(self, candidate, all_candidates):
        """Calculate game theory score"""
        score = 0
        
        # Basic frequency score
        for letter in candidate:
            score += self.letter_frequency.get(letter, 0)
        
        # Position advantage score
        for i, letter in enumerate(candidate):
            if i in self.position_frequency:
                score += self.position_frequency[i].get(letter, 0)
        
        # Differentiation score (degree of difference from other candidates)
        for other in all_candidates:
            if other != candidate:
                diff = sum(1 for i in range(len(candidate)) if candidate[i] != other[i])
                score += diff * 2
        
        # Stealth score (not easily guessed by opponent)
        common_words = ['ABOUT', 'HOUSE', 'WORLD', 'PLACE', 'THINK']
        if candidate in common_words:
            score -= 50
        
        return score
    
    def _get_aggressive_guess(self, candidates, word_length):
        """Aggressive guess strategy"""
        if len(candidates) <= 2:
            return random.choice(candidates)
        
        # Select guess that maximizes information acquisition
        best_guess = None
        best_info_gain = -1
        
        test_words = candidates + [w for w in self.word_list[word_length][:20] if w not in self.guess_history]
        
        for guess in test_words:
            info_gain = self._calculate_expected_info_gain(guess, candidates)
            if info_gain > best_info_gain:
                best_info_gain = info_gain
                best_guess = guess
        
        return best_guess if best_guess else random.choice(candidates)
    
    def _calculate_expected_info_gain(self, guess, candidates):
        """Calculate expected information gain"""
        pattern_counts = {}
        
        for candidate in candidates:
            pattern = str(self._get_detailed_pattern(guess, candidate))
            pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Calculate expected information gain
        total = len(candidates)
        expected_gain = 0
        
        for count in pattern_counts.values():
            if count > 0:
                p = count / total
                expected_gain += p * math.log2(total / count)
        
        return expected_gain
    
    def _get_best_final_guess(self, candidates):
        """Final guess: must select answer"""
        if not candidates:
            return None
        
        # Select most likely answer
        scored_candidates = []
        for candidate in candidates:
            score = self._calculate_final_answer_score(candidate)
            scored_candidates.append((candidate, score))
        
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[0][0]
    
    def _calculate_final_answer_score(self, word):
        """Calculate final answer score"""
        score = 0
        
        # Letter frequency
        for letter in word:
            score += self.letter_frequency.get(letter, 0)
        
        # Position frequency
        for i, letter in enumerate(word):
            if i in self.position_frequency:
                score += self.position_frequency[i].get(letter, 0)
        
        # Weight of confirmed information
        for pos, letter in self.constraints['confirmed_positions'].items():
            if pos < len(word) and word[pos] == letter:
                score += 1000
        
        # Weight of required letters
        for letter in self.constraints['required_letters']:
            if letter in word:
                score += 500
        
        return score


class AIBattle:
    """Main AI battle game class"""
    
    def __init__(self, word_list_file):
        self.wordle = Wordle(word_list_file)
        self.ui = UI()
        self.ui.enable_ai_battle_mode()  # Enable AI Battle mode
        self.ai_players = {
            'beginner': BeginnerAI(self.wordle.word_list),
            'intermediate': IntermediateAI(self.wordle.word_list),
            'advanced': AdvancedAI(self.wordle.word_list)
        }
    
    def start_battle(self, difficulty, word_length):
        """Start human vs AI battle"""
        if difficulty not in self.ai_players:
            print(f"{Fore.RED}Error: Invalid difficulty level{Fore.RESET}")
            return
        
        ai_player = self.ai_players[difficulty]
        ai_player.reset()
        
        # Clear board, start new game
        self.ui.clear()
        
        # Start game
        current_word = self.wordle.start(word_length)
        if current_word is None:
            return
        
        # Setup UI
        self.ui.set_word_length(word_length)
        
        # Randomly decide who goes first
        player_turn = random.choice([True, False])
        
        # Set initial information
        self.ui.set_information("AI Battle started!")
        
        # Determine first player color
        first_player_color = self.ui.ORANGE_COLOR if player_turn else self.ui.LIGHT_BLUE_COLOR
        first_player_text = 'Orange (You)' if player_turn else f'Blue ({ai_player.name})'
        
        self.ui.set_other_msg(f"{Fore.CYAN}[Game Info]{Fore.RESET} "
                             f"{self.ui.ORANGE_COLOR}Orange{Fore.RESET}: You | "
                             f"{self.ui.LIGHT_BLUE_COLOR}Blue{Fore.RESET}: {ai_player.name} | "
                             f"First: {first_player_color}{first_player_text}{Fore.RESET}\n"
                             f"{Fore.CYAN}[Help]{Fore.RESET} {Fore.RED}/exit{Fore.RESET} - Quit game")
        self.ui.set_debug(f"Target word is {Fore.GREEN + current_word + Fore.RESET}")
        
        max_attempts = word_length + 1
        player_attempts = max_attempts
        ai_attempts = max_attempts
        
        # Initialize invalid input counter for player
        player_invalid_count = 0
        max_invalid_attempts = 3
        
        while player_attempts > 0 and ai_attempts > 0:
            if player_turn:
                # Player turn
                remaining_invalid_attempts = max_invalid_attempts - player_invalid_count
                
                # Update other message with invalid input warning if needed
                if player_invalid_count > 0:
                    self.ui.set_other_msg(f"{Fore.CYAN}[Game Info]{Fore.RESET} "
                                         f"{self.ui.ORANGE_COLOR}Orange{Fore.RESET}: You | "
                                         f"{self.ui.LIGHT_BLUE_COLOR}Blue{Fore.RESET}: {ai_player.name} | "
                                         f"First: {first_player_color}{first_player_text}{Fore.RESET}\n"
                                         f"{Fore.CYAN}[Help]{Fore.RESET} {Fore.RED}/exit{Fore.RESET} - Quit game\n"
                                         f"{Fore.RED}Invalid attempts [{player_invalid_count}/{max_invalid_attempts}]{Fore.RESET}")
                
                self.ui.set_information(f"{self.ui.ORANGE_COLOR}Orange{Fore.RESET} (You) turn - Tries left: {player_attempts}")
                self.ui.render()
                
                while True:
                    word = self.ui.input("Your guess > ")
                    
                    if word == "/exit":
                        return
                    
                    # Check for duplicate input first
                    if word.upper() in self.wordle.guess_history:
                        self.ui.set_information(f"{Fore.YELLOW}'{word}'{Fore.RESET} already guessed. Please try a different word.")
                        self.ui.render()
                        continue
                    
                    result = self.wordle.check(word)
                    
                    if result == 404:
                        player_invalid_count += 1
                        remaining_invalid_attempts = max_invalid_attempts - player_invalid_count
                        
                        if player_invalid_count >= max_invalid_attempts:
                            self.ui.set_information(f"{Fore.RED}💻 {self.ui.LIGHT_BLUE_COLOR}Blue{Fore.RESET} ({ai_player.name}) wins! "
                                                   f"Player lost [{max_invalid_attempts}/{max_invalid_attempts}] invalid words.{Fore.RESET}")
                            self.ui.set_other_msg("")  # Clear other messages when game ends
                            self.ui.render()
                            print(f"\n{Fore.RED}💻 {ai_player.name} won!{Fore.RESET} You lost due to too many invalid inputs! The word was '{current_word}'.\n")
                            input("Press Enter to continue...")
                            return
                        else:
                            self.ui.set_information(f"{Fore.RED}'{word}'{Fore.RESET} not in word list. Invalid attempts [{player_invalid_count}/{max_invalid_attempts}]")
                        self.ui.render()
                        continue
                    elif result == 416:
                        player_invalid_count += 1
                        remaining_invalid_attempts = max_invalid_attempts - player_invalid_count
                        
                        if player_invalid_count >= max_invalid_attempts:
                            self.ui.set_information(f"{Fore.RED}💻 {self.ui.LIGHT_BLUE_COLOR}Blue{Fore.RESET} ({ai_player.name}) wins! "
                                                   f"Player lost [{max_invalid_attempts}/{max_invalid_attempts}] invalid words.{Fore.RESET}")
                            self.ui.set_other_msg("")  # Clear other messages when game ends
                            self.ui.render()
                            print(f"\n{Fore.RED}💻 {ai_player.name} won!{Fore.RESET} You lost due to too many invalid inputs! The word was '{current_word}'.\n")
                            input("Press Enter to continue...")
                            return
                        else:
                            self.ui.set_information(f"Wrong length '{Fore.RED}{word}{Fore.RESET}'. Invalid attempts [{player_invalid_count}/{max_invalid_attempts}]")
                        self.ui.render()
                        continue
                    
                    # Reset invalid input counter on valid input
                    player_invalid_count = 0
                    
                    # Clear previous error messages when valid input is entered
                    self.ui.set_information(f"{self.ui.ORANGE_COLOR}Orange{Fore.RESET} (You) turn - Tries left: {player_attempts}")
                    
                    # Reset other message to original state when valid input is entered
                    self.ui.set_other_msg(f"{Fore.CYAN}[Game Info]{Fore.RESET} "
                                         f"{self.ui.ORANGE_COLOR}Orange{Fore.RESET}: You | "
                                         f"{self.ui.LIGHT_BLUE_COLOR}Blue{Fore.RESET}: {ai_player.name} | "
                                         f"First: {first_player_color}{first_player_text}{Fore.RESET}\n"
                                         f"{Fore.CYAN}[Help]{Fore.RESET} {Fore.RED}/exit{Fore.RESET} - Quit game")
                    
                    break
                
                # Add player guess to UI (orange box)
                if result is not None:
                    self.wordle.deduction_opportunity(1)
                    self.ui.insert(result, 'player')  # Specify as player
                    player_attempts -= 1
                
                # Check if player wins
                if self.wordle.get_is_win():
                    self.ui.set_information(f"{Fore.GREEN}🎉 {self.ui.ORANGE_COLOR}Orange{Fore.RESET} (You) wins!{Fore.RESET}")
                    self.ui.set_other_msg("")  # Clear other messages when game ends
                    self.ui.render()
                    print(f"\n{Fore.GREEN}You won!{Fore.RESET} The word was '{current_word}'.\n")
                    input("Press Enter to continue...")
                    return
                
                # Update AI constraints (AI can see player's guess results)
                ai_player.update_constraints(word.upper(), result)
                
            else:
                # AI turn
                self.ui.set_information(f"{self.ui.LIGHT_BLUE_COLOR}Blue{Fore.RESET} ({ai_player.name}) turn - Tries left: {ai_attempts}")
                self.ui.render()
                
                print(f"{ai_player.name} is thinking...")
                time.sleep(1.5)  # Simulate thinking time
                
                ai_guess = ai_player.make_guess(word_length, ai_attempts)
                print(f"{ai_player.name} guessed: {Fore.CYAN}{ai_guess}{Fore.RESET}")
                time.sleep(1)  # Let player see AI's guess
                
                # Reset wordle state to check AI's guess
                original_win_state = self.wordle.is_win
                original_opportunity = self.wordle.opportunity
                self.wordle.is_win = False
                
                result = self.wordle.check(ai_guess)
                
                # Add AI guess to UI (blue box)
                if result is not None:
                    self.ui.insert(result, 'ai')  # Specify as AI
                    ai_attempts -= 1
                
                # Check if AI wins
                if self.wordle.get_is_win():
                    self.ui.set_information(f"{self.ui.LIGHT_BLUE_COLOR}Blue{Fore.RESET} ({ai_player.name}) wins!")
                    self.ui.set_other_msg("")  # Clear other messages when game ends
                    self.ui.render()
                    print(f"\n{Fore.RED}💻 {ai_player.name} won!{Fore.RESET} The word was '{current_word}'.\n")
                    input("Press Enter to continue...")
                    return
                
                # Restore wordle state
                self.wordle.is_win = original_win_state
                self.wordle.opportunity = original_opportunity - 1
                
                # Update AI's own constraints
                ai_player.update_constraints(ai_guess, result)
            
            player_turn = not player_turn
        
        # Game over, draw
        self.ui.set_information(f"{Fore.YELLOW}⚖️ Tie! No one got it right{Fore.RESET}")
        self.ui.set_other_msg("")  # Clear other messages when game ends
        self.ui.render()
        print(f"\n{Fore.YELLOW}Tie!{Fore.RESET} The word was '{current_word}'.\n")
        input("Press Enter to continue...")
    


def parse_args():
    parser = argparse.ArgumentParser(description="Wordle AI Battle Mode")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    return parser.parse_args()


def main():
    args = parse_args()
    config.DEBUG = args.debug
    
    battle = AIBattle("word_list.txt")
    
    print(f"{Fore.GREEN}Welcome to Wordle AI Battle!{Fore.RESET}")
    
    while True:
        print(f"\n{Fore.CYAN}=== Main Menu ==={Fore.RESET}")
        print(f"1. {Fore.GREEN}Start Game{Fore.RESET}")
        print(f"2. {Fore.YELLOW}View AI Info{Fore.RESET}")
        print(f"3. {Fore.RED}Exit{Fore.RESET}")
        
        choice = input("\nPick > ").strip()
        
        if choice == "1":
            # Select difficulty
            print(f"\n{Fore.CYAN}Pick AI Level:{Fore.RESET}")
            print(f"1. {Fore.GREEN}Easy{Fore.RESET} - Basic reasoning with hint algorithm")
            print(f"2. {Fore.YELLOW}Medium{Fore.RESET} - Information theory optimization")
            print(f"3. {Fore.RED}Hard{Fore.RESET} - Game theory with future calculation")
            
            difficulty_choice = input("Pick level (1-3) > ").strip()
            difficulty_map = {"1": "beginner", "2": "intermediate", "3": "advanced"}
            
            if difficulty_choice not in difficulty_map:
                print(f"{Fore.RED}Wrong choice{Fore.RESET}")
                continue
            
            difficulty = difficulty_map[difficulty_choice]
            
            # Select word length
            try:
                word_length = int(input("Word length (3-10) > ").strip())
                if word_length < 3 or word_length > 10:
                    print(f"{Fore.RED}Must be 3-10 letters{Fore.RESET}")
                    continue
            except ValueError:
                print(f"{Fore.RED}Enter a number{Fore.RESET}")
                continue
            
            # Start battle
            battle.start_battle(difficulty, word_length)
            
        elif choice == "2":
            # AI Info
            print(f"\n{Fore.CYAN}=== AI Players Info ==={Fore.RESET}")
            print(f"\n{Fore.GREEN}Easy AI{Fore.RESET}:")
            print("- Pure reasoning strategy")
            print("- Basic hint algorithm")
            print("- Filter candidates by known info")
            print("- Prefer common letters")
            
            print(f"\n{Fore.YELLOW}Medium AI{Fore.RESET}:")
            print("- Enhanced with optimization techniques")
            print("- Information theory & letter frequency")
            print("- Calculate information gain")
            print("- Adjust strategy by remaining attempts")
            
            print(f"\n{Fore.RED}Hard AI{Fore.RESET}:")
            print("- Game theory considering opponent")
            print("- Monte Carlo tree search")
            print("- Balance info gain & concealment")
            print("- Adapt to opponent patterns")
            print("- Minimize strategy exposure")
            
        elif choice == "3":
            print(f"{Fore.GREEN}Thanks for playing!{Fore.RESET}")
            break
        else:
            print(f"{Fore.RED}Wrong choice{Fore.RESET}")


if __name__ == "__main__":
    main()