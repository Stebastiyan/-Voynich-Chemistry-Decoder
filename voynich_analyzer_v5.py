#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ВОЙНИЧ = ФАРМО-ЯДО-ПАРФЮМНОЕ ПРОИЗВОДСТВО (XV век)
Научный анализатор с TF-IDF, N-граммами и статистической проверкой гипотезы

Авторы: Стебястьян — Василий Тёркин 🎖️ & Qwen AI
Дата: Июнь 2026
Версия: 5.0 (Научная)

МАТЕМАТИЧЕСКИЙ КРИТЕРИЙ УСПЕХА:
Если теория верна, то слова с химическими корнями (ol, sol, k) должны иметь 
статистически аномально высокую плотность (TF-IDF) именно в «Биологическом» 
(банном) разделе и резко падать в Астрономическом.
"""

import os
import re
import math
from collections import Counter, defaultdict
from typing import Dict, List, Tuple, Set
import statistics

# ============================================================
# 1. ПАРСЕР ФАЙЛА С ОПРЕДЕЛЕНИЕМ РАЗДЕЛОВ
# ============================================================

class VoynichFileParser:
    """Парсер файла транскрипции с определением разделов по фолио"""
    
    # Границы разделов рукописи
    SECTIONS = {
        'botanical': (1, 66, 'Ботанический'),
        'astronomical': (67, 73, 'Астрономический'),
        'biological': (75, 84, 'Биологический (Бани)'),
        'pharmaceutical': (85, 116, 'Фармацевтический'),
        'cosmological': (65, 73, 'Космологический'),
        'recipes': (103, 116, 'Рецепты')
    }
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.sections_data = defaultdict(lambda: {'words': [], 'lines': []})
        self.all_words = []
        
    def parse(self):
        """Чтение файла и разбивка на разделы"""
        print(f"📖 Загрузка файла: {self.file_path}...")
        
        if not os.path.exists(self.file_path):
            raise FileNotFoundError(f"Файл {self.file_path} не найден")
        
        with open(self.file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        current_section = None
        
        for line in content.splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            
            # Извлечение номера страницы из формата <fXXr.Y...>
            folio_match = re.search(r'<f(\d+)', line)
            if folio_match:
                folio_num = int(folio_match.group(1))
                current_section = self._get_section(folio_num)
            
            # Извлечение текста
            text_match = re.search(r'<%>(.+?)(?:<|$)', line)
            if text_match:
                text = text_match.group(1).strip()
                words = self._extract_words(text)
                
                if current_section:
                    self.sections_data[current_section]['words'].extend(words)
                    self.sections_data[current_section]['lines'].append(text)
                
                self.all_words.extend(words)
        
        print(f"✅ Загружено {len(self.all_words)} слов")
        for section, data in self.sections_data.items():
            print(f"   📚 {section}: {len(data['words'])} слов")
    
    def _get_section(self, folio_num: int) -> str:
        """Определение раздела по номеру страницы"""
        for section, (start, end, name) in self.SECTIONS.items():
            if start <= folio_num <= end:
                return section
        return 'other'
    
    def _extract_words(self, text: str) -> List[str]:
        """Извлечение слов из строки"""
        # Разбиваем по пробелам и точкам
        words = re.split(r'[\s.]+', text)
        # Очистка от служебных символов
        cleaned = []
        for word in words:
            word = word.strip(".,;:?!*-[]{}()<>@")
            if word and len(word) >= 2:
                cleaned.append(word)
        return cleaned


# ============================================================
# 2. МОРФОЛОГИЧЕСКИЙ АНАЛИЗАТОР С ВЕРОЯТНОСТНЫМИ ОЦЕНКАМИ
# ============================================================

class ProbabilisticMorphologyAnalyzer:
    """Морфологический анализ с вероятностными оценками"""
    
    def __init__(self):
        # Морфологическая матрица v4.0
        self.prefixes = {
            'Ot': ('отдача тепла / преднагрев', 0.85),
            'qo': ('поток спирта / рабочее тело', 0.90),
            'op': ('орошение / абсорбция', 0.80),
            'l': ('охлаждение', 0.75),
            'p': ('подъём', 0.70)
        }
        
        self.roots = {
            'sheol': ('мыльная фаза', 0.85),
            'sheod': ('смолянистая фаза', 0.85),
            'sheo': ('мутная среда', 0.80),
            'sho': ('трение / бурление', 0.75),
            'ol': ('масляная фаза', 0.90),
            'ar': ('ароматная рециркуляция', 0.80),
            'am': ('ароматная мацерация', 0.80),
            'edy': ('состояние пара', 0.85),
            'ch': ('растительное сырьё', 0.85),
            'chy': ('замоченное сырьё', 0.80),
            'dar': ('настой', 0.85),
            'qok': ('готовый осадок', 0.90)
        }
        
        self.suffixes = {
            'k': ('кальцинирование', 0.85),
            'r': ('рециркуляция', 0.80),
            'y': ('текучесть', 0.85),
            'ain': ('осадок', 0.80),
            'al': ('основа', 0.75),
            'dy': ('процесс', 0.70)
        }
    
    def analyze_word(self, word: str) -> Dict:
        """Анализ слова с вероятностной оценкой"""
        cleaned = self._clean_word(word)
        if not cleaned:
            return None
        
        analysis = {
            'original': word,
            'cleaned': cleaned,
            'elements': [],
            'confidence': 1.0,
            'chemical_markers': []
        }
        
        remainder = cleaned
        
        # Шаг 1: Приставки
        for pref, (desc, prob) in self.prefixes.items():
            if remainder.startswith(pref):
                analysis['elements'].append(('prefix', pref, desc))
                analysis['confidence'] *= prob
                remainder = remainder[len(pref):]
                break
        
        # Шаг 2: Суффиксы (с конца)
        found_suffixes = []
        changed = True
        while changed:
            changed = False
            for suf, (desc, prob) in self.suffixes.items():
                if remainder.endswith(suf):
                    found_suffixes.insert(0, ('suffix', suf, desc, prob))
                    remainder = remainder[:-len(suf)]
                    changed = True
                    break
        
        # Шаг 3: Корни (по длине)
        sorted_roots = sorted(self.roots.items(), key=lambda x: len(x[0]), reverse=True)
        for root, (desc, prob) in sorted_roots:
            if root in remainder:
                analysis['elements'].append(('root', root, desc))
                analysis['confidence'] *= prob
                analysis['chemical_markers'].append(root)
                remainder = remainder.replace(root, '', 1)
        
        # Добавляем суффиксы
        for _, suf, desc, prob in found_suffixes:
            analysis['elements'].append(('suffix', suf, desc))
            analysis['confidence'] *= prob
        
        return analysis
    
    def _clean_word(self, word: str) -> str:
        """Очистка слова"""
        word = word.strip(".,;:?!*-[]{}()<>@")
        if word.startswith('Ot'):
            return 'Ot' + word[2:].lower()
        return word.lower()


# ============================================================
# 3. TF-IDF АНАЛИЗАТОР
# ============================================================

class TFIDFAnalyzer:
    """Расчет TF-IDF для каждого раздела"""
    
    def __init__(self, sections_data: Dict):
        self.sections_data = sections_data
        self.tfidf_scores = {}
        
    def calculate(self):
        """Расчет TF-IDF для всех слов во всех разделах"""
        print("\n📊 Расчет TF-IDF...")
        
        # Подсчет DF (Document Frequency) - в скольких разделах встречается слово
        df = Counter()
        for section, data in self.sections_data.items():
            unique_words = set(data['words'])
            for word in unique_words:
                df[word] += 1
        
        total_sections = len(self.sections_data)
        
        # Расчет TF-IDF для каждого раздела
        for section, data in self.sections_data.items():
            word_counts = Counter(data['words'])
            total_words = len(data['words'])
            
            tfidf = {}
            for word, count in word_counts.items():
                tf = count / total_words
                idf = math.log(total_sections / (1 + df[word]))
                tfidf[word] = tf * idf
            
            self.tfidf_scores[section] = tfidf
        
        print(f"✅ TF-IDF рассчитан для {len(self.tfidf_scores)} разделов")
    
    def get_top_words(self, section: str, n: int = 20) -> List[Tuple[str, float]]:
        """Получить топ-N слов по TF-IDF для раздела"""
        if section not in self.tfidf_scores:
            return []
        
        sorted_words = sorted(
            self.tfidf_scores[section].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_words[:n]
    
    def get_chemical_words(self, chemical_markers: Set[str]) -> Dict[str, Dict[str, float]]:
        """Получить TF-IDF для слов с химическими маркерами по всем разделам"""
        result = {}
        
        for section, tfidf in self.tfidf_scores.items():
            chemical_tfidf = {}
            for word, score in tfidf.items():
                # Проверяем, содержит ли слово химические маркеры
                for marker in chemical_markers:
                    if marker in word.lower():
                        chemical_tfidf[word] = score
                        break
            result[section] = chemical_tfidf
        
        return result


# ============================================================
# 4. N-GRAMM АНАЛИЗАТОР
# ============================================================

class NgramAnalyzer:
    """Анализ N-грамм для каждого раздела"""
    
    def __init__(self, sections_data: Dict):
        self.sections_data = sections_data
        self.ngrams = {}
    
    def calculate(self, n: int = 2):
        """Расчет N-грамм для каждого раздела"""
        print(f"\n🔤 Расчет {n}-грамм...")
        
        for section, data in self.sections_data.items():
            words = data['words']
            ngram_counts = Counter()
            
            for i in range(len(words) - n + 1):
                ngram = tuple(words[i:i+n])
                ngram_counts[ngram] += 1
            
            self.ngrams[section] = ngram_counts
        
        print(f"✅ N-граммы рассчитаны для {len(self.ngrams)} разделов")
    
    def get_top_ngrams(self, section: str, n: int = 2, top_n: int = 20) -> List[Tuple[tuple, int]]:
        """Получить топ-N N-грамм для раздела"""
        if section not in self.ngrams:
            return []
        
        sorted_ngrams = sorted(
            self.ngrams[section].items(),
            key=lambda x: x[1],
            reverse=True
        )
        return sorted_ngrams[:top_n]


# ============================================================
# 5. СТАТИСТИЧЕСКИЙ АНАЛИЗАТОР
# ============================================================

class StatisticalAnalyzer:
    """Статистическая проверка гипотезы"""
    
    def __init__(self, sections_data: Dict, tfidf_analyzer: TFIDFAnalyzer):
        self.sections_data = sections_data
        self.tfidf_analyzer = tfidf_analyzer
    
    def test_hypothesis(self, chemical_markers: Set[str]):
        """
        Проверка гипотезы: химические маркеры должны иметь аномально высокую
        плотность в биологическом разделе
        """
        print("\n🧪 Статистическая проверка гипотезы...")
        
        # Получаем TF-IDF для слов с химическими маркерами
        chemical_tfidf = self.tfidf_analyzer.get_chemical_words(chemical_markers)
        
        # Считаем среднее TF-IDF для химических слов в каждом разделе
        section_scores = {}
        for section, words in chemical_tfidf.items():
            if words:
                scores = list(words.values())
                section_scores[section] = {
                    'mean': statistics.mean(scores),
                    'median': statistics.median(scores),
                    'count': len(scores),
                    'sum': sum(scores)
                }
        
        # Проверка: биологический раздел должен иметь максимальное значение
        biological_score = section_scores.get('biological', {}).get('mean', 0)
        max_score = max([s.get('mean', 0) for s in section_scores.values()])
        
        hypothesis_confirmed = (biological_score == max_score) and (biological_score > 0)
        
        # Расчет отношения биологического к астрономическому
        astronomical_score = section_scores.get('astronomical', {}).get('mean', 0)
        ratio = biological_score / astronomical_score if astronomical_score > 0 else float('inf')
        
        print(f"\n📈 Результаты:")
        for section, scores in section_scores.items():
            print(f"   {section}: mean={scores['mean']:.4f}, count={scores['count']}")
        
        print(f"\n🎯 Гипотеза: {'✅ ПОДТВЕРЖДЕНА' if hypothesis_confirmed else '❌ НЕ ПОДТВЕРЖДЕНА'}")
        print(f"   Отношение biological/astronomical: {ratio:.2f}x")
        
        return {
            'confirmed': hypothesis_confirmed,
            'ratio': ratio,
            'section_scores': section_scores
        }
    
    def chi_square_test(self, chemical_markers: Set[str]):
        """Хи-квадрат тест для проверки независимости распределения"""
        print("\n📊 Хи-квадрат тест...")
        
        # Подсчет частот химических слов в каждом разделе
        observed = []
        expected = []
        
        total_chemical = 0
        section_totals = {}
        
        for section, data in self.sections_data.items():
            chemical_count = sum(1 for word in data['words'] 
                               if any(marker in word.lower() for marker in chemical_markers))
            total_count = len(data['words'])
            
            observed.append(chemical_count)
            section_totals[section] = total_count
            total_chemical += chemical_count
        
        # Ожидаемые частоты (равномерное распределение)
        total_words = sum(section_totals.values())
        for section in self.sections_data.keys():
            expected_count = (section_totals[section] / total_words) * total_chemical
            expected.append(expected_count)
        
        # Расчет хи-квадрат
        chi_square = sum((o - e) ** 2 / e for o, e in zip(observed, expected) if e > 0)
        
        print(f"   Хи-квадрат: {chi_square:.2f}")
        print(f"   Степени свободы: {len(observed) - 1}")
        
        # Критическое значение для p=0.05 и df=len(observed)-1
        # Упрощенная проверка: если chi_square > 10, то значимо
        significant = chi_square > 10
        
        print(f"   Значимость: {'✅ ЗНАЧИМО' if significant else '❌ НЕ ЗНАЧИМО'}")
        
        return {
            'chi_square': chi_square,
            'significant': significant,
            'observed': observed,
            'expected': expected
        }


# ============================================================
# 6. ГЛАВНЫЙ АНАЛИЗАТОР
# ============================================================

class VoynichThermodynamicAnalyzer:
    """Главный класс для полного анализа"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.parser = VoynichFileParser(file_path)
        self.morphology = ProbabilisticMorphologyAnalyzer()
        self.tfidf = None
        self.ngram = None
        self.statistical = None
        
        # Химические маркеры для проверки гипотезы
        self.chemical_markers = {'ol', 'k', 'sol', 'alk', 'qok', 'sheol', 'sheod', 'dar'}
    
    def run_full_analysis(self):
        """Запуск полного анализа"""
        print("="*70)
        print("🧪 VOYNICH THERMODYNAMIC ANALYZER v5.0")
        print("   Научное исследование с TF-IDF и статистической проверкой")
        print("="*70)
        
        # Шаг 1: Парсинг файла
        self.parser.parse()
        
        # Шаг 2: Расчет TF-IDF
        self.tfidf = TFIDFAnalyzer(self.parser.sections_data)
        self.tfidf.calculate()
        
        # Шаг 3: Расчет N-грамм
        self.ngram = NgramAnalyzer(self.parser.sections_data)
        self.ngram.calculate(n=2)
        
        # Шаг 4: Статистический анализ
        self.statistical = StatisticalAnalyzer(self.parser.sections_data, self.tfidf)
        
        # Шаг 5: Проверка гипотезы
        hypothesis_result = self.statistical.test_hypothesis(self.chemical_markers)
        chi_square_result = self.statistical.chi_square_test(self.chemical_markers)
        
        # Шаг 6: Вывод результатов
        self._print_results(hypothesis_result, chi_square_result)
    
    def _print_results(self, hypothesis_result: Dict, chi_square_result: Dict):
        """Вывод результатов анализа"""
        print("\n" + "="*70)
        print("📊 РЕЗУЛЬТАТЫ АНАЛИЗА")
        print("="*70)
        
        # Топ слова по TF-IDF для каждого раздела
        print("\n🔝 ТОП-10 слов по TF-IDF для каждого раздела:")
        for section in self.parser.sections_data.keys():
            print(f"\n📚 {section}:")
            top_words = self.tfidf.get_top_words(section, n=10)
            for i, (word, score) in enumerate(top_words, 1):
                print(f"   {i:2d}. {word:20s} TF-IDF: {score:.4f}")
        
        # Топ биграммы
        print("\n\n🔤 ТОП-10 биграмм для биологического раздела:")
        top_bigrams = self.ngram.get_top_ngrams('biological', n=2, top_n=10)
        for i, (bigram, count) in enumerate(top_bigrams, 1):
            print(f"   {i:2d}. {' '.join(bigram):30s} {count} раз")
        
        # Примеры морфологического разбора
        print("\n\n🧪 Примеры морфологического разбора:")
        sample_words = ['qokain', 'olkeedy', 'shedy', 'qotolfchedy', 'roly']
        for word in sample_words:
            analysis = self.morphology.analyze_word(word)
            if analysis:
                print(f"\n   Слово: {word}")
                print(f"   Элементы: {' + '.join([e[1] for e in analysis['elements']])}")
                print(f"   Смысл: {' → '.join([e[2] for e in analysis['elements']])}")
                print(f"   Уверенность: {analysis['confidence']:.2%}")
        
        # Итоговый вывод
        print("\n" + "="*70)
        print("🎯 ИТОГОВЫЙ ВЫВОД")
        print("="*70)
        
        if hypothesis_result['confirmed'] and chi_square_result['significant']:
            print("✅ ГИПОТЕЗА ПОДТВЕРЖДЕНА!")
            print(f"   Химические маркеры имеют аномально высокую плотность")
            print(f"   в биологическом разделе (отношение: {hypothesis_result['ratio']:.2f}x)")
            print(f"   Хи-квадрат тест значим (χ²={chi_square_result['chi_square']:.2f})")
        else:
            print("❌ ГИПОТЕЗА НЕ ПОДТВЕРЖДЕНА")
            print("   Необходимо пересмотреть морфологическую матрицу")


# ============================================================
# ТОЧКА ВХОДА
# ============================================================

if __name__ == "__main__":
    FILE_PATH = 'ZL3b-n.txt'
    
    analyzer = VoynichThermodynamicAnalyzer(FILE_PATH)
    analyzer.run_full_analysis()
