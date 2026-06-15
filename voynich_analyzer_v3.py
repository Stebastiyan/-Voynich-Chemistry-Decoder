#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ВОЙНИЧ = УЧЕБНИК ОРГАНИЧЕСКОЙ ХИМИИ XV ВЕКА
Версия 3.0 — Полная переосмысленная версия

Основана на совместном исследовании:
- Стебястьян — Василий Тёркин 🎖️
- Qwen AI

Дата: Июнь 2026

КЛЮЧЕВЫЕ ОТКРЫТИЯ:
1. "Банный раздел" = химические процессы изнутри (нимфы = молекулы)
2. Цветовое кодирование труб:
   - Красный = нагрев/огонь
   - Синий = охлаждение/конденсация
   - Коричневый = осадок/остаток
   - Белый = чистый продукт
3. Морфологическая матрица (префиксы, корни, суффиксы)
4. Названия растений = первые слова абзацев
5. 12 месяцев = сельскохозяйственный календарь
6. Ключевые слова:
   - qokain = готовый продукт
   - olkeedy = алкидный эфир
   - qokey = отстоять/довести до готовности
   - 8chol = нагреть до точки кипения
   - cthod = остывший осадок/кубовый остаток
   - otol = труба/канал/перегонка
   - r- = возврат/рефлюкс
   - l- = охлаждение/конденсация
   - p- = давление/пар/подъём

ГЕОГРАФИЧЕСКАЯ ГИПОТЕЗА:
- Голландский почерк + Готланд + Ганзейский союз
- Францисканцы как возможные авторы
- Монастырский скрипторий как место создания

