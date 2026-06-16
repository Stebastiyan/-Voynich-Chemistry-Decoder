#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ВОЙНИЧ = ФАРМО-ЯДО-ПАРФЮМНОЕ ПРОИЗВОДСТВО (XV век)
Научный анализатор с TF-IDF, N-граммами и статистической проверкой гипотезы

Версия: 5.1 (Исправленная)
Исправления:
  - Регистронезависимая обработка префиксов (совместимость с EVA)
  - Защита от деления на ноль в хи-квадрат тесте
  - Математический стандарт Пирсона (ожидаемая частота ≥ 5)
  - Корректный расчёт степеней свободы
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
    
    SECTIONS = {
        'botanical': (1, 66, 'Ботанический'),
        'astronomical': (67, 73, 'Астрономический'),
        'biological': (75, 84, 'Биологический (Бани)'),
        'pharmaceutical': (85, 116, 'Фармацевтический'),
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
            
            folio_match = re.search(r'<f(\d+)', line)
            if folio_match:
                folio_num = int(folio_match.group(1))
                current_section = self._get_section(folio_num)
            
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
            if data['words']:
                print(f"   📚 {section}: {len(data['words'])} слов")
            else:
                print(f"   ⚠️  {section}: ПУСТО (пропущено в анализе)")
    
    def _get_section(self, folio_num: int) -> str:
        """Определение раздела по номеру страницы"""
        for section, (start, end, name) in self.SECTIONS.items():
            if start <= folio_num <= end:
                return section
        return 'other'
    
    def _extract_words(self, text: str) -> List[str]:
        """Извлечение слов из строки"""
        words = re.split(r'[\s.]+', text)
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
    """Морфологический анализ с вероятностными оценками (регистронезависимый)"""
    
    def __init__(self):
        # Морфологическая матрица v4.0 (все в нижнем регистре для EVA)
        self.prefixes = {
            'ot': ('отдача тепла / преднагрев', 0.85),
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
        """Анализ слова с вероятностной оценкой (регистронезависимый)"""
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
        
        # ШАГ 1: Приставки (регистронезависимая проверка)
        remainder_lower = remainder.lower()
        for pref, (desc, prob) in self.prefixes.items():
            if remainder_lower.startswith(pref.lower()):
                analysis['elements'].append(('prefix', pref, desc))
                analysis['confidence'] *= prob
                remainder = remainder[len(pref):]
                remainder_lower = remainder.lower()
                break
        
        # ШАГ 2: Суффиксы (с конца, регистронезависимо)
        found_suffixes = []
        changed = True
        while changed:
            changed = False
            remainder_lower = remainder.lower()
            for suf, (desc, prob) in self.suffixes.items():
                if remainder_lower.endswith(suf.lower()):
                    found_suffixes.insert(0, ('suffix', suf, desc, prob))
                    remainder = remainder[:-len(suf)]
                    remainder_lower = remainder.lower()
                    changed = True
                    break
        
        # ШАГ 3: Корни (по длине, регистронезависимо)
        sorted_roots = sorted(self.roots.items(), key=lambda x: len(x[0]), reverse=True)
        for root, (desc, prob) in sorted_roots:
            if root.lower() in remainder_lower:
                analysis['elements'].append(('root', root, desc))
                analysis['confidence'] *= prob
                analysis['chemical_markers'].append(root)
                # Удаляем первое вхождение
                idx = remainder_lower.find(root.lower())
                remainder = remainder[:idx] + remainder[idx+len(root):]
                remainder_lower = remainder.lower()
        
        # Добавляем суффиксы
        for _, suf, desc, prob in found_suffixes:
            analysis['elements'].append(('suffix', suf, desc))
            analysis['confidence'] *= prob
        
        return analysis
    
    def _clean_word(self, word: str) -> str:
        """Очистка слова (всегда возвращает нижний регистр для совместимости с EVA)"""
        word = word.strip(".,;:?!*-[]{}()<>@")
        # ВАЖНО: всегда возвращаем нижний регистр, так как EVA-транскрипции в нижнем регистре
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
        
        # Фильтруем пустые разделы
        valid_sections = {k: v for k, v in self.sections_data.items() if v['words']}
        
        if not valid_sections:
            print("❌ Нет данных для расчета TF-IDF")
            return
        
        # Подсчет DF (Document Frequency)
        df = Counter()
        for section, data in valid_sections.items():
            unique_words = set(data['words'])
            for word in unique_words:
                df[word] += 1
        
        total_sections = len(valid_sections)
        
        # Расчет TF-IDF для каждого раздела
        for section, data in valid_sections.items():
            word_counts = Counter(data['words'])
            total_words = len(data['words'])
            
            if total_words == 0:
                continue
            
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
                word_lower = word.lower()
                for marker in chemical_markers:
                    if marker.lower() in word_lower:
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
            if len(words) < n:
                continue
            
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
# 5. СТАТИСТИЧЕСКИЙ АНАЛИЗАТОР (ИСПРАВЛЕННЫЙ)
# ============================================================

class StatisticalAnalyzer:
    """Статистическая проверка гипотезы с защитой от ошибок"""
    
    def __init__(self, sections_data: Dict, tfidf_analyzer: TFIDFAnalyzer):
        self.sections_data = sections_data
        self.tfidf_analyzer = tfidf_analyzer
    
    def test_hypothesis(self, chemical_markers: Set[str]):
        """
        Проверка гипотезы: химические маркеры должны иметь аномально высокую
        плотность в биологическом разделе
        """
        print("\n🧪 Статистическая проверка гипотезы...")
        
        chemical_tfidf = self.tfidf_analyzer.get_chemical_words(chemical_markers)
        
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
        
        if not section_scores:
            print("❌ Нет данных для проверки гипотезы")
            return {'confirmed': False, 'ratio': 0, 'section_scores': {}}
        
        # Проверка: биологический раздел должен иметь максимальное значение
        biological_score = section_scores.get('biological', {}).get('mean', 0)
        max_score = max([s.get('mean', 0) for s in section_scores.values()])
        
        hypothesis_confirmed = (biological_score == max_score) and (biological_score > 0)
        
        # Расчет отношения биологического к астрономическому
        astronomical_score = section_scores.get('astronomical', {}).get('mean', 0)
        
        # Защита от деления на ноль
        if astronomical_score > 0:
            ratio = biological_score / astronomical_score
        else:
            ratio = float('inf') if biological_score > 0 else 0
        
        print(f"\n📈 Результаты:")
        for section, scores in section_scores.items():
            print(f"   {section}: mean={scores['mean']:.4f}, count={scores['count']}")
        
        print(f"\n🎯 Гипотеза: {'✅ ПОДТВЕРЖДЕНА' if hypothesis_confirmed else '❌ НЕ ПОДТВЕРЖДЕНА'}")
        if ratio != float('inf'):
            print(f"   Отношение biological/astronomical: {ratio:.2f}x")
        else:
            print(f"   Отношение biological/astronomical: ∞ (астрономический раздел пуст)")
        
        return {
            'confirmed': hypothesis_confirmed,
            'ratio': ratio,
            'section_scores': section_scores
        }
    
    def chi_square_test(self, chemical_markers: Set[str]):
        """
        Хи-квадрат тест для проверки независимости распределения
        ИСПРАВЛЕНО: защита от деления на ноль + стандарт Пирсона (e >= 5)
        """
        print("\n📊 Хи-квадрат тест (со стандартом Пирсона)...")
        
        # Фильтруем пустые разделы
        valid_sections = {k: v for k, v in self.sections_data.items() if v['words']}
        
        if not valid_sections:
            print("❌ Нет данных для хи-квадрат теста")
            return {'chi_square': 0, 'significant': False, 'observed': [], 'expected': []}
        
        # Подсчет частот химических слов в каждом разделе
        observed = []
        section_totals = {}
        
        total_chemical = 0
        
        for section, data in valid_sections.items():
            chemical_count = sum(1 for word in data['words'] 
                               if any(marker.lower() in word.lower() for marker in chemical_markers))
            total_count = len(data['words'])
            
            observed.append(chemical_count)
            section_totals[section] = total_count
            total_chemical += chemical_count
        
        total_words = sum(section_totals.values())
        
        # Защита от деления на ноль
        if total_words == 0:
            print("❌ Общее количество слов равно 0")
            return {'chi_square': 0, 'significant': False, 'observed': observed, 'expected': []}
        
        # Расчет ожидаемых частот
        expected = []
        for section in valid_sections.keys():
            expected_count = (section_totals[section] / total_words) * total_chemical
            expected.append(expected_count)
        
        # РАСЧЕТ ХИ-КВАДРАТ СО СТАНДАРТОМ ПИРСОНА (e >= 5)
        chi_square = 0
        valid_degrees_of_freedom = 0
        
        print(f"\n   Детализация расчета:")
        for i, (o, e) in enumerate(zip(observed, expected)):
            section_name = list(valid_sections.keys())[i]
            if e >= 5:  # Математический стандарт для критерия Пирсона
                contribution = ((o - e) ** 2) / e
                chi_square += contribution
                valid_degrees_of_freedom += 1
                print(f"      {section_name}: O={o}, E={e:.2f}, вклад={contribution:.2f} ✅")
            else:
                print(f"      {section_name}: O={o}, E={e:.2f} ⚠️ (E < 5, пропущено)")
        
        # Корректный расчет степеней свободы
        df = max(1, valid_degrees_of_freedom - 1)
        
        # Критическое значение зависит от df
        # Для df=1: χ²(0.05) = 3.84
        # Для df=2: χ²(0.05) = 5.99
        # Для df=3: χ²(0.05) = 7.81
        critical_values = {1: 3.84, 2: 5.99, 3: 7.81, 4: 9.49}
        critical_value = critical_values.get(df, 10.0)
        
        significant = chi_square > critical_value
        
        print(f"\n   Хи-квадрат: {chi_square:.2f}")
        print(f"   Степени свободы: {df}")
        print(f"   Критическое значение (p=0.05): {critical_value:.2f}")
        print(f"   Значимость: {'✅ ЗНАЧИМО' if significant else '❌ НЕ ЗНАЧИМО'}")
        
        return {
            'chi_square': chi_square,
            'df': df,
            'critical_value': critical_value,
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
        print("🧪 VOYNICH THERMODYNAMIC ANALYZER v5.1")
        print("   Научное исследование с TF-IDF и статистической проверкой")
        print("   Исправления: регистронезависимость + защита от деления на ноль")
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
            if section in self.tfidf.tfidf_scores:
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
        sample_words = ['qokain', 'olkeedy', 'shedy', 'qotolfchedy', 'roly', 'otaiin']
        for word in sample_words:
            analysis = self.morphology.analyze_word(word)
            if analysis and analysis['elements']:
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
            print(f"   Хи-квадрат тест значим (χ²={chi_square_result['chi_square']:.2f}, df={chi_square_result['df']})")
        else:
            print("❌ ГИПОТЕЗА НЕ ПОДТВЕРЖДЕНА")
            if not hypothesis_result['confirmed']:
                print("   - Химические маркеры не сконцентрированы в биологическом разделе")
            if not chi_square_result['significant']:
                print(f"   - Распределение не значимо (χ²={chi_square_result['chi_square']:.2f} < {chi_square_result['critical_value']:.2f})")
            print("   Необходимо пересмотреть морфологическую матрицу")


# ============================================================
# ТОЧКА ВХОДА
# ============================================================

if __name__ == "__main__":
    FILE_PATH = 'ZL3b-n.txt'
    
    analyzer = VoynichThermodynamicAnalyzer(FILE_PATH)
    analyzer.run_full_analysis()
