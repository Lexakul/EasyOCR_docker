
import json
import os
from difflib import SequenceMatcher
import math
import easyocr


def calculate_center(bbox):
    """Вычисляет центр bounding box"""
    x = sum(point[0] for point in bbox) / 4
    y = sum(point[1] for point in bbox) / 4
    return x, y


def compare_elements(current, reference):
    """Сравнивает текущий и эталонный элементы"""
    text_sim = SequenceMatcher(None, current['text'], reference['text']).ratio()

    cur_center = calculate_center(current['bbox'])
    ref_center = calculate_center(reference['bbox'])
    coord_diff = math.sqrt((cur_center[0] - ref_center[0]) ** 2 + (cur_center[1] - ref_center[1]) ** 2)

    return {
        'text_similarity': text_sim,
        'coord_diff': coord_diff,
        'current_text': current['text'],
        'reference_text': reference['text']
    }


def main():
    reference_file = "./results/streetname_20250531_205012.json"
    image_path = "streetname.jpg"
    #Проверка существования файлов
    if not os.path.exists(reference_file):
        print(f"Ошибка: Эталонный файл не найден по пути: {reference_file}")
        print("Проверьте:")
        print(f"1. Существует ли файл по указанному пути")
        print(f"2. Правильно ли написано имя файла (регистр букв важен!)")
        print(f"3. Полный путь к файлу: {os.path.abspath(reference_file)}")
        return

    if not os.path.exists(image_path):
        print(f"Ошибка: Изображение не найдено: {image_path}")
        return

    #Получение текущих результатов
    print("Запуск распознавания...")
    reader = easyocr.Reader(['en', 'ru'])
    current_raw = reader.readtext(image_path)
    current_results = [{
        'text': text,
        'bbox': bbox,
        'confidence': float(confidence)
    } for bbox, text, confidence in current_raw]

    #Загрузка эталонных данных
    try:
        with open(reference_file, 'r', encoding='utf-8') as f:
            reference_results = json.load(f)
        print(f"Загружен эталонный файл: {reference_file}")
    except Exception as e:
        print(f"Ошибка загрузки JSON: {str(e)}")
        return

    #Сравнение результатов
    print("\nДетальное сравнение:")
    print("=" * 60)

    total_text = 0
    total_coord = 0
    matched = 0

    min_length = min(len(current_results), len(reference_results))
    for i in range(min_length):
        comp = compare_elements(current_results[i], reference_results[i])

        print(f"Элемент {i + 1}:")
        print(f"Текст: '{comp['reference_text']}' → '{comp['current_text']}'")
        print(f"Сходство текста: {comp['text_similarity']:.1%}")
        if comp['coord_diff'] > 2:
            print(f"Смещение: {comp['coord_diff']:.1f} px")
        print("-" * 60)

        total_text += comp['text_similarity']
        total_coord += max(0, 1 - comp['coord_diff'] / 50)
        matched += 1

    #Итого
    if matched > 0:
        print("\nИтоговые метрики:")
        print("=" * 60)
        print(f"Среднее сходство текста: {total_text / matched:.1%}")
        print(f"Среднее сходство координат: {total_coord / matched:.1%}")
        print(f"Общая точность: {(0.7 * total_text / matched + 0.3 * total_coord / matched):.1%}")

    if len(current_results) != len(reference_results):
        diff = abs(len(current_results) - len(reference_results))
        print(f"\nВнимание: разное количество элементов (разница: {diff})")


if __name__ == "__main__":
    main()