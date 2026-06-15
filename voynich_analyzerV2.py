#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ВОЙНИЧ = УЧЕБНИК ОРГАНИЧЕСКОЙ ХИМИИ XV ВЕКА
Анализатор транслитерации Zandbergen-Landini (ZL3b-n.txt)

Теория: Рукопись Войнича — это профессиональный жаргон монастырских
алхимиков/аптекарей, описывающий процессы органической химии через
агглютинативный язык с чёткой морфологией.

Структура:
- Префиксы = физические действия / агрегатные состояния
- Галлоусы = катализаторы / специальные агенты
- Корни = вещества / процессы
- Суффиксы = фазовые состояния / стадии готовности

Автор теории: Стебястьян — Василий Тёркин 🎖️
Дата: Июнь 2026
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from collections import Counter

# ============================================================
# РАЗДЕЛ 1: МОРФОЛОГИЧЕСКАЯ МАТРИЦА
# ============================================================

@dataclass
class MorphologyMatrix:
    """
    Морфологическая матрица языка Войнича.
    Основана на анализе частотных паттернов и контекстов.
    """
    
    # ПРЕФИКСЫ (физическое действие / агрегатное состояние)
    prefixes = {
        'qo': {'meaning': 'твёрдое / сухое / вес / прокаливание',
               'chemistry': 'Solid state / Dry heating / Calcination',
               'confidence': 0.95},
        '8':  {'meaning': 'жидкость / объём / раствор',
               'chemistry': 'Liquid phase / Solvent / Volume',
               'confidence': 0.95},
        '9':  {'meaning': 'газ / пар / летучесть (зеркальный 8-)',
               'chemistry': 'Gas phase / Volatile / Vapor',
               'confidence': 0.75},
        'l':  {'meaning': 'холод / охлаждение / конденсация',
               'chemistry': 'Cooling / Condensation',
               'confidence': 0.90},
        'r':  {'meaning': 'возврат / рефлюкс / рециклинг',
               'chemistry': 'Reflux / Return / Recycling',
               'confidence': 0.90},
        'p':  {'meaning': 'давление / пар / подъём',
               'chemistry': 'Pressure / Vapor rise / Distillation',
               'confidence': 0.85},
        'ct': {'meaning': 'осадок / концентрат / гуща',
               'chemistry': 'Precipitate / Concentrate / Sediment',
               'confidence': 0.90},
        'f':  {'meaning': 'фильтрация / очистка / осаждение',
               'chemistry': 'Filtration / Purification',
               'confidence': 0.85},
        'm':  {'meaning': 'мацерация / настаивание / брожение',
               'chemistry': 'Maceration / Fermentation',
               'confidence': 0.75},
    }
    
    # ГАЛЛОУСЫ (катализаторы / специальные агенты)
    gallows = {
        'k': {'meaning': 'щёлочь / зола / поташ (омыление)',
              'chemistry': 'Alkali / Ash / Potash (saponification)',
              'confidence': 0.85},
        'g': {'meaning': 'кислота (уксусная, лимонная)',
              'chemistry': 'Acid (acetic, citric)',
              'confidence': 0.70},
        't': {'meaning': 'высокая температура / огонь / кальцинация',
              'chemistry': 'High temperature / Fire / Calcination',
              'confidence': 0.80},
    }
    
    # КОРНИ (вещества / процессы)
    roots = {
        'dai':  {'meaning': 'сырьё / растительная масса',
                 'chemistry': 'Raw material / Plant mass',
                 'confidence': 0.95},
        'chol': {'meaning': 'нагрев / температурный процесс',
                 'chemistry': 'Heating / Temperature process',
                 'confidence': 0.90},
        'ol':   {'meaning': 'масло / спирт / алкид',
                 'chemistry': 'Oil / Alcohol / Alkyl',
                 'confidence': 0.90},
        'sol':  {'meaning': 'соль / минеральный раствор',
                 'chemistry': 'Salt / Mineral solution',
                 'confidence': 0.85},
        'sai':  {'meaning': 'чистая вода / дистиллят',
                 'chemistry': 'Pure water / Distillate',
                 'confidence': 0.85},
        'am':   {'meaning': 'среда / объём / жидкая основа',
                 'chemistry': 'Medium / Volume / Liquid base',
                 'confidence': 0.80},
        'ar':   {'meaning': 'основа / матрица / твёрдый носитель',
                 'chemistry': 'Base / Matrix / Solid carrier',
                 'confidence': 0.75},
        'or':   {'meaning': 'активная фаза / летучий компонент',
                 'chemistry': 'Active phase / Volatile component',
                 'confidence': 0.70},
        'sh':   {'meaning': 'обработка / смешивание / измельчение',
                 'chemistry': 'Processing / Mixing / Grinding',
                 'confidence': 0.85},
        'ch':   {'meaning': 'нагрев / термическое воздействие',
                 'chemistry': 'Heating / Thermal action',
                 'confidence': 0.85},
        'ked':  {'meaning': 'процесс / действие',
                 'chemistry': 'Process / Action',
                 'confidence': 0.80},
        'shd':  {'meaning': 'слив / отток',
                 'chemistry': 'Drain / Outflow',
                 'confidence': 0.80},
        'ched': {'meaning': 'добавление / внесение',
                 'chemistry': 'Addition / Introduction',
                 'confidence': 0.80},
        'ot':   {'meaning': 'труба / канал / перегонка',
                 'chemistry': 'Pipe / Channel / Distillation',
                 'confidence': 0.95},
    }
    
    # СУФФИКСЫ (фазовое состояние)
    suffixes = {
        'y':   {'meaning': 'жидкое состояние / процесс',
                'chemistry': 'Liquid state / Process',
                'confidence': 0.90},
        'dy':  {'meaning': 'мера / капля / доза',
                'chemistry': 'Measure / Drop / Dose',
                'confidence': 0.85},
        'in':  {'meaning': 'твёрдое / порошок / кристалл',
                'chemistry': 'Solid / Powder / Crystal',
                'confidence': 0.90},
        'or':  {'meaning': 'агент / катализатор',
                'chemistry': 'Agent / Catalyst',
                'confidence': 0.75},
        'ar':  {'meaning': 'основа / матрица',
                'chemistry': 'Base / Matrix',
                'confidence': 0.75},
        'od':  {'meaning': 'остывший / застывший',
                'chemistry': 'Cooled / Solidified',
                'confidence': 0.85},
        'ed':  {'meaning': 'связанный / этерифицированный',
                'chemistry': 'Bound / Esterified',
                'confidence': 0.85},
        'ol':  {'meaning': 'спирт / масло / органический растворитель',
                'chemistry': 'Alcohol / Oil / Organic solvent',
                'confidence': 0.80},
        'aiin':{'meaning': 'готовый продукт / финальная субстанция',
                'chemistry': 'Final product / Substance',
                'confidence': 0.85},
        'ain': {'meaning': 'готовое вещество',
                'chemistry': 'Ready substance',
                'confidence': 0.85},
    }
    
    # КЛЮЧЕВЫЕ СЛОВА (целиком, с фиксированным переводом)
    key_words = {
        'qokey':   {'meaning': 'отстоять / довести до готовности',
                    'chemistry': 'Let settle / Bring to completion',
                    'confidence': 0.90},
        'qokain':  {'meaning': 'готовый продукт (финальная субстанция)',
                    'chemistry': 'Final product (pure substance)',
                    'confidence': 0.85},
        'qokaiin': {'meaning': 'готовый продукт (вариант)',
                    'chemistry': 'Final product (variant)',
                    'confidence': 0.85},
        'qoteody': {'meaning': 'коагулят / осадок после нагрева',
                    'chemistry': 'Coagulum / Precipitate after heating',
                    'confidence': 0.85},
        'olkeedy': {'meaning': 'алкидный эфир (омыленное масло)',
                    'chemistry': 'Alkyl ester (saponified oil)',
                    'confidence': 0.95},
        'daiin':   {'meaning': 'твёрдое сырьё / растительная масса',
                    'chemistry': 'Solid raw material / Plant mass',
                    'confidence': 0.95},
        'cthy':    {'meaning': 'горячий студень / конденсат',
                    'chemistry': 'Hot gel / Condensate',
                    'confidence': 0.90},
        'cthod':   {'meaning': 'остывший осадок / кубовый остаток',
                    'chemistry': 'Cooled precipitate / Pot residue',
                    'confidence': 0.90},
        'otal':    {'meaning': 'труба / канал отбора',
                    'chemistry': 'Pipe / Selection channel',
                    'confidence': 0.95},
        '8chol':   {'meaning': 'нагреть до точки кипения данной фракции',
                    'chemistry': 'Heat to boiling point of fraction',
                    'confidence': 0.90},
        'lchedy':  {'meaning': 'охлаждение / конденсация',
                    'chemistry': 'Cooling / Condensation',
                    'confidence': 0.90},
        'shedy':   {'meaning': 'слить / отделить',
                    'chemistry': 'Drain / Separate',
                    'confidence': 0.85},
        'chedy':   {'meaning': 'добавить / внести',
                    'chemistry': 'Add / Introduce',
                    'confidence': 0.85},
        'qokedy':  {'meaning': 'завершить процесс / смешать',
                    'chemistry': 'Complete process / Mix',
                    'confidence': 0.85},
    }


