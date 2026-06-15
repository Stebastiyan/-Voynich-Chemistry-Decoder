#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ВОЙНИЧ = ТЕХНОЛОГИЧЕСКОЕ ПОСОБИЕ (XV век)
Анализатор транслитерации ZL3b-n.txt

ПРИНЦИПЫ (без фантомной морфологии):
1. Частотность определяет тип слова:
   - <5 вхождений = уникальная сущность (название растения, редкий реагент)
   - 5-50 вхождений = специфический термин
   - >50 вхождений = базовый процесс/операция

2. Контекст определяет смысл:
   - Первое слово абзаца в ботанике = название растения
   - Слова рядом с иллюстрацией трубы = операции с жидкостью
   - Слова в круговых диаграммах = календарные маркеры

3. Визуальное соответствие:
   - Текст должен соответствовать иллюстрации
   - Нимфы = точки пробоотбора/операции
   - Трубы = каналы перетока

4. Разделы имеют разную структуру:
   - Ботаника (f1r-f66v): каталог растений
   - Астрономия (f67r-f73v): календарь работ
   - Банный (f75r-f84v): химические процессы
   - Фармацевтика (f99r-f116v): рецепты и фасовка

Автор: на основе совместного исследования
Дата: 2026
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from collections import Counter, defaultdict
import json


# ============================================================
# РАЗДЕЛ 1: ОПРЕДЕЛЕНИЕ РАЗДЕЛОВ РУКОПИСИ
# ============================================================

@dataclass
class SectionDef:
    """Определение раздела по диапазону фолио."""
    name: str
    name_ru: str
    start_folio: int
    end_folio: int
    description: str
    expected_chem_density: float  # Ожидаемая плотность "химических" слов


SECTIONS = [
    SectionDef(
        name='herbal',
        name_ru='Ботанический (травник)',
        start_folio=1,
        end_folio=66,
        description='Каталог растений. Каждое растение = страница с иллюстрацией.',
        expected_chem_density=0.3
    ),
    SectionDef(
        name='astronomical',
        name_ru='Астрономический (календарь)',
        start_folio=67,
        end_folio=73,
        description='Зодиакальные круги. Календарь сельскохозяйственных работ.',
        expected_chem_density=0.15
    ),
    SectionDef(
        name='biological',
        name_ru='Банный (химические процессы)',
        start_folio=75,
        end_folio=84,
        description='Схемы реакторов: трубы, бассейны, нимфы. Дистилляция, фильтрация.',
        expected_chem_density=0.7
    ),
    SectionDef(
        name='pharmaceutical',
        name_ru='Фармацевтический (рецепты)',
        start_folio=85,
        end_folio=116,
        description='Рецепты, банки с этикетками, многоступенчатые трубы.',
        expected_chem_density=0.6
    ),
]


def get_section(folio_num: int) -> Optional[SectionDef]:
    """Определить раздел по номеру фолио."""
    for section in SECTIONS:
        if section.start_folio <= folio_num <= section.end_folio:
            return section
    return None


# ============================================================
# РАЗДЕЛ 2: БАЗА ДАННЫХ ИЗВЕСТНЫХ СООТВЕТСТВИЙ
# ============================================================

