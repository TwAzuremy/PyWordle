from colorama import *
from collections import Counter
import random
import math


class Wordle:
    MIN_WORD_LENGTH = 3

    word_list = {}

    is_win = False
    current_word = ""
    opportunity = 0
    guess_history = []  # Store guess history

    def __init__(self, file_path: str):
        self.__process_file(file_path)

        self.min_length = min(self.word_list.keys())
        self.max_length = max(self.word_list.keys())

    def __process_file(self, file_path: str):
        """
        Loads words from a specified file and organizes them by length.

        This function reads a file line by line, processes each word, and stores
        them in a dictionary where the key is the word length and the value is a list
        of words of that length. Words that are shorter than the minimum word length
        or contain non-alphabetical characters are ignored. The words are stored in
        uppercase. After loading, it prints the total number of words loaded.

        Args:
            file_path (str): The path to the file containing the list of words.
        """
        count = 0

        with open(file_path, "r") as file:
            for line in file:
                word = line.strip()

                if len(word) < self.MIN_WORD_LENGTH:
                    continue

                if word.isalpha():
                    length = len(word)

                    if length not in self.word_list:
                        self.word_list[length] = []

                    self.word_list[length].append(word.upper())
                    count += 1

        print(f"{Fore.CYAN}[INFO]{Fore.RESET} Loaded {count} words from \"{file_path}\"")

    def start(self, length: int):
        self.is_win = False
        self.guess_history = []  # Reset guess history.

        if not self.__game_init(length):
            return None

        self.current_word = self.__get_random_word(length)

        return self.current_word

    def check(self, word: str):
        if len(word) != len(self.current_word):
            return 416

        if word.upper() not in self.word_list[len(self.current_word)]:
            return 404

        # Add guess history
        self.guess_history.append(word.upper())

        result = []
        # Mark which positions in the target string have been matched
        matched = [False] * len(word)

        # Find the exact match location (green)
        # Assume that all characters are correct
        all_correct = True
        for i in range(len(word)):
            if word[i].upper() == self.current_word[i]:
                result.append({word[i].upper(): Fore.GREEN})
                # Mark that the location is matched
                matched[i] = True
            else:
                # placeholders, to deal with later
                result.append(None)
                all_correct = False

        if all_correct:
            self.is_win = True
            return result

        # Count the unmatched letters in the target string (for yellow markers)
        available_letters = {}
        for i in range(len(self.current_word)):
            if not matched[i]:
                letter = self.current_word[i]
                available_letters[letter] = available_letters.get(letter, 0) + 1

        # Handle non-green locations
        for i in range(len(word)):
            if result[i] is not None:
                continue

            letter = word[i].upper()
            # Check if the letter is present and available
            if letter in available_letters and available_letters[letter] > 0:
                result[i] = {word[i].upper(): Fore.YELLOW}
                # Reduce the number of times you can use it
                available_letters[letter] -= 1
            else:
                result[i] = {word[i].upper(): Fore.RED}

        return result

    def __game_init(self, length: int):
        if length < self.min_length or length > self.max_length:
            print(
                f"{Fore.RED}[ERROR]{Fore.RESET} The length can only be taken from {self.min_length} - {self.max_length}.")
            return False

        if length not in self.word_list:
            print(f"{Fore.RED}[ERROR]{Fore.RESET} There are no words with a length of {length}.")
            return False

        self.opportunity = length + 1
        return True

    def __get_random_word(self, length: int):
        return random.choice(self.word_list[length])

    def get_opportunity(self):
        return self.opportunity

    def deduction_opportunity(self, number: int):
        self.opportunity -= number

    def get_is_win(self):
        return self.is_win

    def get_current_word(self):
        return self.current_word

    def get_tip(self):
        """Get intelligent hint using adaptive strategy based on game state"""
        word_length = len(self.current_word)

        # If no guess history, use intermediate AI's max info word strategy
        if not self.guess_history:
            return self._get_max_info_word_hint(word_length)

        # Use intermediate AI's reasoning approach
        constraints = self._build_constraints()
        candidates = self._get_valid_candidates_hint(word_length, constraints)
        
        if not candidates:
            # Fallback: return any unguessed word
            remaining_words = [w for w in self.word_list[word_length] if w not in self.guess_history]
            return random.choice(remaining_words) if remaining_words else random.choice(self.word_list[word_length])

        # Adaptive strategy based on game state
        remaining_attempts = max(1, (word_length + 1) - len(self.guess_history))
        candidate_count = len(candidates)
        
        # 改进的策略决策逻辑
        if candidate_count <= 2:
            # 只有1-2个候选词时，直接选择最可能的答案
            return self._get_best_answer_candidate_hint(candidates)
        elif remaining_attempts <= 1:
            # 最后一次机会，选择最可能的答案
            return self._get_best_answer_candidate_hint(candidates)
        elif candidate_count <= 6 and remaining_attempts <= 2:
            # 候选词较少且尝试次数不多时，优先选择答案候选词
            return self._get_best_answer_candidate_hint(candidates)
        else:
            # 其他情况优先考虑信息增益，以获得最大信息量
            info_gain_word = self._get_max_info_gain_word_hint(candidates, word_length)
            
            # 如果信息增益推荐的词就是候选词之一，直接返回
            if info_gain_word in candidates:
                return info_gain_word
            
            # 否则在信息增益和答案候选词之间做权衡
            if candidate_count <= 10 and remaining_attempts >= 3:
                # 候选词不多且还有足够尝试次数时，70%选择信息增益，30%选择答案候选词
                if random.random() < 0.7:
                    return info_gain_word
                else:
                    return self._get_best_answer_candidate_hint(candidates)
            else:
                # 默认选择信息增益最大的词
                return info_gain_word

    def _get_max_info_word_hint(self, word_length):
        """Get word with maximum information value (from Intermediate AI)"""
        # Calculate letter frequency for this word length
        letter_frequency = Counter()
        for word in self.word_list[word_length]:
            letter_frequency.update(word)
        
        # Select words with most common and non-repeating letters
        best_word = None
        best_score = -1
        
        for word in self.word_list[word_length]:
            if len(set(word)) == len(word):  # No repeat letters
                score = sum(letter_frequency[letter] for letter in word)
                if score > best_score:
                    best_score = score
                    best_word = word
        
        return best_word if best_word else random.choice(self.word_list[word_length])

    def _get_valid_candidates_hint(self, word_length, constraints):
        """Get all valid candidate words using intermediate AI logic"""
        candidates = []
        for word in self.word_list[word_length]:
            if word in self.guess_history:
                continue
            if self._is_valid_candidate_hint(word, constraints):
                candidates.append(word)
        return candidates

    def _is_valid_candidate_hint(self, word, constraints):
        """Advanced candidate validation (from Intermediate AI)"""
        # Check confirmed positions
        for pos, letter in constraints['confirmed_positions'].items():
            if word[pos] != letter:
                return False
        
        # Check required letters
        word_letters = set(word)
        if not constraints['required_letters'].issubset(word_letters):
            return False
        
        # Check forbidden letters
        if word_letters.intersection(constraints['forbidden_letters']):
            return False
        
        # Check wrong positions
        for letter, forbidden_positions in constraints['wrong_positions'].items():
            for pos in forbidden_positions:
                if pos < len(word) and word[pos] == letter:
                    return False
        
        # Letter count validations
        for letter, count_constraint in constraints['letter_counts'].items():
            actual_count = word.count(letter)
            min_count = count_constraint.get('min', 0)
            max_count = count_constraint.get('max', float('inf'))
            if actual_count < min_count or actual_count > max_count:
                return False
        
        return True

    def _get_max_info_gain_word_hint(self, candidates, word_length):
        """Select word with maximum information gain (from Intermediate AI)"""
        # 移除候选词数量限制，即使候选词很少也要计算信息增益
        
        # Calculate letter frequency for scoring
        letter_frequency = Counter()
        for word in self.word_list[word_length]:
            letter_frequency.update(word)
        
        # Improved information gain calculation
        best_word = None
        best_score = -1
        
        # 扩大测试范围，提高推荐质量
        test_words = self.word_list[word_length]
        test_limit = min(200, len(test_words))  # 增加到200个单词
        
        for test_word in test_words[:test_limit]:
            if test_word in self.guess_history:
                continue
            
            score = self._calculate_info_gain_hint(test_word, candidates)
            
            # 给候选词额外加分，但不完全偏向候选词
            if test_word in candidates:
                score += 0.1  # 小幅加分
            
            if score > best_score:
                best_score = score
                best_word = test_word
        
        return best_word if best_word else random.choice(candidates)

    def _calculate_info_gain_hint(self, test_word, candidates):
        """Calculate information gain (improved version)"""
        # Simulate this word's partition of the candidate set
        pattern_groups = {}
        
        # 使用所有候选词进行计算，不再限制数量
        for candidate in candidates:
            pattern = self._get_pattern_hint(test_word, candidate)
            pattern_key = str(pattern)
            if pattern_key not in pattern_groups:
                pattern_groups[pattern_key] = 0
            pattern_groups[pattern_key] += 1
        
        # Calculate entropy (information gain)
        total = sum(pattern_groups.values())
        if total == 0:
            return 0
            
        entropy = 0
        for count in pattern_groups.values():
            if count > 0:
                p = count / total
                entropy -= p * math.log2(p)
        
        # 额外考虑分组的均匀性 - 更均匀的分组意味着更好的信息增益
        group_count = len(pattern_groups)
        if group_count > 1:
            # 奖励能产生更多不同模式的单词
            entropy += math.log2(group_count) * 0.1
        
        return entropy

    def _get_pattern_hint(self, guess, target):
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

    def _get_best_answer_candidate_hint(self, candidates):
        """Select most likely answer candidate (from Intermediate AI)"""
        # Calculate letter frequency for scoring
        letter_frequency = Counter()
        for length_words in self.word_list.values():
            for word in length_words:
                letter_frequency.update(word)
        
        # Based on letter frequency and position probability
        scored_candidates = []
        for word in candidates:
            score = self._calculate_answer_score_hint(word, letter_frequency)
            scored_candidates.append((word, score))
        
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        return scored_candidates[0][0]

    def _calculate_answer_score_hint(self, word, letter_frequency):
        """Calculate answer score"""
        score = 0
        
        # Letter frequency score
        for letter in word:
            score += letter_frequency.get(letter, 0)
        
        # Build constraints for scoring
        constraints = self._build_constraints()
        
        # Position score (confirmed position letters get high score)
        for pos, letter in constraints['confirmed_positions'].items():
            if pos < len(word) and word[pos] == letter:
                score += 100
        
        # Score for containing required letters
        for letter in constraints['required_letters']:
            if letter in word:
                score += 50
        
        return score

    def _build_constraints(self):
        """Build comprehensive constraints from all guess history"""
        constraints = {
            'confirmed_positions': {},  # {position: letter}
            'required_letters': set(),  # Letters that must be in the word
            'forbidden_letters': set(),  # Letters that cannot be in the word
            'wrong_positions': {},  # {letter: set of forbidden positions}
            'letter_counts': {},  # {letter: {'min': int, 'max': int}}
        }

        for guess in self.guess_history:
            result = self._analyze_guess(guess)
            self._update_constraints_from_guess(constraints, guess, result)

        return constraints

    def _update_constraints_from_guess(self, constraints, guess, result):
        """Update constraints based on a single guess result"""
        letter_feedback = {}  # Track feedback for each letter in this guess
        
        # First pass: collect all feedback for each letter
        for i, (letter, color) in enumerate(result):
            if letter not in letter_feedback:
                letter_feedback[letter] = {'positions': [], 'colors': []}
            letter_feedback[letter]['positions'].append(i)
            letter_feedback[letter]['colors'].append(color)

        # Second pass: update constraints based on complete letter feedback
        for letter, feedback in letter_feedback.items():
            green_positions = [pos for pos, color in zip(feedback['positions'], feedback['colors']) if color == Fore.GREEN]
            yellow_positions = [pos for pos, color in zip(feedback['positions'], feedback['colors']) if color == Fore.YELLOW]
            red_positions = [pos for pos, color in zip(feedback['positions'], feedback['colors']) if color == Fore.RED]

            # Handle green letters (confirmed positions)
            for pos in green_positions:
                constraints['confirmed_positions'][pos] = letter
                constraints['required_letters'].add(letter)

            # Handle yellow letters (wrong positions but letter exists)
            if yellow_positions:
                constraints['required_letters'].add(letter)
                if letter not in constraints['wrong_positions']:
                    constraints['wrong_positions'][letter] = set()
                constraints['wrong_positions'][letter].update(yellow_positions)

            # Handle red letters (more complex logic)
            if red_positions and not green_positions and not yellow_positions:
                # Letter is completely absent
                constraints['forbidden_letters'].add(letter)
            elif red_positions:
                # Letter exists but not in these red positions
                if letter not in constraints['wrong_positions']:
                    constraints['wrong_positions'][letter] = set()
                constraints['wrong_positions'][letter].update(red_positions)

            # Update letter count constraints
            total_occurrences = len([pos for pos, color in zip(feedback['positions'], feedback['colors']) 
                                   if color in [Fore.GREEN, Fore.YELLOW]])
            
            if total_occurrences > 0:
                if letter not in constraints['letter_counts']:
                    constraints['letter_counts'][letter] = {'min': 0, 'max': float('inf')}
                constraints['letter_counts'][letter]['min'] = max(
                    constraints['letter_counts'][letter]['min'], total_occurrences
                )
            
            # If we see red positions for a letter that also has green/yellow, 
            # it means the letter appears exactly as many times as green+yellow
            if red_positions and (green_positions or yellow_positions):
                if letter not in constraints['letter_counts']:
                    constraints['letter_counts'][letter] = {'min': 0, 'max': float('inf')}
                constraints['letter_counts'][letter]['max'] = total_occurrences

    def _is_valid_candidate(self, word, constraints):
        """Check if a word satisfies all constraints"""
        # Check confirmed positions
        for pos, letter in constraints['confirmed_positions'].items():
            if word[pos] != letter:
                return False

        # Check required letters
        word_letters = set(word)
        if not constraints['required_letters'].issubset(word_letters):
            return False

        # Check forbidden letters
        if word_letters.intersection(constraints['forbidden_letters']):
            return False

        # Check wrong positions
        for letter, forbidden_positions in constraints['wrong_positions'].items():
            for pos in forbidden_positions:
                if pos < len(word) and word[pos] == letter:
                    return False

        # Check letter count constraints
        for letter, count_constraint in constraints['letter_counts'].items():
            actual_count = word.count(letter)
            if actual_count < count_constraint['min'] or actual_count > count_constraint['max']:
                return False

        return True

    def _calculate_word_score(self, word, constraints):
        """Calculate a score for how good a candidate word is"""
        score = 0
        
        # Prefer words with common letters in remaining positions
        common_letters = 'ETAOINSHRDLCUMWFGYPBVKJXQZ'
        for i, letter in enumerate(word):
            if i not in constraints['confirmed_positions']:
                # Score based on letter frequency (higher for more common letters)
                letter_score = (26 - common_letters.index(letter)) if letter in common_letters else 1
                score += letter_score

        # Bonus for words that use more different letters (better information gain)
        unique_letters = len(set(word))
        score += unique_letters * 10

        # Penalty for letters we already know are wrong in other positions
        for letter, wrong_positions in constraints['wrong_positions'].items():
            if letter in word:
                # Small penalty for using letters we know have position constraints
                score -= len(wrong_positions) * 2

        return score

    def _analyze_guess(self, guess):
        """
        Analyze the guess result and return color information for each letter

        Args:
            guess (str): The guessed word

        Returns:
            list: [(letter, color), ...]
        """
        result = []
        matched = [False] * len(guess)

        # Find exact match positions (green)
        for i in range(len(guess)):
            if guess[i] == self.current_word[i]:
                result.append((guess[i], Fore.GREEN))
                matched[i] = True
            else:
                result.append((guess[i], None))

        # Count unmatched letters in the target word
        available_letters = {}
        for i in range(len(self.current_word)):
            if not matched[i]:
                letter = self.current_word[i]
                available_letters[letter] = available_letters.get(letter, 0) + 1

        # Handle non-green positions
        for i in range(len(guess)):
            if result[i][1] is not None:
                continue

            letter = guess[i]
            if letter in available_letters and available_letters[letter] > 0:
                result[i] = (letter, Fore.YELLOW)
                available_letters[letter] -= 1
            else:
                result[i] = (letter, Fore.RED)

        return result