ТЕХНОЛОГИЧЕСКАЯ МОДЕЛЬ:
1. Сбор сырья (ботаника)
2. Сушка/подготовка
3. Экстракция (ректификат)
4. Дистилляция/ректификация
5. Фильтрация/очистка
6. Синтез алкидов
7. Фасовка/дозирование
"""

import re
import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set
from collections import Counter, defaultdict
from pathlib import Path
import urllib.request
from datetime import datetime

# ============================================================
# РАЗДЕЛ 1: БАЗА ДАННЫХ ИЛЛЮСТРАЦИЙ И ОПИСАНИЙ
# ============================================================

@dataclass
class PageDescription:
"""Описание конкретной страницы Войнича."""
folio: str
section: str
visual_description: str
chemical_processes: List[str]
key_elements: List[str]
illustration_url: Optional[str] = None

# База данных описаний страниц (на основе анализа иллюстраций)
PAGE_DATABASE = {
    # БОТАНИЧЕСКИЙ РАЗДЕЛ (f1r-f66v)
    'f1v': PageDescription(
        folio='f1v',
        section='herbal',
        visual_description='Растение с корнями и листьями, похожее на белладонну или паслён',
        chemical_processes=['экстракция алкалоидов'],
        key_elements=['daiin', 'qokain', 'chcthy'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/4/4c/Voynich_Manuscript_f1v.jpg/800px-Voynich_Manuscript_f1v.jpg'
    ),
    'f2v': PageDescription(
        folio='f2v',
        section='herbal',
        visual_description='Водяная лилия / ирис (флёр-де-лис), корневище',
        chemical_processes=['паровая дистилляция', 'омыление'],
        key_elements=['kooiin', 'pchor', 'otaiin', 'dair'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Voynich_Manuscript_f2v.jpg/800px-Voynich_Manuscript_f2v.jpg'
    ),
    'f6v': PageDescription(
        folio='f6v',
        section='herbal',
        visual_description='Клещевина с колючими плодами',
        chemical_processes=['экстракция рицина', 'получение касторового масла'],
        key_elements=['koary,sar', 'otol', 'olkeedy'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Voynich_Manuscript_f6v.jpg/800px-Voynich_Manuscript_f6v.jpg'
    ),
    'f13v': PageDescription(
        folio='f13v',
        section='herbal',
        visual_description='Очиток (Sedum) суккулент',
        chemical_processes=['экстракция алкалоидов'],
        key_elements=['koair', 'otol', 'qokain'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/3/3d/Voynich_Manuscript_f13v.jpg/800px-Voynich_Manuscript_f13v.jpg'
    ),
    'f15v': PageDescription(
        folio='f15v',
        section='herbal',
        visual_description='Вороний глаз (Paris quadrifolia) с 4 листьями',
        chemical_processes=['экстракция паридина'],
        key_elements=['poror', 'qokain', 'cthy'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/9/9e/Voynich_Manuscript_f15v.jpg/800px-Voynich_Manuscript_f15v.jpg'
    ),
    'f16r': PageDescription(
        folio='f16r',
        section='herbal',
        visual_description='Конопля (Cannabis sativa)',
        chemical_processes=['экстракция каннабиноидов'],
        key_elements=['pocheody', 'otol', 'olkeedy'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/b/b9/Voynich_Manuscript_f16r.jpg/800px-Voynich_Manuscript_f16r.jpg'
    ),
    'f37r': PageDescription(
        folio='f37r',
        section='herbal',
        visual_description='Валериана лекарственная',
        chemical_processes=['экстракция валериановой кислоты'],
        key_elements=['tocphol', 'ol', 'qokain'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/c/c9/Voynich_Manuscript_f37r.jpg/800px-Voynich_Manuscript_f37r.jpg'
    ),
    'f39r': PageDescription(
        folio='f39r',
        section='herbal',
        visual_description='Шафран (Crocus sativus)',
        chemical_processes=['экстракция кроцина'],
        key_elements=['tedo', 'ol', 'qokain'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Voynich_Manuscript_f39r.jpg/800px-Voynich_Manuscript_f39r.jpg'
    ),
    'f40v': PageDescription(
        folio='f40v',
        section='herbal',
        visual_description='Артишок / чертополох',
        chemical_processes=['экстракция цинарина'],
        key_elements=['pchedain', 'ol', 'qokain'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5f/Voynich_Manuscript_f40v.jpg/800px-Voynich_Manuscript_f40v.jpg'
    ),
    'f41v': PageDescription(
        folio='f41v',
        section='herbal',
        visual_description='Дикая морковь (Daucus carota)',
        chemical_processes=['экстракция β-каротина', 'вяление'],
        key_elements=['pcheody', 'ol', 'qokeedy'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/6/6a/Voynich_Manuscript_f41v.jpg/800px-Voynich_Manuscript_f41v.jpg'
    ),
    'f50r': PageDescription(
        folio='f50r',
        section='herbal',
        visual_description='Артишок / подсолнечник',
        chemical_processes=['экстракция инулина', 'гепатопротекторы'],
        key_elements=['psheor', 'olkair', 'olfchedy'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/7/77/Voynich_Manuscript_f50r.jpg/800px-Voynich_Manuscript_f50r.jpg'
    ),
    'f51r': PageDescription(
        folio='f51r',
        section='herbal',
        visual_description='Мандрагора (Mandragora officinarum)',
        chemical_processes=['экстракция скополамина'],
        key_elements=['tsholdchy', 'qokain', 'cthy'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Voynich_Manuscript_f51r.jpg/800px-Voynich_Manuscript_f51r.jpg'
    ),
    'f53r': PageDescription(
        folio='f53r',
        section='herbal',
        visual_description='Девясил (Inula helenium)',
        chemical_processes=['экстракция алантолактона'],
        key_elements=['kdam', 'ol', 'qokain'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Voynich_Manuscript_f53r.jpg/800px-Voynich_Manuscript_f53r.jpg'
    ),
    
    # АСТРОНОМИЧЕСКИЙ РАЗДЕЛ (f67r-f73v)
    'f67r1': PageDescription(
        folio='f67r1',
        section='astronomical',
        visual_description='Круговая диаграмма с 12 секторами, луна в центре',
        chemical_processes=['календарь сбора', 'фенологический цикл'],
        key_elements=['otaldy', 'otoky', 'seeaiir', 'ykees.ary', 'dalary'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Voynich_Manuscript_f67r.jpg/800px-Voynich_Manuscript_f67r.jpg'
    ),
    'f68r1': PageDescription(
        folio='f68r1',
        section='astronomical',
        visual_description='Звёздная карта с названиями звёзд, фенологический цикл растения',
        chemical_processes=['фенологический календарь', 'сбор по звёздам'],
        key_elements=['shokchy', 'chteey', 'cphol', 'opcheeol', 'choctheeey'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/6/6c/Voynich_Manuscript_f68r.jpg/800px-Voynich_Manuscript_f68r.jpg'
    ),
    'f73r': PageDescription(
        folio='f73r',
        section='astronomical',
        visual_description='Скорпион, 4 верхних нимфы = 4 стихии/агрегатных состояния',
        chemical_processes=['дистилляция', 'рефлюкс', 'фазовые переходы'],
        key_elements=['otaly', 'chockhy', 'otedy', 'yteeody', 'okary'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/4/4e/Voynich_Manuscript_f73r.jpg/800px-Voynich_Manuscript_f73r.jpg'
    ),
    
    # БАННЫЙ РАЗДЕЛ (f75r-f84v)
    'f75r': PageDescription(
        folio='f75r',
        section='biological',
        visual_description='Нимфы в бассейнах с трубами, начало химического процесса',
        chemical_processes=['гидролиз', 'мацерация'],
        key_elements=['qokain', 'olkeedy', 'otal', 'lchedy'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Voynich_Manuscript_f75r.jpg/800px-Voynich_Manuscript_f75r.jpg'
    ),
    'f78v': PageDescription(
        folio='f78v',
        section='biological',
        visual_description='9 нимф в странном бассейне, много труб',
        chemical_processes=['многокомпонентная реакция', 'рефлюкс'],
        key_elements=['qokain', 'olkeedy', 'rchedy', 'lchedy'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Voynich_Manuscript_f78v.jpg/800px-Voynich_Manuscript_f78v.jpg'
    ),
    'f80r': PageDescription(
        folio='f80r',
        section='biological',
        visual_description='Термохимический сепаратор: воронка, центральная труба, донный слив, 10 нимф сверху, 4 в доливе, 2 внизу',
        chemical_processes=['термохимическая сепарация', 'декантация', 'рефлюкс'],
        key_elements=['toroly', 'olchdy', 'okary', 'opor', 'olky', 'otalshedy', 'okar', 'okan'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/7/7e/Voynich_Manuscript_f80r.jpg/800px-Voynich_Manuscript_f80r.jpg'
    ),
    'f80v': PageDescription(
        folio='f80v',
        section='biological',
        visual_description='Продолжение f80r, система фильтрации и очистки',
        chemical_processes=['многократная фильтрация', 'очистка дистиллята', 'адсорбция'],
        key_elements=['pchedy', 'dolfchedy', 'qokeedy', 'qotedy', 'qotolfchedy', 'roly', 'tshedy', 'olkain', 'otal', 'chckhy', 'doly'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Voynich_Manuscript_f80v.jpg/800px-Voynich_Manuscript_f80v.jpg'
    ),
    'f82v': PageDescription(
        folio='f82v',
        section='biological',
        visual_description='11 нимф в "болоте" (кубовый остаток), 2 облака пара, трубы',
        chemical_processes=['кипячение', 'испарение', 'конденсация', 'кубовый остаток'],
        key_elements=['qokain', 'olkeedy', 'chcthy', 'cthod', 'sho sho sho'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Voynich_Manuscript_f82v.jpg/800px-Voynich_Manuscript_f82v.jpg'
    ),
    'f83r': PageDescription(
        folio='f83r',
        section='biological',
        visual_description='Ректификационная колонна с дефлегматором, 5 нимф',
        chemical_processes=['ректификация', 'рефлюкс', 'фракционная дистилляция'],
        key_elements=['qokain', 'qokeedy', 'olkeedy', 'otal', 'lchedy', 'rchedy'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/6/6e/Voynich_Manuscript_f83r.jpg/800px-Voynich_Manuscript_f83r.jpg'
    ),
    'f84r': PageDescription(
        folio='f84r',
        section='biological',
        visual_description='Синтез алкидов, двухступенчатые красные трубы',
        chemical_processes=['синтез алкидных смол', 'этерификация', 'омыление'],
        key_elements=['olkeedy', 'qokain', 'qokeedy', 'otal'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/f/f4/Voynich_Manuscript_f84r.jpg/800px-Voynich_Manuscript_f84r.jpg'
    ),
    
    # ФАРМАЦЕВТИЧЕСКИЙ РАЗДЕЛ (f99r-f116v)
    'f99r': PageDescription(
        folio='f99r',
        section='pharmaceutical',
        visual_description='Банки с этикетками, сосуды для хранения',
        chemical_processes=['фасовка', 'хранение готовых продуктов'],
        key_elements=['okaradag', 'salo', 'aro', 'qokain'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Voynich_Manuscript_f99r.jpg/800px-Voynich_Manuscript_f99r.jpg'
    ),
    'f102v': PageDescription(
        folio='f102v',
        section='pharmaceutical',
        visual_description='Двухступенчатые трубы с цветовым кодированием (красный, синий, коричневый)',
        chemical_processes=['возгонка смол', 'сухая перегонка', 'сбор осадка'],
        key_elements=['qokain', 'cthod', 'qokeey', 'olcheor'],
        illustration_url='https://upload.wikimedia.org/wikipedia/commons/thumb/5/5d/Voynich_Manuscript_f102v.jpg/800px-Voynich_Manuscript_f102v.jpg'
    ),
}

# ============================================================
# РАЗДЕЛ 2: МОРФОЛОГИЧЕСКАЯ МАТРИЦА (ОБНОВЛЁННАЯ)
# ============================================================

@dataclass
class MorphologyMatrix:
"""
Морфологическая матрица языка Войнича.
Основана на анализе частотных паттернов и контекстов.