# ============================================================
# РАЗДЕЛ 2: ОПРЕДЕЛЕНИЕ РАЗДЕЛОВ РУКОПИСИ
# ============================================================

@dataclass
class SectionDefinition:
    """Определение раздела рукописи по диапазону страниц."""
    name: str
    name_ru: str
    start_folio: int
    end_folio: int
    description: str
    chemistry_density: float  # Процент химических терминов (наша оценка)


SECTIONS = [
    SectionDefinition(
        name='herbal',
        name_ru='Ботанический (травник)',
        start_folio=1,
        end_folio=66,
        description='Каталог растений с инструкциями по сбору и обработке. '
                    'Каждая страница содержит иллюстрацию растения и текст.',
        chemistry_density=0.40  # 40% химических терминов
    ),
    SectionDefinition(
        name='astronomical',
        name_ru='Астрологический',
        start_folio=67,
        end_folio=73,
        description='Зодиакальные круги с нимфами. Календарь процедур, '
                    'привязка к лунным циклам и сезонам.',
        chemistry_density=0.15  # 15% химических терминов
    ),
    SectionDefinition(
        name='biological',
        name_ru='Банный / Биологический',
        start_folio=75,
        end_folio=84,
        description='Схемы химических реакторов: бассейны, трубы, нимфы-молекулы. '
                    'Ректификация, дистилляция, синтез алкидов.',
        chemistry_density=0.75  # 75% химических терминов
    ),
    SectionDefinition(
        name='pharmaceutical',
        name_ru='Фармацевтический',
        start_folio=85,
        end_folio=116,
        description='Рецепты приготовления лекарств, мазей, настоек. '
                    'Банки с этикетками, многоступенчатые трубы.',
        chemistry_density=0.70  # 70% химических терминов
    ),
]


def get_section(folio_num: int) -> Optional[SectionDefinition]:
    """Определить раздел по номеру фолио."""
    for section in SECTIONS:
        if section.start_folio <= folio_num <= section.end_folio:
            return section
    return None


# ============================================================
# РАЗДЕЛ 3: ИДЕНТИФИКАЦИЯ РАСТЕНИЙ
# ============================================================