# Названия растений (первое слово абзаца в ботанике)
# Формат: {folio: (plant_name, confidence)}
KNOWN_PLANTS = {
    'f1v': ('Atropa belladonna / Solanum nigrum', 0.7),
    'f2r': ('Cyanus segelis (василёк)', 0.8),
    'f2v': ('Nymphoides peltata / водяная лилия', 0.7),
    'f3r': ('Crassulatea (диктамн критский)', 0.6),
    'f4r': ('Hypericum (зверобой)', 0.7),
    'f4v': ('Convolvulus / Ipomea (вьюнок)', 0.6),
    'f5r': ('Herba Paris / Indian Cucumber', 0.5),
    'f6r': ('Asclepiades (ластовень)', 0.6),
    'f6v': ('Ricinus communis (клещевина)', 0.8),
    'f7r': ('Nymphaea alba (кувшинка)', 0.8),
    'f8r': ('Praenanthes / Atriplex', 0.5),
    'f9r': ('Chelidonium Majus (чистотел)', 0.8),
    'f9v': ('Viola tricoloris (фиалка)', 0.7),
    'f10r': ('Scabiosa (короставник)', 0.7),
    'f13r': ('Tussilago (мать-и-мачеха)', 0.7),
    'f13v': ('Crassulatea Fetthenne (очиток)', 0.6),
    'f14r': ('Sagittaria (стрелолист)', 0.6),
    'f14v': ('Osmunda (папоротник)', 0.6),
    'f15r': ('Thistle (чертополох)', 0.7),
    'f15v': ('Paris Quadrifolia (вороний глаз)', 0.8),
    'f16r': ('Cannabis sativa (конопля)', 0.8),
    'f20r': ('Polytrichum (мох)', 0.6),
    'f25r': ('Nettle / Mint (крапива/мята)', 0.6),
    'f26r': ('Artemisia absinthium (полынь)', 0.7),
    'f26v': ('Verbena (вербена)', 0.7),
    'f27r': ('Asarum (копытень)', 0.6),
    'f28r': ('Arum (аронник)', 0.6),
    'f30v': ('Boragine (бурачник)', 0.6),
    'f32r': ('Mentastrum / Brunella (мята)', 0.7),
    'f32v': ('Campanula / Archangelica', 0.6),
    'f35r': ('Orchid root (корень орхидеи)', 0.6),
    'f35v': ('Quercus (дуб)', 0.7),
    'f36r': ('Geranium (герань)', 0.7),
    'f36v': ('Indian hemp (индийская конопля)', 0.7),
    'f37r': ('Valeriana (валериана)', 0.8),
    'f38v': ('Cichorium / Lactuca (цикорий)', 0.6),
    'f39r': ('Crocus sativus (шафран)', 0.8),
    'f40v': ('Thistle / Artichoke (артишок)', 0.7),
    'f41v': ('Plain carrot (дикая морковь)', 0.6),
    'f46r': ('Asclepias (ваточник)', 0.6),
    'f46v': ('Boragine / Anchusa', 0.5),
    'f50r': ('Artichoke / Sunflower', 0.7),
    'f51r': ('Mandragora (мандрагора)', 0.8),
    'f53r': ('Inula helenium (девясил)', 0.7),
    'f56r': ('Boragine / Dianthus', 0.5),
    'f66v': ('Primula (первоцвет)', 0.7),
    'f87r': ('Herbal (почерк 4)', 0.3),
    'f90v2': ('Xerantrium / Osmunda regalis', 0.5),
    'f93r': ('American Sunflower', 0.6),
    'f94r': ('Lunaria (лунник)', 0.6),
    'f95v1': ('Artemisia Absinthium (вермут)', 0.7),
    'f96r': ('Calendula (календула)', 0.7),
    'f96v': ('Smilax / Chenopodium', 0.5),
}


# Ключевые технологические слова (высокочастотные, >50 вхождений)
# Эти слова встречаются во всех разделах = базовые операции
HIGH_FREQ_WORDS = {
    'qokain': 'готовый продукт / осадок',
    'qokedy': 'завершить процесс',
    'shedy': 'слить / отделить',
    'chedy': 'добавить / внести',
    'daiin': 'сырьё / растительная масса',
    'ol': 'масло / спирт',
    'chol': 'нагрев',
    'otal': 'труба / канал',
    'cthy': 'студень / конденсат',
    'saiin': 'чистая вода / дистиллят',
    'sol': 'соль / раствор',
    'lchedy': 'охлаждение',
    'qokeedy': 'довести до готовности',
    'okeey': 'готовый выход',
    'or': 'активная фаза',
    'ar': 'основа / матрица',
    'am': 'среда / объём',
    'dar': 'добавка / реагент',
    'dy': 'мера / доза',
    'qokar': 'испарился / выпарился',
    'qokary': 'расслоился',
    'qokaldy': 'кристаллизовался',
    'otaldy': 'холод / замерзание',
    'otoky': 'оттепель',
    'ykees.ary': 'пахота / обработка поля',
    'dalary': 'отдыхающее поле / под паром',
    'ary': 'поле / покров',
    'dal': 'отдых / покой',
    'opar': 'слив / фильтрация',
    'roly': 'смешивание в поток',
    'doly': 'доливание в поток',
}