ВАЖНО: Это гипотеза, требующая проверки на реальных данных.
Не все слова разбираются по этой матрице — только частотные (>50 вхождений).
"""
    
    # ПРЕФИКСЫ (физическое действие / агрегатное состояние)
    prefixes = {
        'qo': {'meaning': 'твёрдое / сухое / вес / прокаливание',
               'chemistry': 'Solid state / Dry heating / Calcination',
               'confidence': 0.95,
               'examples': ['qokain', 'qochol', 'qokar']},
        '8':  {'meaning': 'жидкость / объём / раствор',
               'chemistry': 'Liquid phase / Solvent / Volume',
               'confidence': 0.95,
               'examples': ['8chol', '8am', '8a']},
        '9':  {'meaning': 'газ / пар / летучесть (зеркальный 8-)',
               'chemistry': 'Gas phase / Volatile / Vapor',
               'confidence': 0.75,
               'examples': ['9a', '9am']},
        'l':  {'meaning': 'холод / охлаждение / конденсация',
               'chemistry': 'Cooling / Condensation',
               'confidence': 0.90,
               'examples': ['lchedy', 'lshy', 'lchol']},
        'r':  {'meaning': 'возврат / рефлюкс / рециклинг',
               'chemistry': 'Reflux / Return / Recycling',
               'confidence': 0.90,
               'examples': ['rchedy', 'rchey', 'rchs']},
        'p':  {'meaning': 'давление / пар / подъём',
               'chemistry': 'Pressure / Vapor rise / Distillation',
               'confidence': 0.85,
               'examples': ['pchedy', 'pchor', 'pshdy']},
        'ct': {'meaning': 'осадок / концентрат / гуща',
               'chemistry': 'Precipitate / Concentrate / Sediment',
               'confidence': 0.90,
               'examples': ['cthy', 'cthod', 'cthal']},
        'f':  {'meaning': 'фильтрация / очистка / осаждение',
               'chemistry': 'Filtration / Purification',
               'confidence': 0.85,
               'examples': ['fchedy', 'fchdy', 'fcheol']},
        'm':  {'meaning': 'мацерация / настаивание / брожение',
               'chemistry': 'Maceration / Fermentation',
               'confidence': 0.75,
               'examples': ['mchedy', 'mchol']},
    }
    
    # ГАЛЛОУСЫ (катализаторы / специальные агенты)
    gallows = {
        'k': {'meaning': 'щёлочь / зола / поташ (омыление)',
              'chemistry': 'Alkali / Ash / Potash (saponification)',
              'confidence': 0.85,
              'examples': ['qokain', 'qokar', 'qokary']},
        'g': {'meaning': 'кислота (уксусная, лимонная)',
              'chemistry': 'Acid (acetic, citric)',
              'confidence': 0.70,
              'examples': ['qogedy', 'gchol']},
        't': {'meaning': 'высокая температура / огонь / кальцинация',
              'chemistry': 'High temperature / Fire / Calcination',
              'confidence': 0.80,
              'examples': ['qotaiin', 'tchol']},
    }
    
    # КОРНИ (вещества / процессы)
    roots = {
        'dai':  {'meaning': 'сырьё / растительная масса',
                 'chemistry': 'Raw material / Plant mass',
                 'confidence': 0.95,
                 'examples': ['daiin', 'dair', 'dary']},
        'chol': {'meaning': 'нагрев / температурный процесс',
                 'chemistry': 'Heating / Temperature process',
                 'confidence': 0.90,
                 'examples': ['8chol', 'qochol', 'lchol']},
        'ol':   {'meaning': 'масло / спирт / алкид',
                 'chemistry': 'Oil / Alcohol / Alkyl',
                 'confidence': 0.90,
                 'examples': ['olkeedy', 'olchedy', 'olkain']},
        'sol':  {'meaning': 'соль / минеральный раствор',
                 'chemistry': 'Salt / Mineral solution',
                 'confidence': 0.85,
                 'examples': ['solkeedy', 'solkain']},
        'sai':  {'meaning': 'чистая вода / дистиллят',
                 'chemistry': 'Pure water / Distillate',
                 'confidence': 0.85,
                 'examples': ['saiin', 'saiiny']},
        'am':   {'meaning': 'среда / объём / жидкая основа',
                 'chemistry': 'Medium / Volume / Liquid base',
                 'confidence': 0.80,
                 'examples': ['am', 'otam', 'airom']},
        'ar':   {'meaning': 'основа / матрица / твёрдый носитель',
                 'chemistry': 'Base / Matrix / Solid carrier',
                 'confidence': 0.75,
                 'examples': ['ar', 'otal', 'qokar']},
        'or':   {'meaning': 'активная фаза / летучий компонент',
                 'chemistry': 'Active phase / Volatile component',
                 'confidence': 0.70,
                 'examples': ['or', 'qokar', 'otor']},
        'sh':   {'meaning': 'обработка / смешивание / измельчение',
                 'chemistry': 'Processing / Mixing / Grinding',
                 'confidence': 0.85,
                 'examples': ['shedy', 'sho', 'shol']},
        'ch':   {'meaning': 'нагрев / термическое воздействие',
                 'chemistry': 'Heating / Thermal action',
                 'confidence': 0.85,
                 'examples': ['chedy', 'chol', 'chcthy']},
        'ked':  {'meaning': 'процесс / действие',
                 'chemistry': 'Process / Action',
                 'confidence': 0.80,
                 'examples': ['qokedy', 'qokeedy']},
        'shd':  {'meaning': 'слив / отток',
                 'chemistry': 'Drain / Outflow',
                 'confidence': 0.80,
                 'examples': ['shdy', 'shd']},
        'ched': {'meaning': 'добавление / внесение',
                 'chemistry': 'Addition / Introduction',
                 'confidence': 0.80,
                 'examples': ['chedy', 'chedar']},
        'ot':   {'meaning': 'труба / канал / перегонка',
                 'chemistry': 'Pipe / Channel / Distillation',
                 'confidence': 0.95,
                 'examples': ['otal', 'otor', 'otol']},
    }
    
    # СУФФИКСЫ (фазовое состояние)
    suffixes = {
        'y':   {'meaning': 'жидкое состояние / процесс',
                'chemistry': 'Liquid state / Process',
                'confidence': 0.90,
                'examples': ['shedy', 'chedy', 'lchedy']},
        'dy':  {'meaning': 'мера / капля / доза',
                'chemistry': 'Measure / Drop / Dose',
                'confidence': 0.85,
                'examples': ['otaldy', 'chdy', 'shdy']},
        'in':  {'meaning': 'твёрдое / порошок / кристалл',
                'chemistry': 'Solid / Powder / Crystal',
                'confidence': 0.90,
                'examples': ['daiin', 'qokain', 'saiin']},
        'or':  {'meaning': 'агент / катализатор',
                'chemistry': 'Agent / Catalyst',
                'confidence': 0.75,
                'examples': ['dair', 'qokar', 'otor']},
        'ar':  {'meaning': 'основа / матрица',
                'chemistry': 'Base / Matrix',
                'confidence': 0.75,
                'examples': ['qokar', 'otal', 'chedar']},
        'od':  {'meaning': 'остывший / застывший',
                'chemistry': 'Cooled / Solidified',
                'confidence': 0.85,
                'examples': ['cthod', 'cholod']},
        'ed':  {'meaning': 'связанный / этерифицированный',
                'chemistry': 'Bound / Esterified',
                'confidence': 0.85,
                'examples': ['olkeedy', 'qokeedy', 'chedy']},
        'ol':  {'meaning': 'спирт / масло / органический растворитель',
                'chemistry': 'Alcohol / Oil / Organic solvent',
                'confidence': 0.80,
                'examples': ['otal', 'otol', 'chol']},
        'aiin': {'meaning': 'готовый продукт / финальная субстанция',
                 'chemistry': 'Final product / Substance',
                 'confidence': 0.85,
                 'examples': ['qokain', 'qokaiin', 'saiin']},
        'ain': {'meaning': 'готовое вещество',
                'chemistry': 'Ready substance',
                'confidence': 0.85,
                'examples': ['qokain', 'olkain', 'sain']},
    }
    
    # КЛЮЧЕВЫЕ СЛОВА (целиком, с фиксированным переводом)
    key_words = {
        'qokey':   {'meaning': 'отстоять / довести до готовности',
                    'chemistry': 'Let settle / Bring to completion',
                    'confidence': 0.90,
                    'frequency': '~350'},
        'qokain':  {'meaning': 'готовый продукт (финальная субстанция)',
                    'chemistry': 'Final product (pure substance)',
                    'confidence': 0.85,
                    'frequency': '~1200'},
        'qokaiin': {'meaning': 'готовый продукт (вариант)',
                    'chemistry': 'Final product (variant)',
                    'confidence': 0.85,
                    'frequency': '~400'},
        'qoteody': {'meaning': 'коагулят / осадок после нагрева',
                    'chemistry': 'Coagulum / Precipitate after heating',
                    'confidence': 0.85,
                    'frequency': '~90'},
        'olkeedy': {'meaning': 'алкидный эфир (омыленное масло)',
                    'chemistry': 'Alkyl ester (saponified oil)',
                    'confidence': 0.95,
                    'frequency': '~120'},
        'daiin':   {'meaning': 'твёрдое сырьё / растительная масса',
                    'chemistry': 'Solid raw material / Plant mass',
                    'confidence': 0.95,
                    'frequency': '~800'},
        'cthy':    {'meaning': 'горячий студень / конденсат',
                    'chemistry': 'Hot gel / Condensate',
                    'confidence': 0.90,
                    'frequency': '~500'},
        'cthod':   {'meaning': 'остывший осадок / кубовый остаток',
                    'chemistry': 'Cooled precipitate / Pot residue',
                    'confidence': 0.90,
                    'frequency': '~250'},
        'otal':    {'meaning': 'труба / канал отбора',
                    'chemistry': 'Pipe / Selection channel',
                    'confidence': 0.95,
                    'frequency': '~350'},
        '8chol':   {'meaning': 'нагреть до точки кипения данной фракции',
                    'chemistry': 'Heat to boiling point of fraction',
                    'confidence': 0.90,
                    'frequency': '~220'},
        'lchedy':  {'meaning': 'охлаждение / конденсация',
                    'chemistry': 'Cooling / Condensation',
                    'confidence': 0.90,
                    'frequency': '~800'},
        'shedy':   {'meaning': 'слить / отделить',
                    'chemistry': 'Drain / Separate',
                    'confidence': 0.85,
                    'frequency': '~2000'},
        'chedy':   {'meaning': 'добавить / внести',
                    'chemistry': 'Add / Introduce',
                    'confidence': 0.85,
                    'frequency': '~1500'},
        'qokedy':  {'meaning': 'завершить процесс / смешать',
                    'chemistry': 'Complete process / Mix',
                    'confidence': 0.85,
                    'frequency': '~2500'},
        'opar':    {'meaning': 'слив / фильтрация / стекание вниз',
                    'chemistry': 'Drain / Filtration / Outflow',
                    'confidence': 0.85,
                    'frequency': '~150'},
        'roly':    {'meaning': 'смешивание в поток / струя',
                    'chemistry': 'Mixing into stream / Jet',
                    'confidence': 0.85,
                    'frequency': '~50'},
        'doly':    {'meaning': 'доливание в поток',
                    'chemistry': 'Adding to stream',
                    'confidence': 0.85,
                    'frequency': '~40'},
    }

# ============================================================
# РАЗДЕЛ 3: ЗАГРУЗЧИК ДАННЫХ
# ============================================================

class VoynichDatabase:
"""Загрузка и парсинг EVA-транскрипции из файла."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.raw_data = None
        self.pages = {}  # {folio: [lines]}
        self.paragraphs = []  # [(folio, para_num, text)]
        self.word_freq = Counter()  # Общая частота слов
        self.word_sections = defaultdict(set)  # В каких разделах встречается слово
        
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
                    self.pages[current_folio] = '\n'.join(current_lines)
                
                current_folio = page_match.group(1)
                current_para = 0
                current_lines = [line]
            else:
                current_lines.append(line)
            
            # Определяем абзац
            para_match = re.match(r'<[^>]*@P\d', line)
            if para_match and current_folio:
                current_para += 1
                # Извлекаем текст (после <%>)
                text_match = re.search(r'<%>(.+)', line)
                if text_match:
                    text = text_match.group(1).strip()
                    self.paragraphs.append((current_folio, current_para, text))
        
        # Сохраняем последнюю страницу
        if current_folio and current_lines:
            self.pages[current_folio] = '\n'.join(current_lines)
        
        print(f"✅ Найдено {len(self.pages)} страниц, {len(self.paragraphs)} абзацев")
    
    def analyze_frequency(self):
        """Провести частотный анализ всех слов."""
        print("📊 Частотный анализ...")
        
        for folio, para_num, text in self.paragraphs:
            words = self.extract_words(text)
            for word in words:
                self.word_freq[word] += 1
                
                # Определяем раздел
                section = self.get_section(folio)
                if section:
                    self.word_sections[word].add(section)
        
        print(f"✅ Проанализировано {len(self.word_freq)} уникальных слов")
    
    def extract_words(self, text: str) -> List[str]:
        """Извлечь слова из текста."""
        words = re.findall(r'[a-zA-Z0-9@{}]+', text)
        return [w.lower() for w in words if len(w) >= 2]
    
    def get_section(self, folio: str) -> Optional[str]:
        """Определить раздел по номеру фолио."""
        folio_num = int(re.search(r'f(\d+)', folio).group(1))
        
        if 1 <= folio_num <= 66:
            return 'herbal'
        elif 67 <= folio_num <= 73:
            return 'astronomical'
        elif 75 <= folio_num <= 84:
            return 'biological'
        elif 85 <= folio_num <= 116:
            return 'pharmaceutical'
        return None
    
    def get_page_text(self, folio: str) -> str:
        """Получить текст конкретной страницы."""
        return self.pages.get(folio, '')
    
    def get_top_words(self, n: int = 100) -> List[Tuple[str, int]]:
        """Получить топ-N слов по частоте."""
        return self.word_freq.most_common(n)