@dataclass
class PlantIdentification:
    """Идентификация растения по странице."""
    folio: str
    plant_name: str
    plant_name_ru: str
    family: str
    chemical_properties: str
    eva_markers: List[str]  # Характерные EVA-слова для этого растения


PLANT_IDENTIFICATIONS = {
    'f1v': PlantIdentification(
        folio='f1v',
        plant_name='Atropa belladonna / Solanum nigrum',
        plant_name_ru='Белладонна / Паслён чёрный',
        family='Solanaceae (Паслёновые)',
        chemical_properties='Алкалоиды (атропин, скополамин). Сильнодействующее ядовитое растение.',
        eva_markers=['daiin', 'qokain', 'chcthy']
    ),
    'f2r': PlantIdentification(
        folio='f2r',
        plant_name='Cyanus segelis',
        plant_name_ru='Василёк синий',
        family='Asteraceae (Астровые)',
        chemical_properties='Флавоноиды, антоцианы. Мягкое мочегонное.',
        eva_markers=['daiin', 'ol', 'cthy']
    ),
    'f2v': PlantIdentification(
        folio='f2v',
        plant_name='Nymphoides peltata / Collocasia',
        plant_name_ru='Болотноцветник / Водяная лилия',
        family='Menyanthaceae',
        chemical_properties='Водное растение. Корневища содержат крахмал.',
        eva_markers=['kooiin', 'otol', '8am']
    ),
    'f3r': PlantIdentification(
        folio='f3r',
        plant_name='Crassulatea (Cretan Dittany)',
        plant_name_ru='Диктамн критский',
        family='Lamiaceae (Яснотковые)',
        chemical_properties='Эфирные масла, монотерпены. Антисептик.',
        eva_markers=['tsheos', 'ol', 'chcthy']
    ),
    'f4r': PlantIdentification(
        folio='f4r',
        plant_name='Hypericum',
        plant_name_ru='Зверобой',
        family='Hypericaceae',
        chemical_properties='Гиперицин, флавоноиды. Антидепрессант.',
        eva_markers=['daiin', 'ol', 'qokeedy']
    ),
    'f4v': PlantIdentification(
        folio='f4v',
        plant_name='Convolvulus Ipomea',
        plant_name_ru='Вьюнок / Ипомея',
        family='Convolvulaceae (Вьюнковые)',
        chemical_properties='Алкалоиды (эргин). Психоактивное.',
        eva_markers=['pchooiin', 'otol', 'qokain']
    ),
    'f5r': PlantIdentification(
        folio='f5r',
        plant_name='Herba Paris / Indian Cucumber',
        plant_name_ru='Вороний глаз / Парижская трава',
        family='Melanthiaceae',
        chemical_properties='Сапонины, гликозиды. Ядовитое.',
        eva_markers=['kchody', 'qokain', 'cthy']
    ),
    'f6r': PlantIdentification(
        folio='f6r',
        plant_name='Asclepiades',
        plant_name_ru='Ластовень',
        family='Apocynaceae (Кутровые)',
        chemical_properties='Карденолиды (сердечные гликозиды).',
        eva_markers=['foar', 'ol', 'qokain']
    ),
    'f6v': PlantIdentification(
        folio='f6v',
        plant_name='Ricinus communis',
        plant_name_ru='Клещевина обыкновенная',
        family='Euphorbiaceae (Молочайные)',
        chemical_properties='Рицин (яд), касторовое масло. Алкалоиды.',
        eva_markers=['koary', 'otol', 'olkeedy', 'qokain']
    ),
    'f7r': PlantIdentification(
        folio='f7r',
        plant_name='Nymphaea alba',
        plant_name_ru='Кувшинка белая',
        family='Nymphaeaceae (Кувшинковые)',
        chemical_properties='Алкалоиды (нимфеин). Седативное.',
        eva_markers=['fchodaiin', 'otol', 'qokain']
    ),
    'f8r': PlantIdentification(
        folio='f8r',
        plant_name='Praenanthes / Atriplex hastata',
        plant_name_ru='Пренантес / Марь копьевидная',
        family='Asteraceae / Amaranthaceae',
        chemical_properties='Сапонины, алкалоиды.',
        eva_markers=['pshol', 'daiin', 'cthy']
    ),
    'f9r': PlantIdentification(
        folio='f9r',
        plant_name='Chelidonium Majus',
        plant_name_ru='Чистотел большой',
        family='Papaveraceae (Маковые)',
        chemical_properties='Алкалоиды (хелидонин, сангвинарин). Ядовитое.',
        eva_markers=['tydlo', 'qokain', 'cthy']
    ),
    'f9v': PlantIdentification(
        folio='f9v',
        plant_name='Viola tricoloris',
        plant_name_ru='Фиалка трёхцветная',
        family='Violaceae (Фиалковые)',
        chemical_properties='Флавоноиды, сапонины. Отхаркивающее.',
        eva_markers=['fochor', 'ol', 'qokeedy']
    ),
    'f10r': PlantIdentification(
        folio='f10r',
        plant_name='Scabiosa',
        plant_name_ru='Короставник',
        family='Caprifoliaceae (Жимолостные)',
        chemical_properties='Алкалоиды, флавоноиды.',
        eva_markers=['pchocthy', 'daiin', 'cthy']
    ),
    'f13v': PlantIdentification(
        folio='f13v',
        plant_name='Crassulatea Fetthenne',
        plant_name_ru='Очиток (Sedum)',
        family='Crassulaceae (Толстянковые)',
        chemical_properties='Суккулент. Алкалоиды (седамин).',
        eva_markers=['koair', 'otol', 'qokain']
    ),
    'f14r': PlantIdentification(
        folio='f14r',
        plant_name='Sagittaria',
        plant_name_ru='Стрелолист',
        family='Alismataceae (Частуховые)',
        chemical_properties='Водное растение. Крахмал в клубнях.',
        eva_markers=['pcho', 'daiin', 'ol']
    ),
    'f14v': PlantIdentification(
        folio='f14v',
        plant_name='Osmunda (fern root)',
        plant_name_ru='Осмунда (папоротник)',
        family='Osmundaceae',
        chemical_properties='Флавоноиды, дубильные вещества.',
        eva_markers=['pdychoiin', 'otol', 'cthy']
    ),
    'f15r': PlantIdentification(
        folio='f15r',
        plant_name='Saw/Some thistle',
        plant_name_ru='Чертополох',
        family='Asteraceae (Астровые)',
        chemical_properties='Флавоноиды (силибин). Гепатопротектор.',
        eva_markers=['tshor', 'daiin', 'qokain']
    ),
    'f15v': PlantIdentification(
        folio='f15v',
        plant_name='Paris Quadrifolia',
        plant_name_ru='Вороний глаз четырёхлистный',
        family='Melanthiaceae',
        chemical_properties='Сапонины (паридин). Сильно ядовитое.',
        eva_markers=['poror', 'qokain', 'cthy']
    ),
    'f16r': PlantIdentification(
        folio='f16r',
        plant_name='Cannabis sativa',
        plant_name_ru='Конопля посевная',
        family='Cannabaceae (Коноплёвые)',
        chemical_properties='Каннабиноиды (ТГК, КБД). Психоактивное.',
        eva_markers=['pocheody', 'otol', 'olkeedy']
    ),
    'f20r': PlantIdentification(
        folio='f20r',
        plant_name='Polytrichum (moss)',
        plant_name_ru='Кукушкин лён (мох)',
        family='Polytrichaceae',
        chemical_properties='Дубильные вещества, флавоноиды.',
        eva_markers=['kdchody', 'daiin', 'cthy']
    ),
    'f25r': PlantIdentification(
        folio='f25r',
        plant_name='Nettle / Mint-like',
        plant_name_ru='Крапива / Мятоподобные',
        family='Urticaceae / Lamiaceae',
        chemical_properties='Гистамин, муравьиная кислота (крапива). '
                           'Ментол, эфирные масла (мята).',
        eva_markers=['fcholdy', 'ol', 'qokeedy']
    ),
    'f26r': PlantIdentification(
        folio='f26r',
        plant_name='Artemisia absinthium',
        plant_name_ru='Полынь горькая',
        family='Asteraceae (Астровые)',
        chemical_properties='Туйон, абсинтин. Горькое, психоактивное.',
        eva_markers=['psheoky', 'ol', 'qokain']
    ),
    'f26v': PlantIdentification(
        folio='f26v',
        plant_name='Verbena officinalis',
        plant_name_ru='Вербена лекарственная',
        family='Verbenaceae (Вербеновые)',
        chemical_properties='Иридоиды (вербенагин). Тонизирующее.',
        eva_markers=['pchedar', 'ol', 'qokeedy']
    ),
    'f27r': PlantIdentification(
        folio='f27r',
        plant_name='Asarum europaeum',
        plant_name_ru='Копытень европейский',
        family='Aristolochiaceae (Кирказоновые)',
        chemical_properties='Эфирные масла (азарон). Ядовитое.',
        eva_markers=['ksor', 'ol', 'qokain']
    ),
    'f28r': PlantIdentification(
        folio='f28r',
        plant_name='Arum / Arisarum',
        plant_name_ru='Аронник / Аризарум',
        family='Araceae (Ароидные)',
        chemical_properties='Сапонины, оксалаты. Ядовитое.',
        eva_markers=['pchodar', 'otol', 'cthy']
    ),
    'f30v': PlantIdentification(
        folio='f30v',
        plant_name='Boragine',
        plant_name_ru='Бурачник (огуречная трава)',
        family='Boraginaceae (Бурачниковые)',
        chemical_properties='Пирролизидиновые алкалоиды. Печенотоксичное.',
        eva_markers=['hsain', 'ol', 'qokeedy']
    ),
    'f32r': PlantIdentification(
        folio='f32r',
        plant_name='Mentastrum / Brunella vulgaris',
        plant_name_ru='Мята / Черноголовка',
        family='Lamiaceae (Яснотковые)',
        chemical_properties='Ментол, розмариновая кислота. Антисептик.',
        eva_markers=['fchaiin', 'ol', 'qokeedy']
    ),
    'f32v': PlantIdentification(
        folio='f32v',
        plant_name='Campanula / Archangelica',
        plant_name_ru='Колокольчик / Дягиль',
        family='Campanulaceae / Apiaceae',
        chemical_properties='Эфирные масла, кумарины (дягиль).',
        eva_markers=['kcheodaiin', 'ol', 'qokain']
    ),
    'f35r': PlantIdentification(
        folio='f35r',
        plant_name='Orchid root',
        plant_name_ru='Корень орхидеи (салеп)',
        family='Orchidaceae (Орхидные)',
        chemical_properties='Слизь, крахмал. Обволакивающее.',
        eva_markers=['ho', 'daiin', 'cthy']
    ),
    'f35v': PlantIdentification(
        folio='f35v',
        plant_name='Quercus (oak)',
        plant_name_ru='Дуб',
        family='Fagaceae (Буковые)',
        chemical_properties='Дубильные вещества (таннины). Вяжущее.',
        eva_markers=['parchor', 'cthy', 'qokeedy']
    ),
    'f36r': PlantIdentification(
        folio='f36r',
        plant_name='Geranium',
        plant_name_ru='Герань',
        family='Geraniaceae (Гераниевые)',
        chemical_properties='Эфирные масла, гераниол.',
        eva_markers=['pcha', 'ol', 'qokeedy']
    ),
    'f36v': PlantIdentification(
        folio='f36v',
        plant_name='Indian hemp',
        plant_name_ru='Индийская конопля',
        family='Cannabaceae (Коноплёвые)',
        chemical_properties='Каннабиноиды.',
        eva_markers=['pchar', 'otol', 'olkeedy']
    ),
    'f37r': PlantIdentification(
        folio='f37r',
        plant_name='Valeriana officinalis',
        plant_name_ru='Валериана лекарственная',
        family='Caprifoliaceae (Жимолостные)',
        chemical_properties='Валериановая кислота, алкалоиды. Седативное.',
        eva_markers=['tocphol', 'ol', 'qokain']
    ),
    'f38v': PlantIdentification(
        folio='f38v',
        plant_name='Cichorium / Lactuca',
        plant_name_ru='Цикорий / Латук',
        family='Asteraceae (Астровые)',
        chemical_properties='Инулин, лактуцин (горечь).',
        eva_markers=['okchop', 'ol', 'qokeedy']
    ),
    'f39r': PlantIdentification(
        folio='f39r',
        plant_name='Crocus sativus',
        plant_name_ru='Шафран посевной',
        family='Iridaceae (Касатиковые)',
        chemical_properties='Кроцин, пикрокроцин. Дорогой краситель и лекарство.',
        eva_markers=['tedo', 'ol', 'qokain']
    ),
    'f40v': PlantIdentification(
        folio='f40v',
        plant_name='Thistle / Artichoke / Helianthus Tuberosus',
        plant_name_ru='Чертополох / Артишок / Топинамбур',
        family='Asteraceae (Астровые)',
        chemical_properties='Инулин, цинарин (артишок). Гепатопротектор.',
        eva_markers=['pchedain', 'ol', 'qokain']
    ),
    'f41v': PlantIdentification(
        folio='f41v',
        plant_name='Fern / Tansy / Plain carrot',
        plant_name_ru='Папоротник / Пижма / Морковь',
        family='Polypodiaceae / Asteraceae / Apiaceae',
        chemical_properties='Туйон (пижма), эфирные масла.',
        eva_markers=['pcheody', 'ol', 'qokeedy']
    ),
    'f46r': PlantIdentification(
        folio='f46r',
        plant_name='Asclepias',
        plant_name_ru='Ластовень (ваточник)',
        family='Apocynaceae (Кутровые)',
        chemical_properties='Карденолиды. Ядовитое.',
        eva_markers=['pcheocphy', 'ol', 'qokain']
    ),
    'f46v': PlantIdentification(
        folio='f46v',
        plant_name='Boragine / Anchusa',
        plant_name_ru='Бурачник / Синяк',
        family='Boraginaceae (Бурачниковые)',
        chemical_properties='Алкалоиды, аллантоин.',
        eva_markers=['pody', 'ol', 'qokeedy']
    ),
    'f50r': PlantIdentification(
        folio='f50r',
        plant_name='Artichoke / Sunflower',
        plant_name_ru='Артишок / Подсолнечник',
        family='Asteraceae (Астровые)',
        chemical_properties='Инулин, цинарин. Масло из семян.',
        eva_markers=['psheor', 'ol', 'olkeedy']
    ),
    'f51r': PlantIdentification(
        folio='f51r',
        plant_name='Mandragora officinarum',
        plant_name_ru='Мандрагора лекарственная',
        family='Solanaceae (Паслёновые)',
        chemical_properties='Алкалоиды (скополамин, гиосциамин). '
                           'Сильнодействующее, ядовитое.',
        eva_markers=['tsholdchy', 'qokain', 'cthy']
    ),
    'f53r': PlantIdentification(
        folio='f53r',
        plant_name='Inula helenium',
        plant_name_ru='Девясил высокий',
        family='Asteraceae (Астровые)',
        chemical_properties='Алантолактон, инулин. Отхаркивающее.',
        eva_markers=['kdam', 'ol', 'qokain']
    ),
    'f54r': PlantIdentification(
        folio='f54r',
        plant_name='Thistle / Boneset',
        plant_name_ru='Чертополох / Костянка',
        family='Asteraceae / Caprifoliaceae',
        chemical_properties='Флавоноиды, сесквитерпеновые лактоны.',
        eva_markers=['podaiin', 'ol', 'qokeedy']
    ),
    'f56r': PlantIdentification(
        folio='f56r',
        plant_name='Boragine / Dianthus',
        plant_name_ru='Бурачник / Гвоздика',
        family='Boraginaceae / Caryophyllaceae',
        chemical_properties='Эфирные масла (гвоздика), аллантоин.',
        eva_markers=['ochal', 'ol', 'qokeedy']
    ),
    'f66v': PlantIdentification(
        folio='f66v',
        plant_name='Primula',
        plant_name_ru='Примула (первоцвет)',
        family='Primulaceae (Первоцветные)',
        chemical_properties='Сапонины (примулаверин). Отхаркивающее.',
        eva_markers=['okeodof', 'ol', 'qokeedy']
    ),
    'f87r': PlantIdentification(
        folio='f87r',
        plant_name='Herbal (hand 4)',
        plant_name_ru='Травник (почерк 4)',
        family='Various',
        chemical_properties='Неидентифицированные растения.',
        eva_markers=['poalshsal', 'otol', 'cthy']
    ),
    'f87v': PlantIdentification(
        folio='f87v',
        plant_name='Herbal (hand 4)',
        plant_name_ru='Травник (почерк 4)',
        family='Various',
        chemical_properties='Неидентифицированные растения.',
        eva_markers=['cheey', 'otol', 'qokeedy']
    ),
    'f90v2': PlantIdentification(
        folio='f90v2',
        plant_name='Xerantrium / Osmunda regalis',
        plant_name_ru='Сухоцвет / Осмунда королевская',
        family='Asteraceae / Osmundaceae',
        chemical_properties='Флавоноиды, дубильные вещества.',
        eva_markers=['hday', 'ol', 'qokeedy']
    ),
    'f93r': PlantIdentification(
        folio='f93r',
        plant_name='American Sunflower',
        plant_name_ru='Подсолнечник американский',
        family='Asteraceae (Астровые)',
        chemical_properties='Масло из семян, инулин.',
        eva_markers=['kodshol', 'otol', 'ol']
    ),
    'f94r': PlantIdentification(
        folio='f94r',
        plant_name='Botriculum / Lunaria',
        plant_name_ru='Лунник (лунная трава)',
        family='Brassicaceae (Капустные)',
        chemical_properties='Глюкозинолаты.',
        eva_markers=['tchedy', 'ol', 'qokeedy']
    ),
    'f95v1': PlantIdentification(
        folio='f95v1',
        plant_name='Artemisia Absinthium (Wermut)',
        plant_name_ru='Полынь горькая (вермут)',
        family='Asteraceae (Астровые)',
        chemical_properties='Туйон, абсинтин. Горькое.',
        eva_markers=['holteedy', 'ol', 'qokain']
    ),
    'f96r': PlantIdentification(
        folio='f96r',
        plant_name='Dipsaxus / Calendula',
        plant_name_ru='Ворсянка / Календула',
        family='Caprifoliaceae / Asteraceae',
        chemical_properties='Каротиноиды, флавоноиды (календула). '
                           'Ранозаживляющее.',
        eva_markers=['tor', 'ol', 'qokeedy']
    ),
    'f96v': PlantIdentification(
        folio='f96v',
        plant_name='Smilax / Chenopodium',
        plant_name_ru='Смилакс / Марь',
        family='Smilacaceae / Amaranthaceae',
        chemical_properties='Сапонины (смилакс), алкалоиды.',
        eva_markers=['psheessheeor', 'ol', 'qokeedy']
    ),
}