# Редкие слова (<5 вхождений) = уникальные сущности
# Эти слова встречаются только в特定ных контекстах
RARE_WORDS_CONTEXT = {
    'kooiin': 'название растения (ирис/водяная лилия)',
    'kydainy': 'название растения (василёк)',
    'koary,sar': 'название растения (клещевина)',
    'poror': 'название растения (вороний глаз)',
    'tsholdchy': 'название растения (мандрагора)',
    'chepchey': 'редкий реагент/инструмент (3 раза)',
    'olkeedy': 'алкидный эфир (специфический продукт)',
}


# ============================================================
# РАЗДЕЛ 3: ЗАГРУЗЧИК ДАННЫХ
# ============================================================

class VoynichLoader:
    """Загрузка и парсинг EVA-транскрипции."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.raw_data = None
        self.pages = {}  # {folio: [lines]}
        self.paragraphs = []  # [(folio, para_num, text)]
    
    def load(self) -> bool:
        """Загрузить файл."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.raw_data = f.read()
            print(f"✅ Загружено {len(self.raw_data)} символов из {self.filepath}")
            return True
        except Exception as e:
            print(f"❌ Ошибка загрузки: {e}")
            return False
    
    def parse(self):
        """Разобрать данные по страницам и абзацам."""
        if not self.raw_data:
            return
        
        print("🔍 Разбор по страницам...")
        
        current_folio = None
        current_para = 0
        current_lines = []
        
        for line in self.raw_data.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Определяем номер страницы
            page_match = re.match(r'<(f\d+[rv]?\d*)', line)
            if page_match:
                # Сохраняем предыдущую страницу
                if current_folio and current_lines:
                    self.pages[current_folio] = current_lines
                
                current_folio = page_match.group(1)
                current_para = 0
                current_lines = []
            
            # Определяем абзац
            para_match = re.match(r'<[^>]*@P\d', line)
            if para_match:
                current_para += 1
                # Извлекаем текст (после <%>)
                text_match = re.search(r'<%>(.+)', line)
                if text_match:
                    text = text_match.group(1).strip()
                    self.paragraphs.append((current_folio, current_para, text))
            
            current_lines.append(line)
        
        # Сохраняем последнюю страницу
        if current_folio and current_lines:
            self.pages[current_folio] = current_lines
        
        print(f"✅ Найдено {len(self.pages)} страниц, {len(self.paragraphs)} абзацев")
    
    def get_folio_number(self, folio_str: str) -> int:
        """Извлечь номер фолио из строки (f83r -> 83)."""
        match = re.search(r'f(\d+)', folio_str)
        if match:
            return int(match.group(1))
        return 0
    
    def get_words_from_paragraph(self, text: str) -> List[str]:
        """Извлечь слова из текста абзаца."""
        # Разделяем по точкам и пробелам
        words = re.findall(r'[a-zA-Z0-9@{}]+', text)
        return [w.lower() for w in words if len(w) >= 2]


# ============================================================
# РАЗДЕЛ 4: ЧАСТОТНЫЙ АНАЛИЗ
# ============================================================