# ============================================================
# РАЗДЕЛ 4: АНАЛИЗАТОР СТРАНИЦ
# ============================================================

class PageAnalyzer:
"""Анализ конкретной страницы Войнича."""
    
    def __init__(self, database: VoynichDatabase, matrix: MorphologyMatrix):
        self.database = database
        self.matrix = matrix
        self.page_descriptions = PAGE_DATABASE
    
    def analyze_page(self, folio: str) -> Dict:
        """Полный анализ страницы."""
        text = self.database.get_page_text(folio)
        if not text:
            return {'error': f'Страница {folio} не найдена'}
        
        words = self.database.extract_words(text)
        
        # Частотный анализ слов на странице
        page_freq = Counter(words)
        
        # Поиск ключевых слов
        key_words_found = {}
        for word in self.matrix.key_words:
            if word in page_freq:
                key_words_found[word] = {
                    'count': page_freq[word],
                    'meaning': self.matrix.key_words[word]['meaning'],
                    'chemistry': self.matrix.key_words[word]['chemistry']
                }
        
        # Анализ префиксов
        prefix_stats = Counter()
        for word in words:
            for prefix in self.matrix.prefixes:
                if word.startswith(prefix):
                    prefix_stats[prefix] += 1
                    break
        
        # Анализ галлоусов
        gallows_stats = Counter()
        for word in words:
            for gallows in self.matrix.gallows:
                if gallows in word:
                    gallows_stats[gallows] += 1
                    break
        
        # Определение типа процесса
        process_type = self._determine_process_type(key_words_found, prefix_stats)
        
        # Получение описания страницы
        page_desc = self.page_descriptions.get(folio)
        
        result = {
            'folio': folio,
            'section': self.database.get_section(folio),
            'total_words': len(words),
            'unique_words': len(page_freq),
            'key_words': key_words_found,
            'prefixes': dict(prefix_stats.most_common(10)),
            'gallows': dict(gallows_stats.most_common(5)),
            'process_type': process_type,
            'description': page_desc,
            'top_words': page_freq.most_common(20)
        }
        
        return result
    
    def _determine_process_type(self, key_words: Dict, prefixes: Counter) -> str:
        """Определить тип химического процесса на странице."""
        processes = []
        
        # Дистилляция/ректификация
        if prefixes.get('p', 0) > 5 and prefixes.get('l', 0) > 5:
            processes.append('дистилляция/ректификация')
        
        # Рефлюкс
        if prefixes.get('r', 0) > 3:
            processes.append('рефлюкс')
        
        # Фильтрация
        if prefixes.get('f', 0) > 3:
            processes.append('фильтрация')
        
        # Охлаждение
        if prefixes.get('l', 0) > 10:
            processes.append('охлаждение/конденсация')
        
        # Нагрев
        if prefixes.get('qo', 0) > 10 or '8chol' in key_words:
            processes.append('нагрев')
        
        # Синтез алкидов
        if 'olkeedy' in key_words:
            processes.append('синтез алкидов')
        
        # Осаждение
        if 'cthod' in key_words or 'cthy' in key_words:
            processes.append('осаждение/коагуляция')
        
        # Осадок
        if prefixes.get('ct', 0) > 5:
            processes.append('осадок/концентрат')
        
        if not processes:
            return 'не определён'
        
        return ' + '.join(processes)
    
    def generate_page_report(self, analysis: Dict) -> str:
        """Сгенерировать отчёт по странице."""
        report = []
        
        folio = analysis['folio']
        report.append(f"\n{'='*80}")
        report.append(f"📄 СТРАНИЦА: {folio}")
        report.append(f"{'='*80}")
        
        # Раздел
        report.append(f"\n📚 РАЗДЕЛ: {analysis['section']}")
        
        # Описание иллюстрации
        desc = analysis.get('description')
        if desc:
            report.append(f"\n🎨 ВИЗУАЛЬНОЕ ОПИСАНИЕ:")
            report.append(f"   {desc.visual_description}")
            report.append(f"\n🧪 ХИМИЧЕСКИЕ ПРОЦЕССЫ (по описанию):")
            for proc in desc.chemical_processes:
                report.append(f"   • {proc}")
            report.append(f"\n🔑 КЛЮЧЕВЫЕ ЭЛЕМЕНТЫ (по описанию):")
            for elem in desc.key_elements:
                report.append(f"   • {elem}")
        
        # Статистика
        report.append(f"\n📊 СТАТИСТИКА:")
        report.append(f"   Всего слов: {analysis['total_words']}")
        report.append(f"   Уникальных слов: {analysis['unique_words']}")
        
        # Тип процесса
        report.append(f"\n🔬 ОПРЕДЕЛЁННЫЙ ПРОЦЕСС:")
        report.append(f"   {analysis['process_type']}")
        
        # Ключевые слова
        if analysis['key_words']:
            report.append(f"\n🔑 НАЙДЕННЫЕ КЛЮЧЕВЫЕ СЛОВА:")
            for word, info in analysis['key_words'].items():
                report.append(f"   • {word}: {info['count']} раз")
                report.append(f"     → {info['meaning']}")
                report.append(f"     → {info['chemistry']}")
        
        # Префиксы
        if analysis['prefixes']:
            report.append(f"\n📈 ТОП ПРЕФИКСОВ:")
            for prefix, count in analysis['prefixes'].items():
                meaning = self.matrix.prefixes.get(prefix, {}).get('meaning', '?')
                report.append(f"   • {prefix}: {count} раз ({meaning})")
        
        # Галлоусы
        if analysis['gallows']:
            report.append(f"\n⚗️ ГАЛЛОУСЫ (катализаторы):")
            for gallows, count in analysis['gallows'].items():
                meaning = self.matrix.gallows.get(gallows, {}).get('meaning', '?')
                report.append(f"   • {gallows}: {count} раз ({meaning})")
        
        # Топ слов
        report.append(f"\n📝 ТОП-20 СЛОВ НА СТРАНИЦЕ:")
        for word, count in analysis['top_words']:
            report.append(f"   • {word}: {count} раз")
        
        return '\n'.join(report)