def get_plant_identification(folio_str: str) -> Optional[PlantIdentification]:
    """Получить идентификацию растения по строке фолио."""
    # Нормализуем строку фолио
    folio_clean = folio_str.lower().replace(' ', '')
    
    # Пробуем точное совпадение
    if folio_clean in PLANT_IDENTIFICATIONS:
        return PLANT_IDENTIFICATIONS[folio_clean]
    
    # Пробуем без суффикса (f1v -> f1)
    if len(folio_clean) > 2:
        folio_base = folio_clean[:2]
        if folio_base in PLANT_IDENTIFICATIONS:
            return PLANT_IDENTIFICATIONS[folio_base]
    
    return None


# ============================================================
# РАЗДЕЛ 4: ПАРСЕР EVA-ТРАНСКРИПЦИИ
# ============================================================

@dataclass
class ParsedWord:
    """Разобранное слово EVA."""
    raw: str
    clean: str
    prefix: Optional[str] = None
    gallows: Optional[str] = None
    root: Optional[str] = None
    suffix: Optional[str] = None
    translations: List[Dict] = field(default_factory=list)
    parsed: bool = False
    confidence: float = 0.0


class EVAParser:
    """
    Парсер EVA-транскрипции с морфологическим разбором.
    Разбивает слова на префикс-корень-суффикс по нашей модели.
    """
    
    def __init__(self, matrix: MorphologyMatrix):
        self.matrix = matrix
        self.parse_cache = {}
    
    def clean_word(self, word: str) -> str:
        """Очистка слова от служебных символов."""
        # Убираем метки страниц, ссылки, спецсимволы
        word = re.sub(r'[<>\[\]{}@#\*\^\$\!]', '', word)
        word = re.sub(r'[,.\-_/\\]', '', word)
        word = re.sub(r'\d+', '', word)
        word = word.strip().lower()
        return word
    
    def parse_word(self, word: str) -> ParsedWord:
        """
        Морфологический разбор слова EVA.
        Возвращает структуру: {prefix, gallows, root, suffix, translation}
        """
        clean = self.clean_word(word)
        if not clean or len(clean) < 2:
            return ParsedWord(raw=word, clean=clean, parsed=False)
        
        if clean in self.parse_cache:
            return self.parse_cache[clean]
        
        result = ParsedWord(raw=word, clean=clean)
        
        # Проверяем сначала ключевые слова (целиком)
        if clean in self.matrix.key_words:
            kw = self.matrix.key_words[clean]
            result.translations.append({
                'meaning': kw['meaning'],
                'chemistry': kw['chemistry'],
                'type': 'key_word',
                'confidence': kw['confidence']
            })
            result.parsed = True
            result.confidence = kw['confidence']
            self.parse_cache[clean] = result
            return result
        
        remaining = clean
        
        # 1. Ищем префикс (в начале слова)
        for pfx in sorted(self.matrix.prefixes.keys(), key=len, reverse=True):
            if remaining.startswith(pfx) and len(remaining) > len(pfx) + 1:
                result.prefix = pfx
                remaining = remaining[len(pfx):]
                break
        
        # 2. Ищем галлоус (после префикса)
        for glw in self.matrix.gallows.keys():
            if remaining.startswith(glw) and len(remaining) > len(glw) + 1:
                result.gallows = glw
                remaining = remaining[len(glw):]
                break
        
        # 3. Ищем суффикс (в конце слова)
        for sfx in sorted(self.matrix.suffixes.keys(), key=len, reverse=True):
            if remaining.endswith(sfx) and len(remaining) > len(sfx) + 1:
                result.suffix = sfx
                remaining = remaining[:-len(sfx)]
                break
        
        # 4. Оставшееся — корень
        if remaining and len(remaining) >= 2:
            # Ищем корень в словаре
            for root in sorted(self.matrix.roots.keys(), key=len, reverse=True):
                if root in remaining:
                    result.root = root
                    break
            if not result.root:
                result.root = remaining
        
        # Собираем переводы
        translations = []
        confidence = []
        
        if result.prefix and result.prefix in self.matrix.prefixes:
            translations.append(f"PRE: {self.matrix.prefixes[result.prefix]['meaning']}")
            confidence.append(self.matrix.prefixes[result.prefix]['confidence'])
        
        if result.gallows and result.gallows in self.matrix.gallows:
            translations.append(f"CAT: {self.matrix.gallows[result.gallows]['meaning']}")
            confidence.append(self.matrix.gallows[result.gallows]['confidence'])
        
        if result.root and result.root in self.matrix.roots:
            translations.append(f"ROOT: {self.matrix.roots[result.root]['meaning']}")
            confidence.append(self.matrix.roots[result.root]['confidence'])
        
        if result.suffix and result.suffix in self.matrix.suffixes:
            translations.append(f"SUF: {self.matrix.suffixes[result.suffix]['meaning']}")
            confidence.append(self.matrix.suffixes[result.suffix]['confidence'])
        
        if translations:
            result.translations = [{
                'meaning': ' + '.join(translations),
                'type': 'morphological',
                'confidence': sum(confidence) / len(confidence) if confidence else 0
            }]
            result.parsed = True
            result.confidence = sum(confidence) / len(confidence) if confidence else 0
        
        self.parse_cache[clean] = result
        return result