class FrequencyAnalyzer:
    """Анализ частотности слов для определения их типа."""
    
    def __init__(self, loader: VoynichLoader):
        self.loader = loader
        self.word_freq = Counter()  # Общая частота
        self.word_sections = defaultdict(set)  # В каких разделах встречается
        self.word_first_in_para = Counter()  # Первое слово в абзаце
    
    def analyze(self):
        """Провести частотный анализ."""
        print("📊 Частотный анализ...")
        
        for folio, para_num, text in self.loader.paragraphs:
            words = self.loader.get_words_from_paragraph(text)
            
            if words:
                # Первое слово в абзаце
                self.word_first_in_para[words[0]] += 1
                
                for word in words:
                    self.word_freq[word] += 1
                    
                    # Определяем раздел
                    folio_num = self.loader.get_folio_number(folio)
                    section = get_section(folio_num)
                    if section:
                        self.word_sections[word].add(section.name)
        
        print(f"✅ Проанализировано {len(self.word_freq)} уникальных слов")
    
    def classify_word(self, word: str) -> Dict:
        """Классифицировать слово по частоте и контексту."""
        freq = self.word_freq.get(word, 0)
        sections = self.word_sections.get(word, set())
        first_in_para = self.word_first_in_para.get(word, 0)
        
        # Определяем тип
        if freq < 5:
            word_type = 'rare_entity'  # Уникальная сущность
        elif freq < 50:
            word_type = 'specific_term'  # Специфический термин
        else:
            word_type = 'base_process'  # Базовый процесс
        
        # Проверяем, является ли названием растения
        is_plant_name = False
        if first_in_para > 0 and 'herbal' in sections:
            # Если слово часто встречается первым в абзаце ботаники
            # и редко в других разделах
            if len(sections) <= 2 and freq < 10:
                is_plant_name = True
        
        return {
            'word': word,
            'frequency': freq,
            'sections': list(sections),
            'first_in_para': first_in_para,
            'type': word_type,
            'is_plant_name': is_plant_name,
        }
    
    def get_top_words(self, n: int = 50) -> List[Dict]:
        """Получить топ-N слов по частоте."""
        results = []
        for word, freq in self.word_freq.most_common(n):
            classification = self.classify_word(word)
            results.append(classification)
        return results
    
    def get_plant_names(self) -> List[Dict]:
        """Найти вероятные названия растений."""
        results = []
        for word, count in self.word_first_in_para.most_common():
            if count >= 1:  # Хотя бы раз первое слово
                classification = self.classify_word(word)
                if classification['is_plant_name']:
                    results.append(classification)
        return results[:50]  # Топ-50


# ============================================================
# РАЗДЕЛ 5: АНАЛИЗАТОР РАЗДЕЛОВ
# ============================================================

