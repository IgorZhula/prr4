import os
import time
from multiprocessing import Pool
from pathlib import Path

# Пытаемся импортировать PIL с обработкой ошибки
try:
    from PIL import Image

    PIL_AVAILABLE = True
    print("✓ Библиотека Pillow успешно загружена")
except ImportError as import_err:
    PIL_AVAILABLE = False
    print(f"✗ Ошибка: Pillow не установлен. Ошибка: {import_err}")
    print("  Установите командой: pip install Pillow")
    exit(1)


def process_single_image(params):
    """Обработка одного изображения"""
    image_path, output_dir = params
    prefix = "out_"

    try:
        # Открываем изображение
        img = Image.open(image_path)

        # 1. Поворот на 90 градусов по часовой стрелке
        img_rotated = img.rotate(-90, expand=True)

        # 2. Изменение размера до 800x600 с фильтром LANCZOS
        img_resized = img_rotated.resize((800, 600), Image.Resampling.LANCZOS)

        # 3. Преобразование в оттенки серого
        img_gray = img_resized.convert('L')

        # Формируем имя выходного файла
        original_name = Path(image_path).stem
        output_filename = f"{prefix}{original_name}.jpg"
        output_path = os.path.join(output_dir, output_filename)

        # Сохраняем результат
        img_gray.save(output_path, 'JPEG', quality=95)

        print(f"  ✓ Обработано: {original_name}")
        return True

    except Exception as processing_err:
        print(f"  ✗ Ошибка при обработке {image_path}: {processing_err}")
        return False


def sequential_processing(image_files, output_dir):
    """Последовательная обработка"""
    print("\nНачинаем последовательную обработку...")
    start_time = time.time()

    for i, img_file in enumerate(image_files):
        print(f"Обработка {i + 1}/{len(image_files)}: {os.path.basename(img_file)}")
        params = (img_file, output_dir)
        process_single_image(params)

    elapsed_time = time.time() - start_time
    return elapsed_time


def parallel_processing(image_files, output_dir):
    """Параллельная обработка с multiprocessing.Pool"""
    print("\nНачинаем параллельную обработку...")
    start_time = time.time()

    num_workers = min(os.cpu_count(), len(image_files))
    print(f"Используем {num_workers} процессов")

    # Подготавливаем аргументы для каждого изображения
    args_list = [(img_file, output_dir) for img_file in image_files]

    with Pool(processes=num_workers) as pool:
        results = pool.map(process_single_image, args_list)

        # Выводим статистику
        success_count = sum(results)
        fail_count = len(results) - success_count
        print(f"\nРезультат: успешно {success_count}, ошибок {fail_count}")

    elapsed_time = time.time() - start_time
    return elapsed_time


def get_image_files(folder_path):
    """Получает список всех JPG/JPEG файлов в папке"""
    image_extensions = {'.jpg', '.jpeg', '.JPG', '.JPEG'}
    image_files = []

    try:
        for file in os.listdir(folder_path):
            if any(file.endswith(ext) for ext in image_extensions):
                image_files.append(os.path.join(folder_path, file))
    except Exception as dir_err:
        print(f"Ошибка при чтении папки: {dir_err}")
        return []

    return image_files


def clear_output_folder(output_dir):
    """Очищает выходную папку"""
    if os.path.exists(output_dir):
        for file in os.listdir(output_dir):
            file_path = os.path.join(output_dir, file)
            if os.path.isfile(file_path):
                os.unlink(file_path)
    else:
        os.makedirs(output_dir)


