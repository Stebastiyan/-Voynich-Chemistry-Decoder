import os
import re
from collections import Counter

class VoynichThermodynamicAnalyzer:
    def __init__(self):
        # 1. Жестко фиксируем ваши новые критерии v4.0
        self.prefixes = {
            'Ot': 'отдача тепла / преднагрев (теряющий, отдающий температуру)',
            'qo': 'поток спирта / рабочее тело (приходящий, поступающий)',
            'op': 'орошение / абсорбция (принявший опрыскивание, опыление)'
        }
        
        self.roots_and_markers = {
            'sheol': 'мыльная фаза (мутное масло)',
            'sheod': 'смолянистая фаза (мутная смола)',
            'sheo': 'мутная/гетерогенная среда',
            'sho': 'интенсивное трение / перемешивание / бурление',
            'ol': 'масляная фаза / липиды',
            'ar': 'ароматная рециркуляция (эфирные масла)',
            'am': 'ароматная мацерация (экстракция духов)',
            'edy': 'состояние пара (временное определение: настоящий/бывший/будущий)',
            'd': 'принадлежность к смолам'
        }
        
        self.suffixes = {
            'k': 'кальцинирование / ощелачивание (зола, поташ)',
            'r': 'рециркуляция / возврат / рефлюкс флегмы',
            'y': 'текучесть / жидкая подвижная фаза'
        }

    def clean_word(self, word):
        """Очистка слова от знаков препинания и приведение к нижнему регистру (кроме Ot)"""
        word = word.strip(".,;:?!*-[]{}()")
        # Сохраняем Ot в исходном регистре, остальное в нижний
        if word.startswith('Ot'):
            return 'Ot' + word[2:].lower()
        return word.lower()

    def analyze_word(self, word):
        """Разбор слова по обновленной матрице v4.0"""
        cleaned = self.clean_word(word)
        if not cleaned:
            return None

        analysis = {
            'original': word,
            'cleaned': cleaned,
            'detected_elements': [],
            'physical_meaning': []
        }

        # Копия для пошагового разбора
        remainder = cleaned

        # Шаг 1: Поиск приставок направления
        for pref, desc in self.prefixes.items():
            if remainder.startswith(pref):
                analysis['detected_elements'].append(('Prefix', pref))
                analysis['physical_meaning'].append(desc)
                remainder = remainder[len(pref):]
                break

        # Шаг 2: Поиск суффиксов в конце слова (с конца)
        # Сортируем суффиксы, чтобы сначала проверять самые длинные, если появятся составные
        found_suffixes = []
        changed = True
        while changed:
            changed = False
            for suf, desc in self.suffixes.items():
                if remainder.endswith(suf):
                    found_suffixes.insert(0, ('Suffix', suf, desc))
                    remainder = remainder[:-len(suf)]
                    changed = True
                    break
        
        # Шаг 3: Поиск корней и маркеров в оставшейся части (по приоритету длины)
        # Важно: сначала ищем длинные 'sheol'/'sheod', потом короткие 'sho'/'ol'
        sorted_roots = sorted(self.roots_and_markers.items(), key=lambda x: len(x[0]), reverse=True)
        
        for root, desc in sorted_roots:
            if root in remainder:
                analysis['detected_elements'].append(('Root/Marker', root))
                analysis['physical_meaning'].append(desc)
                # Удаляем первое вхождение корня для избежания повторов
                remainder = remainder.replace(root, '', 1)

        # Добавляем найденные суффиксы в общий список в правильном порядке
        for _, suf, desc in found_suffixes:
            analysis['detected_elements'].append(('Suffix', suf))
            analysis['physical_meaning'].append(desc)

        return analysis

    def process_file(self, file_path):
        """Чтение файла транскрипции и полный статистический анализ"""
        if not os.path.exists(file_path):
            print(f"❌ Файл {file_path} не найден. Проверьте путь.")
            return

        print(f"📖 Загрузка файла: {file_path}...")
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Разбиваем на слова, игнорируя служебные строки транскрипций (начинающиеся с #)
        words = []
        for line in content.splitlines():
            line = line.strip()
            if line and not line.startswith('#'):
                # Разбиваем строку по пробелам
                words.extend(line.split())

        total_words = len(words)
        print(f"📊 Всего слов для анализа: {total_words}")

        analyzed_count = 0
        element_counter = Counter()
        matches_examples = []

        for word in words:
            analysis = self.analyze_word(word)
            if analysis and analysis['detected_elements']:
                analyzed_count += 1
                for el_type, el_val in analysis['detected_elements']:
                    element_counter[f"{el_type}: {el_val}"] += 1
                
                # Сохраняем примеры интересных разборов (сложные слова из >= 2 элементов)
                if len(analysis['detected_elements']) >= 2 and len(matches_examples) < 10:
                    matches_examples.append(analysis)

        # Вывод результатов в консоль
        print("\n" + "="*50)
        print("📈 РЕЗУЛЬТАТЫ АНАЛИЗА МАТРИЦЫ ПРОЦЕССОВ (v4.0)")
        print("="*50)
        print(f"Слов с физическими маркерами: {analyzed_count} ({(analyzed_count/total_words)*100:.2f}%)")
        
        print("\n🔝 Частотность физических маркеров в тексте:")
        for el, count in element_counter.most_common(15):
            print(f"  🔹 {el}: {count} раз")

        print("\n🧪 Примеры структурного разбора реальных слов:")
        print("-" * 50)
        for ex in matches_examples:
            print(f"Слово в EVA: {ex['original']}")
            print(f"  Структура: {' + '.join([val for _, val in ex['detected_elements']])}")
            print(f"  Физический смысл цепочки:")
            for step in ex['physical_meaning']:
                print(f"    -> {step}")
            print("-" * 50)


# === ТОЧКА ВХОДА ДЛЯ ЗАПУСКА ===
if __name__ == "__main__":
    # Укажите имя любого файла транскрипции из вашего репозитория
    # Например: 'ZL3b-n.txt', 'CD2a-n.txt' или 'VT0e-n.txt'
    FILE_PATH = 'ZL3b-n.txt' 

    # Создаем тестовый файл, если репозиторий запускается в изолированной среде
    if not os.path.exists(FILE_PATH):
        with open(FILE_PATH, 'w', encoding='utf-8') as f:
            f.write("# Тестовая транскрипция для проверки логики v4.0\n")
            f.write("Otsheoldy qokain sheody Otdy sho-ol-k\n")
            f.write("opedyk r-ol-edy sheol.y\n")

    analyzer = VoynichThermodynamicAnalyzer()
    analyzer.process_file(FILE_PATH)