class SectionAnalyzer:
    """Анализ структуры разделов."""
    
    def __init__(self, loader: VoynichLoader, freq_analyzer: FrequencyAnalyzer):
        self.loader = loader
        self.freq = freq_analyzer
        self.section_stats = defaultdict(lambda: {
            'pages': 0,
            'paragraphs': 0,
            'words': 0,
            'unique_words': set(),
            'high_freq_words': Counter(),
            'rare_words': Counter(),
        })
    
    def analyze(self):
        """Анализировать каждый раздел."""
        print("📚 Анализ разделов...")
        
        for folio, para_num, text in self.loader.paragraphs:
            folio_num = self.loader.get_folio_number(folio)
            section = get_section(folio_num)
            
            if section:
                stats = self.section_stats[section.name]
                stats['pages'] += 1
                stats['paragraphs'] += 1
                
                words = self.loader.get_words_from_paragraph(text)
                stats['words'] += len(words)
                stats['unique_words'].update(words)
                
                # Считаем высокочастотные и редкие слова
                for word in words:
                    if self.freq.word_freq.get(word, 0) >= 50:
                        stats['high_freq_words'][word] += 1
                    elif self.freq.word_freq.get(word, 0) < 5:
                        stats['rare_words'][word] += 1
        
        print(f"✅ Проанализировано {len(self.section_stats)} разделов")
    
    def get_report(self) -> str:
        """Сгенерировать отчёт по разделам."""
        report = []
        report.append("=" * 70)
        report.append("📚 ОТЧЁТ ПО РАЗДЕЛАМ РУКОПИСИ")
        report.append("=" * 70)
        
        for section in SECTIONS:
            if section.name not in self.section_stats:
                continue
            
            stats = self.section_stats[section.name]
            
            report.append(f"\n{'─' * 70}")
            report.append(f"📖 {section.name_ru} ({section.name})")
            report.append(f"   Фолио: f{section.start_folio}r - f{section.end_folio}v")
            report.append(f"   Описание: {section.description}")
            report.append(f"{'─' * 70}")
            
            report.append(f"\n📊 Статистика:")
            report.append(f"   Страниц: {stats['pages']}")
            report.append(f"   Абзацев: {stats['paragraphs']}")
            report.append(f"   Слов всего: {stats['words']}")
            report.append(f"   Уникальных слов: {len(stats['unique_words'])}")
            
            # Плотность химических терминов
            chem_density = stats['high_freq_words'].total() / stats['words'] if stats['words'] > 0 else 0
            report.append(f"   Плотность базовых терминов: {chem_density:.1%}")
            report.append(f"   Ожидаемая плотность: {section.expected_chem_density:.1%}")
            
            # Топ высокочастотных слов
            if stats['high_freq_words']:
                report.append(f"\n   🔹 Топ базовых терминов:")
                for word, count in stats['high_freq_words'].most_common(10):
                    meaning = HIGH_FREQ_WORDS.get(word, '?')
                    report.append(f"      {word}: {count} раз ({meaning})")
            
            # Редкие слова
            if stats['rare_words']:
                report.append(f"\n   🔹 Редкие слова (уникальные сущности):")
                for word, count in stats['rare_words'].most_common(10):
                    context = RARE_WORDS_CONTEXT.get(word, 'неизвестно')
                    report.append(f"      {word}: {count} раз ({context})")
        
        return '\n'.join(report)


# ============================================================
# РАЗДЕЛ 6: АНАЛИЗАТОР БОТАНИЧЕСКОГО РАЗДЕЛА
# ============================================================

class BotanicalAnalyzer:
    """Анализ ботанического раздела (каталог растений)."""
    
    def __init__(self, loader: VoynichLoader, freq_analyzer: FrequencyAnalyzer):
        self.loader = loader
        self.freq = freq_analyzer
        self.plant_pages = []  # [(folio, first_word, plant_name)]
    
    def analyze(self):
        """Найти страницы с растениями."""
        print("🌿 Анализ ботанического раздела...")
        
        for folio, para_num, text in self.loader.paragraphs:
            folio_num = self.loader.get_folio_number(folio)
            
            # Только ботанический раздел
            if not (1 <= folio_num <= 66):
                continue
            
            # Только первый абзац на странице
            if para_num != 1:
                continue
            
            words = self.loader.get_words_from_paragraph(text)
            if words:
                first_word = words[0]
                plant_name = KNOWN_PLANTS.get(folio, 'не идентифицировано')
                self.plant_pages.append((folio, first_word, plant_name))
        
        print(f"✅ Найдено {len(self.plant_pages)} страниц с растениями")
    
    def get_report(self) -> str:
        """Отчёт по растениям."""
        report = []
        report.append("=" * 70)
        report.append("🌿 КАТАЛОГ РАСТЕНИЙ (ботанический раздел)")
        report.append("=" * 70)
        
        for folio, first_word, plant_name in self.plant_pages[:30]:
            report.append(f"\n📄 {folio}:")
            report.append(f"   Первое слово: {first_word}")
            report.append(f"   Растение: {plant_name}")
            
            # Проверяем частоту первого слова
            word_info = self.freq.classify_word(first_word)
            report.append(f"   Частота слова: {word_info['frequency']}")
            report.append(f"   Тип: {word_info['type']}")
        
        return '\n'.join(report)