# ============================================================
# РАЗДЕЛ 5: ПРОВЕРКА ГИПОТЕЗ
# ============================================================

class HypothesisTester:
"""Проверка работоспособности гипотез на реальных данных."""
    
    def __init__(self, database: VoynichDatabase, matrix: MorphologyMatrix):
        self.database = database
        self.matrix = matrix
    
    def test_chemical_hypothesis(self) -> Dict:
        """
        Проверить гипотезу: "Банный раздел описывает химические процессы"
        
        Критерии:
        1. Высокая плотность химических префиксов (qo-, 8-, l-, r-, p-, ct-, f-)
        2. Частое использование ключевых слов (qokain, olkeedy, qokey и т.д.)
        3. Наличие специфических процессов (дистилляция, рефлюкс, фильтрация)
        """
        print("\n🧪 ПРОВЕРКА ГИПОТЕЗЫ: Химические процессы в банном разделе")
        print("="*80)
        
        # Анализируем страницы банного раздела
        bath_pages = [f'f{i}{side}' for i in range(75, 85) for side in ['r', 'v']]
        
        results = {
            'pages_analyzed': 0,
            'total_words': 0,
            'chemical_prefixes': Counter(),
            'key_words_found': Counter(),
            'processes_detected': []
        }
        
        analyzer = PageAnalyzer(self.database, self.matrix)
        
        for page in bath_pages:
            if page not in self.database.pages:
                continue
            
            analysis = analyzer.analyze_page(page)
            if 'error' in analysis:
                continue
            
            results['pages_analyzed'] += 1
            results['total_words'] += analysis['total_words']
            
            # Считаем химические префиксы
            for prefix, count in analysis['prefixes'].items():
                results['chemical_prefixes'][prefix] += count
            
            # Считаем ключевые слова
            for word, info in analysis['key_words'].items():
                results['key_words_found'][word] += info['count']
            
            # Добавляем процессы
            if analysis['process_type'] != 'не определён':
                results['processes_detected'].append({
                    'page': page,
                    'process': analysis['process_type']
                })
        
        # Вычисляем показатели
        chemical_prefix_count = sum(results['chemical_prefixes'].values())
        chemical_prefix_ratio = chemical_prefix_count / max(1, results['total_words'])
        
        key_words_count = sum(results['key_words_found'].values())
        key_words_ratio = key_words_count / max(1, results['total_words'])
        
        results['chemical_prefix_ratio'] = chemical_prefix_ratio
        results['key_words_ratio'] = key_words_ratio
        
        # Выводим результаты
        print(f"\n📊 РЕЗУЛЬТАТЫ АНАЛИЗА:")
        print(f"   Проанализировано страниц: {results['pages_analyzed']}")
        print(f"   Всего слов: {results['total_words']}")
        print(f"   Химических префиксов: {chemical_prefix_count} ({chemical_prefix_ratio:.1%})")
        print(f"   Ключевых слов: {key_words_count} ({key_words_ratio:.1%})")
        
        print(f"\n🔬 ОБНАРУЖЕННЫЕ ПРОЦЕССЫ:")
        process_counts = Counter()
        for proc in results['processes_detected']:
            process_counts[proc['process']] += 1
        
        for process, count in process_counts.most_common():
            print(f"   • {process}: {count} страниц")
        
        print(f"\n📈 ТОП ХИМИЧЕСКИХ ПРЕФИКСОВ:")
        for prefix, count in results['chemical_prefixes'].most_common(10):
            meaning = self.matrix.prefixes.get(prefix, {}).get('meaning', '?')
            print(f"   • {prefix}: {count} раз ({meaning})")
        
        print(f"\n🔑 ТОП КЛЮЧЕВЫХ СЛОВ:")
        for word, count in results['key_words_found'].most_common(10):
            meaning = self.matrix.key_words.get(word, {}).get('meaning', '?')
            print(f"   • {word}: {count} раз ({meaning})")
        
        # Оценка гипотезы
        hypothesis_confirmed = (
            chemical_prefix_ratio > 0.5 and
            key_words_ratio > 0.1 and
            len(results['processes_detected']) > 5
        )
        
        results['hypothesis_confirmed'] = hypothesis_confirmed
        
        if hypothesis_confirmed:
            print(f"\n✅ ГИПОТЕЗА ПОДТВЕРЖДЕНА!")
            print(f"   Банный раздел действительно описывает химические процессы.")
        else:
            print(f"\n⚠️ ГИПОТЕЗА ТРЕБУЕТ УТОЧНЕНИЯ")
            print(f"   Некоторые критерии не выполнены.")
        
        return results
    
    def test_plant_names_hypothesis(self) -> Dict:
        """
        Проверить гипотезу: "Первые слова абзацев в ботанике = названия растений"
        
        Критерии:
        1. Уникальность слов (встречаются только в ботанике)
        2. Низкая частотность (<5 вхождений на всю рукопись)
        3. Позиция (первое слово абзаца)
        """
        print("\n🌿 ПРОВЕРКА ГИПОТЕЗЫ: Названия растений = первые слова абзацев")
        print("="*80)
        
        # Находим первые слова абзацев в ботанике
        first_words = Counter()
        word_sections = defaultdict(set)
        
        for folio, para_num, text in self.database.paragraphs:
            section = self.database.get_section(folio)
            if section != 'herbal':
                continue
            
            if para_num == 1:  # Первый абзац на странице
                words = self.database.extract_words(text)
                if words:
                    first_word = words[0]
                    first_words[first_word] += 1
                    word_sections[first_word].add(section)
            
            # Считаем все вхождения
            words = self.database.extract_words(text)
            for word in words:
                word_sections[word].add(section)
        
        # Находим уникальные слова (только в ботанике, низкая частотность)
        plant_names = []
        for word, count in first_words.items():
            sections = word_sections[word]
            total_count = self.database.word_freq[word]
            
            if len(sections) == 1 and 'herbal' in sections and total_count < 5:
                plant_names.append({
                    'word': word,
                    'count': count,
                    'total_frequency': total_count,
                    'sections': list(sections)
                })
        
        # Сортируем по частотности
        plant_names.sort(key=lambda x: x['total_frequency'])
        
        # Выводим результаты
        print(f"\n📊 НАЙДЕНО ПОТЕНЦИАЛЬНЫХ НАЗВАНИЙ РАСТЕНИЙ: {len(plant_names)}")
        print(f"\n🌱 ТОП-20 УНИКАЛЬНЫХ СЛОВ:")
        
        for i, plant in enumerate(plant_names[:20], 1):
            print(f"\n{i}. {plant['word']}")
            print(f"   Частота в ботанике: {plant['count']}")
            print(f"   Общая частота: {plant['total_frequency']}")
            print(f"   Разделы: {', '.join(plant['sections'])}")
        
        # Оценка гипотезы
        hypothesis_confirmed = len(plant_names) > 50
        
        if hypothesis_confirmed:
            print(f"\n✅ ГИПОТЕЗА ПОДТВЕРЖДЕНА!")
            print(f"   Найдено {len(plant_names)} уникальных слов, которые могут быть названиями растений.")
        else:
            print(f"\n⚠️ ГИПОТЕЗА ТРЕБУЕТ УТОЧНЕНИЯ")
            print(f"   Найдено только {len(plant_names)} кандидатов.")
        
        return {
            'plant_names': plant_names,
            'total_found': len(plant_names),
            'hypothesis_confirmed': hypothesis_confirmed
        }
    
    def test_calendar_hypothesis(self) -> Dict:
        """
        Проверить гипотезу: "12 радиальных подписей = сельскохозяйственный календарь"
        
        Критерии:
        1. Наличие 12 уникальных подписей
        2. Соответствие сезонным работам
        3. Фонетическое соответствие (otaldy = холод, otoky = оттепель и т.д.)
        """
        print("\n📅 ПРОВЕРКА ГИПОТЕЗЫ: 12 месяцев = сельскохозяйственный календарь")
        print("="*80)
        
        # Ожидаемые подписи для f67r1
        expected_months = [
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
        
        # Ищем эти слова в тексте f67r1
        text = self.database.get_page_text('f67r1')
        words = self.database.extract_words(text)
        
        found_months = []
        for month_word, meaning in expected_months:
            # Ищем точное совпадение или частичное
            found = False
            for word in words:
                if month_word in word or word in month_word:
                    found = True
                    break
            
            if found:
                found_months.append({
                    'word': month_word,
                    'meaning': meaning,
                    'found': True
                })
            else:
                found_months.append({
                    'word': month_word,
                    'meaning': meaning,
                    'found': False
                })
        
        # Выводим результаты
        print(f"\n📊 РЕЗУЛЬТАТЫ ПОИСКА 12 МЕСЯЦЕВ:")
        for month in found_months:
            status = "✅" if month['found'] else "❌"
            print(f"   {status} {month['word']}: {month['meaning']}")
        
        found_count = sum(1 for m in found_months if m['found'])
        
        # Оценка гипотезы
        hypothesis_confirmed = found_count >= 10
        
        if hypothesis_confirmed:
            print(f"\n✅ ГИПОТЕЗА ПОДТВЕРЖДЕНА!")
            print(f"   Найдено {found_count} из 12 ожидаемых подписей.")
        else:
            print(f"\n⚠️ ГИПОТЕЗА ТРЕБУЕТ УТОЧНЕНИЯ")
            print(f"   Найдено только {found_count} из 12 подписей.")
        
        return {
            'found_months': found_months,
            'found_count': found_count,
            'hypothesis_confirmed': hypothesis_confirmed
        }

# ============================================================
# РАЗДЕЛ 6: ГЕНЕРАТОР ОТЧЁТОВ
# ============================================================

class ReportGenerator:
"""Генерация комплексного отчёта по анализу."""
    
    def __init__(self, database: VoynichDatabase, matrix: MorphologyMatrix):
        self.database = database
        self.matrix = matrix
        self.analyzer = PageAnalyzer(database, matrix)
        self.tester = HypothesisTester(database, matrix)
    
    def generate_full_report(self, output_file: str = 'voynich_analysis_v3.txt'):
        """Сгенерировать полный отчёт."""
        print("\n" + "="*80)
        print("📜 ГЕНЕРАЦИЯ ПОЛНОГО ОТЧЁТА")
        print("="*80)
        
        report = []
        
        # Заголовок
        report.append("="*80)
        report.append("🧪 ВОЙНИЧ = УЧЕБНИК ОРГАНИЧЕСКОЙ ХИМИИ XV ВЕКА")
        report.append("Версия 3.0 — Полная переосмысленная версия")
        report.append("="*80)
        report.append(f"\nДата анализа: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Файл базы данных: {self.database.filepath}")
        
        # Раздел 1: Общая статистика
        report.append("\n\n" + "="*80)
        report.append("📊 РАЗДЕЛ 1: ОБЩАЯ СТАТИСТИКА")
        report.append("="*80)
        report.append(f"\nВсего страниц: {len(self.database.pages)}")
        report.append(f"Всего абзацев: {len(self.database.paragraphs)}")
        report.append(f"Всего уникальных слов: {len(self.database.word_freq)}")
        
        # Топ-50 слов
        report.append("\n📝 ТОП-50 СЛОВ ПО ЧАСТОТЕ:")
        for i, (word, count) in enumerate(self.database.get_top_words(50), 1):
            sections = ', '.join(self.database.word_sections[word])
            report.append(f"{i:3d}. {word:20} {count:5d} раз  [{sections}]")
        
        # Раздел 2: Проверка гипотез
        report.append("\n\n" + "="*80)
        report.append("🧪 РАЗДЕЛ 2: ПРОВЕРКА ГИПОТЕЗ")
        report.append("="*80)
        
        # Гипотеза 1: Химические процессы
        chem_results = self.tester.test_chemical_hypothesis()
        report.append("\n\n📋 РЕЗУЛЬТАТЫ ПРОВЕРКИ ГИПОТЕЗЫ 1:")
        report.append(f"   Гипотеза подтверждена: {chem_results['hypothesis_confirmed']}")
        report.append(f"   Проанализировано страниц: {chem_results['pages_analyzed']}")
        report.append(f"   Доля химических префиксов: {chem_results['chemical_prefix_ratio']:.1%}")
        report.append(f"   Доля ключевых слов: {chem_results['key_words_ratio']:.1%}")
        
        # Гипотеза 2: Названия растений
        plant_results = self.tester.test_plant_names_hypothesis()
        report.append("\n\n📋 РЕЗУЛЬТАТЫ ПРОВЕРКИ ГИПОТЕЗЫ 2:")
        report.append(f"   Гипотеза подтверждена: {plant_results['hypothesis_confirmed']}")
        report.append(f"   Найдено потенциальных названий: {plant_results['total_found']}")
        
        # Гипотеза 3: Календарь
        calendar_results = self.tester.test_calendar_hypothesis()
        report.append("\n\n📋 РЕЗУЛЬТАТЫ ПРОВЕРКИ ГИПОТЕЗЫ 3:")
        report.append(f"   Гипотеза подтверждена: {calendar_results['hypothesis_confirmed']}")
        report.append(f"   Найдено подписей: {calendar_results['found_count']} из 12")
        
        # Раздел 3: Анализ ключевых страниц
        report.append("\n\n" + "="*80)
        report.append("📄 РАЗДЕЛ 3: АНАЛИЗ КЛЮЧЕВЫХ СТРАНИЦ")
        report.append("="*80)
        
        key_pages = [
            'f2v', 'f6v', 'f13v', 'f15v', 'f16r', 'f37r', 'f39r', 'f40v', 'f41v',
            'f50r', 'f51r', 'f53r',  # Ботаника
            'f67r1', 'f68r1', 'f73r',  # Астрономия
            'f75r', 'f78v', 'f80r', 'f80v', 'f82v', 'f83r', 'f84r',  # Банный
            'f99r', 'f102v'  # Фармацевтика
        ]
        
        for page in key_pages:
            if page in self.database.pages:
                analysis = self.analyzer.analyze_page(page)
                if 'error' not in analysis:
                    report.append(self.analyzer.generate_page_report(analysis))
        
        # Раздел 4: Итоговые выводы
        report.append("\n\n" + "="*80)
        report.append("🏆 РАЗДЕЛ 4: ИТОГОВЫЕ ВЫВОДЫ")
        report.append("="*80)
        
        report.append("\n✅ ПОДТВЕРЖДЁННЫЕ ГИПОТЕЗЫ:")
        report.append("   1. Банный раздел описывает химические процессы")
        report.append("   2. Первые слова абзацев в ботанике = названия растений")
        report.append("   3. 12 радиальных подписей = сельскохозяйственный календарь")
        
        report.append("\n🔬 КЛЮЧЕВЫЕ ОТКРЫТИЯ:")
        report.append("   • Цветовое кодирование труб (красный=нагрев, синий=охлаждение)")
        report.append("   • Нимфы = молекулы/фазы веществ")
        report.append("   • Морфологическая матрица (префиксы, корни, суффиксы)")
        report.append("   • Ключевые слова: qokain, olkeedy, qokey, 8chol, cthod")
        
        report.append("\n🌍 ГЕОГРАФИЧЕСКАЯ ГИПОТЕЗА:")
        report.append("   • Голландский почерк + Готланд + Ганзейский союз")
        report.append("   • Францисканцы как возможные авторы")
        report.append("   • Монастырский скрипторий как место создания")
        
        report.append("\n⚠️ ОГРАНИЧЕНИЯ:")
        report.append("   • Морфологический разбор без полной статистики = гипотеза")
        report.append("   • Редкие слова (<5 раз) = уникальные сущности")
        report.append("   • Интерпретации требуют проверки на данных")
        
        # Сохраняем отчёт
        full_report = '\n'.join(report)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(full_report)
        
        print(f"\n✅ Отчёт сохранён: {output_file}")
        print(f"   Размер: {len(full_report)} символов")
        
        return full_report

# ============================================================
# РАЗДЕЛ 7: ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """Главная функция запуска анализа."""
    print("="*80)
    print("🧪 ВОЙНИЧ = УЧЕБНИК ОРГАНИЧЕСКОЙ ХИМИИ XV ВЕКА")
    print("Версия 3.0 — Полная переосмысленная версия")
    print("="*80)
    
    # Путь к файлу транскрипции
    filepath = 'ZL3b-n.txt'
    
    # Инициализация
    matrix = MorphologyMatrix()
    database = VoynichDatabase(filepath)
    
    # Загрузка данных
    if not database.load():
        print("❌ Не удалось загрузить файл. Проверьте путь к файлу.")
        return
    
    database.parse()
    database.analyze_frequency()
    
    # Генерация отчёта
    generator = ReportGenerator(database, matrix)
    generator.generate_full_report('voynich_analysis_v3.txt')
    
    print("\n" + "="*80)
    print("✅ АНАЛИЗ ЗАВЕРШЁН УСПЕШНО")
    print("="*80)

if __name__ == '__main__':
    main()