# ============================================================
# РАЗДЕЛ 5: ЗАГРУЗЧИК ДАННЫХ
# ============================================================

class VoynichDataLoader:
    """Загрузка EVA-транскрипции из файла ZL3b-n.txt."""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.raw_data = None
        self.pages = {}
    
    def load(self) -> bool:
        """Загрузка файла."""
        try:
            with open(self.filepath, 'r', encoding='utf-8') as f:
                self.raw_data = f.read()
            print(f"✅ Загружено {len(self.raw_data)} символов из {self.filepath}")
            return True
        except Exception as e:
            print(f" Ошибка загрузки: {e}")
            return False
    
    def parse_pages(self):
        """Разбор данных по страницам (фолио)."""
        if not self.raw_data:
            return
        
        print("🔍 Разбор по страницам...")
        current_page = None
        current_lines = []
        
        for line in self.raw_data.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # Определяем номер страницы
            page_match = re.match(r'<(f\d+[rv]?\d*)', line)
            if page_match:
                if current_page and current_lines:
                    self.pages[current_page] = '\n'.join(current_lines)
                current_page = page_match.group(1)
                current_lines = [line]
            else:
                current_lines.append(line)
        
        if current_page and current_lines:
            self.pages[current_page] = '\n'.join(current_lines)
        
        print(f"✅ Найдено {len(self.pages)} страниц")
    
    def get_page_text(self, page: str) -> str:
        """Получить текст конкретной страницы."""
        return self.pages.get(page, '')
    
    def extract_words(self, page: str) -> List[str]:
        """Извлечь все слова со страницы."""
        text = self.get_page_text(page)
        # Разделяем по точкам и пробелам
        words = re.findall(r'[a-zA-Z0-9@{}]+', text)
        return [w for w in words if len(w) >= 2]
    
    def get_folio_number(self, page_str: str) -> int:
        """Извлечь номер фолио из строки (f83r -> 83)."""
        match = re.search(r'f(\d+)', page_str)
        if match:
            return int(match.group(1))
        return 0