# ============================================================
# РАЗДЕЛ 7: АНАЛИЗАТОР БАННОГО РАЗДЕЛА
# ============================================================

class BathAnalyzer:
    """Анализ "банного" раздела (химические процессы)."""
    
    def __init__(self, loader: VoynichLoader, freq_analyzer: FrequencyAnalyzer):
        self.loader = loader
        self.freq = freq_analyzer
        self.process_pages = []  # [(folio, words, analysis)]
    
    def analyze(self):
        """Анализировать страницы с химическими процессами."""
        print("🧪 Анализ банного раздела...")
        
        for folio, para_num, text in self.loader.paragraphs:
            folio_num = self.loader.get_folio_number(folio)
            
            # Только банный раздел
            if not (75 <= folio_num <= 84):
                continue
            
            words = self.loader.get_words_from_paragraph(text)
            
            # Анализируем паттерны
            analysis = self.analyze_process(words)
            self.process_pages.append((folio, words, analysis))
        
        print(f"✅ Проанализировано {len(self.process_pages)} абзацев")
    
    def analyze_process(self, words: List[str]) -> Dict:
        """Анализировать процесс по словам."""
        # Считаем ключевые операции
        operations = Counter()
        
        for word in words:
            if word in HIGH_FREQ_WORDS:
                operations[word] += 1
        
        # Определяем тип процесса
        process_type = 'unknown'
        
        if operations.get('otal', 0) > 3 and operations.get('lchedy', 0) > 2:
            process_type = 'дистилляция/конденсация'
        elif operations.get('opar', 0) > 2 or operations.get('roly', 0) > 1:
            process_type = 'фильтрация/смешивание'
        elif operations.get('chepchey', 0) > 0:
            process_type = 'специфическая операция (редкий реагент)'
        elif operations.get('olkeedy', 0) > 1:
            process_type = 'синтез алкидов'
        elif operations.get('qokain', 0) > 3:
            process_type = 'осаждение/получение продукта'
        
        return {
            'process_type': process_type,
            'operations': dict(operations.most_common(10)),
            'word_count': len(words),
        }
    
    def get_report(self) -> str:
        """Отчёт по химическим процессам."""
        report = []
        report.append("=" * 70)
        report.append("🧪 ХИМИЧЕСКИЕ ПРОЦЕССЫ (банный раздел)")
        report.append("=" * 70)
        
        # Группируем по типу процесса
        process_types = defaultdict(list)
        for folio, words, analysis in self.process_pages:
            process_types[analysis['process_type']].append(folio)
        
        for process_type, folios in process_types.items():
            report.append(f"\n🔬 {process_type}:")
            report.append(f"   Страницы: {', '.join(folios[:10])}")
            report.append(f"   Количество: {len(folios)}")
        
        # Примеры процессов
        report.append(f"\n{'─' * 70}")
        report.append("📋 ПРИМЕРЫ ПРОЦЕССОВ:")
        
        for folio, words, analysis in self.process_pages[:5]:
            report.append(f"\n📄 {folio}:")
            report.append(f"   Тип: {analysis['process_type']}")
            report.append(f"   Операции: {analysis['operations']}")
            report.append(f"   Текст: {' '.join(words[:10])}...")
        
        return '\n'.join(report)


# ============================================================
# РАЗДЕЛ 8: АНАЛИЗАТОР АСТРОНОМИЧЕСКОГО РАЗДЕЛА
# ============================================================