def main():
    print("=" * 60)
    print("ОБРАБОТЧИК ИЗОБРАЖЕНИЙ")
    print("=" * 60)

    # Проверка наличия PIL
    if not PIL_AVAILABLE:
        print("\nНевозможно продолжить: Pillow не установлен")
        print("Выполните в терминале: pip install Pillow")
        return

    # Ввод пути к папке с изображениями
    print("\nВведите путь к папке с изображениями")
    print("(например: C:\\Users\\YourName\\Desktop\\photos или ./images)")
    input_folder = input("\nПуть: ").strip()

    # Убираем кавычки если есть
    input_folder = input_folder.strip('"').strip("'")

    # Проверяем существует ли папка
    if not os.path.exists(input_folder):
        print(f"\nОшибка: Папка '{input_folder}' не найдена!")
        print("Проверьте правильность пути")
        return

    # Получаем все изображения
    image_files = get_image_files(input_folder)

    if not image_files:
        print(f"\nВ папке '{input_folder}' не найдено изображений .jpg или .jpeg")
        return

    # Создаем и очищаем выходную папку
    output_dir = "processed"
    clear_output_folder(output_dir)

    print(f"\nНайдено изображений: {len(image_files)}")
    print(f"Выходная папка: {output_dir}")

    # Показываем список файлов
    print("\nСписок файлов для обработки:")
    for i, file in enumerate(image_files, 1):
        print(f"  {i}. {os.path.basename(file)}")

    # Выбор режима
    print("\n" + "=" * 60)
    print("Выберите режим обработки:")
    print("  1 - Последовательная обработка")
    print("  2 - Параллельная обработка")
    print("  3 - Оба режима (сравнение)")

    choice = input("\nВаш выбор (1/2/3): ").strip()

    if choice == "1":
        # Только последовательная
        print("\n" + "=" * 60)
        seq_time = sequential_processing(image_files, output_dir)
        print("\n" + "=" * 60)
        print(f"Время выполнения: {seq_time:.2f} секунд")

    elif choice == "2":
        # Только параллельная
        print("\n" + "=" * 60)
        par_time = parallel_processing(image_files, output_dir)
        print("\n" + "=" * 60)
        print(f"Время выполнения: {par_time:.2f} секунд")

    elif choice == "3":
        # Оба режима
        print("\n" + "=" * 60)
        print("РЕЖИМ 1: Последовательная обработка")
        seq_time = sequential_processing(image_files, output_dir)
        print(f"Время: {seq_time:.2f} секунд")

        # Очищаем выходную папку
        print("\nОчистка папки для следующего теста...")
        clear_output_folder(output_dir)

        # Параллельная
        print("\n" + "=" * 60)
        print("РЕЖИМ 2: Параллельная обработка")
        par_time = parallel_processing(image_files, output_dir)
        print(f"Время: {par_time:.2f} секунд")

        # Сравнение
        print("\n" + "=" * 60)
        print("СРАВНЕНИЕ ПРОИЗВОДИТЕЛЬНОСТИ:")
        print(f"  Последовательная: {seq_time:.2f} сек")
        print(f"  Параллельная:      {par_time:.2f} сек")

        if par_time < seq_time and seq_time > 0:
            speedup = seq_time / par_time
            print(f"  📈 Ускорение: {speedup:.2f}x")
        elif seq_time > 0:
            print(f"  ⚠️  Параллельная обработка медленнее на {par_time - seq_time:.2f} сек")

    else:
        print("\nНеверный выбор! Запустите программу снова.")
        return

    # Показываем результаты
    print("\n" + "=" * 60)
    output_files = os.listdir(output_dir)
    print(f"✅ Результаты сохранены в папке: {output_dir}")
    print(f"📁 Обработано файлов: {len(output_files)} из {len(image_files)}")

    if output_files:
        print("\n📋 Созданные файлы:")
        for file in sorted(output_files)[:10]:  # Показываем первые 10
            file_size = os.path.getsize(os.path.join(output_dir, file))
            print(f"  - {file} ({file_size:,} байт)")

        if len(output_files) > 10:
            print(f"  ... и еще {len(output_files) - 10} файлов")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Программа прервана пользователем")
    except Exception as fatal_err:
        print(f"\n❌ Критическая ошибка: {fatal_err}")
        print("Попробуйте перезапустить программу")