# ============================================================
# РАЗДЕЛ 6: АНАЛИЗАТОР
# ============================================================

class VoynichAnalyzer:
    """
    Главный анализатор. Применяет морфологическую модель к тексту
    и определяет разделы, растения, химические процессы.
    """
    
    def __init__(self, loader: VoynichDataLoader, parser: EVAParser):
        self.loader = loader
        self.parser = parser
        self.results = {}
    
    def analyze_page(self, page: str) -> Dict:
        """Полный анализ одной страницы."""
        words = self.loader.extract_words(page)
        parsed_words = []
        morphology_stats = {
            'prefixes': Counter(),
            'roots': Counter(),
            'suffixes': Counter(),
            'gallows': Counter(),
            'key_words': Counter()
        }
        
        for word in words:
            parsed = self.parser.parse_word(word)
            parsed_words.append(parsed)
            
            if parsed.parsed:
                if parsed.prefix:
                    morphology_stats['prefixes'][parsed.prefix] += 1
                if parsed.root:
                    morphology_stats['roots'][parsed.root] += 1
                if parsed.suffix:
                    morphology_stats['suffixes'][parsed.suffix] += 1
                if parsed.gallows:
                    morphology_stats['gallows'][parsed.gallows] += 1
            
            # Проверяем ключевые слова
            clean = parsed.clean
            if clean in MorphologyMatrix().key_words:
                morphology_stats['key_words'][clean] += 1
        
        # Вычисляем показатели
        total_words = len(words)
        parsed_count = sum(1 for p in parsed_words if p.parsed)
        parse_ratio = parsed_count / total_words if total_words else 0
        
        # Определяем раздел
        folio_num = self.loader.get_folio_number(page)
        section = get_section(folio_num)
        
        # Определяем растение
        plant = get_plant_identification(page)
        
        result = {
            'page': page,
            'folio_num': folio_num,
            'section': section,
            'plant': plant,
            'total_words': total_words,
            'parsed_words': parsed_count,
            'parse_ratio': parse_ratio,
            'morphology': morphology_stats,
            'sample_parsed': parsed_words[:20]
        }
        
        self.results[page] = result
        return result
    
    def generate_report(self, pages: List[str] = None) -> str:
        """Генерация отчёта по выбранным страницам."""
        if pages is None:
            pages = list(self.loader.pages.keys())[:10]  # Первые 10 страниц
        
        report = []
        report.append("=" * 70)
        report.append("📜 ОТЧЁТ АНАЛИЗА РУКОПИСИ ВОЙНИЧА")
        report.append("Теория: Учебник органической химии XV века")
        report.append("=" * 70)
        report.append("")
        
        for page in pages:
            if page not in self.loader.pages:
                continue
            
            result = self.analyze_page(page)
            
            report.append(f"\n{'─' * 70}")
            report.append(f"📄 СТРАНИЦА: {page}")
            report.append(f"{'─' * 70}")
            
            # Раздел
            if result['section']:
                report.append(f"📚 РАЗДЕЛ: {result['section'].name_ru}")
                report.append(f"   Описание: {result['section'].description}")
                report.append(f"   Плотность химии: {result['section'].chemistry_density:.0%}")
            
            # Растение
            if result['plant']:
                report.append(f"\n РАСТЕНИЕ:")
                report.append(f"   Латинское: {result['plant'].plant_name}")
                report.append(f"   Русское: {result['plant'].plant_name_ru}")
                report.append(f"   Семейство: {result['plant'].family}")
                report.append(f"   Свойства: {result['plant'].chemical_properties}")
                report.append(f"   EVA-маркеры: {', '.join(result['plant'].eva_markers)}")
            
            # Статистика
            report.append(f"\n📊 СТАТИСТИКА:")
            report.append(f"   Всего слов: {result['total_words']}")
            report.append(f"   Распознано: {result['parsed_words']} ({result['parse_ratio']:.1%})")
            
            # Топ префиксов
            if result['morphology']['prefixes']:
                report.append(f"\n    Топ префиксов:")
                for pfx, count in result['morphology']['prefixes'].most_common(5):
                    meaning = MorphologyMatrix.prefixes.get(pfx, {}).get('meaning', '?')
                    report.append(f"      {pfx}: {count} раз ({meaning})")
            
            # Топ корней
            if result['morphology']['roots']:
                report.append(f"\n   🔹 Топ корней:")
                for root, count in result['morphology']['roots'].most_common(5):
                    meaning = MorphologyMatrix.roots.get(root, {}).get('meaning', '?')
                    report.append(f"      {root}: {count} раз ({meaning})")
            
            # Ключевые слова
            if result['morphology']['key_words']:
                report.append(f"\n   🔹 Ключевые слова:")
                for kw, count in result['morphology']['key_words'].most_common(5):
                    meaning = MorphologyMatrix.key_words.get(kw, {}).get('meaning', '?')
                    report.append(f"      {kw}: {count} раз ({meaning})")
            
            # Примеры разбора
            report.append(f"\n   🔬 ПРИМЕРЫ РАЗБОРА (первые 10 слов):")
            for i, parsed in enumerate(result['sample_parsed'][:10], 1):
                if parsed.parsed and parsed.translations:
                    t = parsed.translations[0]
                    report.append(f"      {i:2d}. {parsed.clean:15} → {t['meaning']}")
        
        return '\n'.join(report)