class AstronomicalAnalyzer:
    """Анализ астрономического раздела (календарь)."""
    
    def __init__(self, loader: VoynichLoader, freq_analyzer: FrequencyAnalyzer):
        self.loader = loader
        self.freq = freq_analyzer
        self.calendar_entries = []  # [(folio, words, analysis)]
    
    def analyze(self):
        """Анализировать календарные записи."""
        print("🌙 Анализ астрономического раздела...")
        
        for folio, para_num, text in self.loader.paragraphs:
            folio_num = self.loader.get_folio_number(folio)
            
            # Только астрономический раздел
            if not (67 <= folio_num <= 73):
                continue
            
            words = self.loader.get_words_from_paragraph(text)
            
            # Ищем календарные маркеры
            analysis = self.analyze_calendar(words)
            self.calendar_entries.append((folio, words, analysis))
        
        print(f"✅ Проанализировано {len(self.calendar_entries)} записей")
    
    def analyze_calendar(self, words: List[str]) -> Dict:
        """Анализировать календарную запись."""
        # Ищем маркеры месяцев/сезонов
        month_markers = []
        
        for word in words:
            if word in ['otaldy', 'otoky', 'seeaiir', 'ykees.ary', 
                       'sosaiir', 'oteey.dar', 'yto,daiir', 'sheosam',
                       'ykeeody', 'okeol.sal', 'okeey.sar', 'dalary']:
                month_markers.append(word)
        
        # Определяем сезон
        season = 'unknown'
        if 'otaldy' in month_markers:
            season = 'январь (холод)'
        elif 'otoky' in month_markers:
            season = 'февраль (оттепель)'
        elif 'ykees.ary' in month_markers:
            season = 'апрель (пахота)'
        elif 'dalary' in month_markers:
            season = 'декабрь (отдыхающее поле)'
        
        return {
            'season': season,
            'month_markers': month_markers,
            'word_count': len(words),
        }
    
    def get_report(self) -> str:
        """Отчёт по календарю."""
        report = []
        report.append("=" * 70)
        report.append("🌙 КАЛЕНДАРЬ СЕЛЬСКОХОЗЯЙСТВЕННЫХ РАБОТ")
        report.append("   (астрономический раздел)")
        report.append("=" * 70)
        
        # Группируем по сезону
        seasons = defaultdict(list)
        for folio, words, analysis in self.calendar_entries:
            if analysis['season'] != 'unknown':
                seasons[analysis['season']].append(folio)
        
        for season, folios in seasons.items():
            report.append(f"\n📅 {season}:")
            report.append(f"   Страницы: {', '.join(folios)}")
        
        # 12 радиальных подписей (f67r1)
        report.append(f"\n{'─' * 70}")
        report.append("📆 12 МЕСЯЦЕВ (f67r1):")
        
        months = [
            ('otaldy', 'январь - холод'),
            ('otoky', 'февраль - оттепель'),
            ('seeaiir', 'март - разливы/сев'),
            ('ykees.ary', 'апрель - пахота'),
            ('sosaiir', 'май - посев'),
            ('oteey.dar', 'июнь - прополка'),
            ('yto,daiir', 'июль - жатва'),
            ('sheosam', 'август - сбор'),
            ('ykeeody', 'сентябрь - конец сбора'),
            ('okeol.sal', 'октябрь - пожелтение'),
            ('okeey.sar', 'ноябрь - орехи'),
            ('dalary', 'декабрь - отдыхающее поле'),
        ]
        
        for month_word, meaning in months:
            report.append(f"   {month_word:15} = {meaning}")
        
        return '\n'.join(report)


# ============================================================
# РАЗДЕЛ 9: ГЛАВНЫЙ АНАЛИЗАТОР
# ============================================================

class VoynichAnalyzer:
    """Главный анализатор рукописи."""
    
    def __init__(self, filepath: str):
        self.loader = VoynichLoader(filepath)
        self.freq_analyzer = None
        self.section_analyzer = None
        self.botanical_analyzer = None
        self.bath_analyzer = None
        self.astronomical_analyzer = None
    
    def run(self):
        """Запустить полный анализ."""
        print("=" * 70)
        print("🧪 ВОЙНИЧ = ТЕХНОЛОГИЧЕСКОЕ ПОСОБИЕ (XV век)")
        print("   Анализатор без фантомной морфологии")
        print("=" * 70)
        
        # 1. Загрузка
        if not self.loader.load():
            return
        
        self.loader.parse()
        
        # 2. Частотный анализ
        self.freq_analyzer = FrequencyAnalyzer(self.loader)
        self.freq_analyzer.analyze()
        
        # 3. Анализ разделов
        self.section_analyzer = SectionAnalyzer(self.loader, self.freq_analyzer)
        self.section_analyzer.analyze()
        
        # 4. Анализ ботаники
        self.botanical_analyzer = BotanicalAnalyzer(self.loader, self.freq_analyzer)
        self.botanical_analyzer.analyze()
        
        # 5. Анализ банного раздела
        self.bath_analyzer = BathAnalyzer(self.loader, self.freq_analyzer)
        self.bath_analyzer.analyze()
        
        # 6. Анализ астрономии
        self.astronomical_analyzer = AstronomicalAnalyzer(self.loader, self.freq_analyzer)
        self.astronomical_analyzer.analyze()
        
        # 7. Генерация отчётов
        print("\n" + "=" * 70)
        print(" ГЕНЕРАЦИЯ ОТЧЁТОВ")
        print("=" * 70)
        
        reports = []
        
        reports.append(self.section_analyzer.get_report())
        reports.append(self.botanical_analyzer.get_report())
        reports.append(self.bath_analyzer.get_report())
        reports.append(self.astronomical_analyzer.get_report())
        
        # Сводный отчёт
        summary = self.generate_summary()
        reports.append(summary)
        
        full_report = '\n\n'.join(reports)
        
        # Вывод
        print(full_report)
        
        # Сохранение
        with open('voynich_analysis_v2.txt', 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        print(f"\n✅ Отчёт сохранён: voynich_analysis_v2.txt")
    
    def generate_summary(self) -> str:
        """Сводный отчёт."""
        report = []
        report.append("=" * 70)
        report.append("🏆 СВОДНЫЙ ОТЧЁТ")
        report.append("=" * 70)
        
        report.append("\n ОСНОВНЫЕ ВЫВОДЫ:")
        report.append("\n1. СТРУКТУРА РУКОПИСИ:")
        report.append("   - Ботаника (f1r-f66v): каталог из ~116 растений")
        report.append("   - Астрономия (f67r-f73v): календарь сельхозработ")
        report.append("   - Банный (f75r-f84v): химические процессы")
        report.append("   - Фармацевтика (f99r-f116v): рецепты и фасовка")
        
        report.append("\n2. ПРИНЦИПЫ ДЕШИФРОВКИ:")
        report.append("   - Частотность определяет тип слова")
        report.append("   - Контекст определяет смысл")
        report.append("   - Визуальное соответствие обязательно")
        
        report.append("\n3. КЛЮЧЕВЫЕ НАХОДКИ:")
        report.append("   - Названия растений = первые слова абзацев")
        report.append("   - 12 месяцев = радиальные подписи f67r1")
        report.append("   - Нимфы = точки пробоотбора")
        report.append("   - Трубы = каналы перетока")
        
        report.append("\n4. ЧЕСТНЫЕ ОГРАНИЧЕНИЯ:")
        report.append("   - Морфологический разбор без статистики = подгонка")
        report.append("   - Редкие слова (<5 раз) = уникальные сущности")
        report.append("   - Интерпретации требуют проверки на данных")
        
        return '\n'.join(report)


# ============================================================
# РАЗДЕЛ 10: ЗАПУСК
# ============================================================

def main():
    """Главная функция."""
    # Путь к файлу транскрипции
    filepath = 'ZL3b-n.txt'
    
    # Создаём анализатор
    analyzer = VoynichAnalyzer(filepath)
    
    # Запускаем анализ
    analyzer.run()


if __name__ == '__main__':
    main()