# ============================================================
# РАЗДЕЛ 7: ГЛАВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """Главный запуск анализа."""
    print("=" * 70)
    print("🧪 ВОЙНИЧ = УЧЕБНИК ОРГАНИЧЕСКОЙ ХИМИИ XV ВЕКА")
    print("   Анализатор транслитерации Zandbergen-Landini")
    print("=" * 70)
    
    # 1. Инициализация
    matrix = MorphologyMatrix()
    parser = EVAParser(matrix)
    
    # 2. Загрузка данных
    loader = VoynichDataLoader('ZL3b-n.txt')
    if not loader.load():
        print("❌ Не удалось загрузить файл ZL3b-n.txt")
        print("💡 Убедитесь, что файл находится в той же папке, что и скрипт.")
        return
    
    loader.parse_pages()
    
    # 3. Анализ
    analyzer = VoynichAnalyzer(loader, parser)
    
    # Анализируем первые 20 страниц
    pages_to_analyze = list(loader.pages.keys())[:20]
    
    print(f"\n🔬 Анализ {len(pages_to_analyze)} страниц...")
    report = analyzer.generate_report(pages_to_analyze)
    
    # 4. Вывод отчёта
    print("\n" + report)
    
    # 5. Сохранение отчёта
    with open('voynich_analysis_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n Отчёт сохранён: voynich_analysis_report.txt")
    
    # 6. Статистика по разделам
    print("\n" + "=" * 70)
    print(" СВОДНАЯ СТАТИСТИКА ПО РАЗДЕЛАМ")
    print("=" * 70)
    
    section_stats = {}
    for page, result in analyzer.results.items():
        if result['section']:
            section_name = result['section'].name_ru
            if section_name not in section_stats:
                section_stats[section_name] = {
                    'pages': 0,
                    'total_words': 0,
                    'parsed_words': 0
                }
            section_stats[section_name]['pages'] += 1
            section_stats[section_name]['total_words'] += result['total_words']
            section_stats[section_name]['parsed_words'] += result['parsed_words']
    
    for section_name, stats in section_stats.items():
        ratio = stats['parsed_words'] / stats['total_words'] if stats['total_words'] else 0
        print(f"\n📚 {section_name}:")
        print(f"   Страниц: {stats['pages']}")
        print(f"   Слов: {stats['total_words']}")
        print(f"   Распознано: {stats['parsed_words']} ({ratio:.1%})")
    
    print("\n" + "=" * 70)
    print("✅ АНАЛИЗ ЗАВЕРШЁН")
    print("=" * 70)


if __name__ == '__main__':
    main()
