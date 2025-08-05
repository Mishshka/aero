from ultralytics import YOLO
import cv2
import numpy as np

# Шаг 1: Загрузка модели
def load_model(model_path):
    """
    Загружает модель YOLOv8 для сегментации.
    """
    model = YOLO(model_path)
    return model

# Шаг 2: Обработка изображения
def process_image(model, image_path):
    """
    Процессирует аэроснимок и выполняет сегментацию.
    """
    # Чтение изображения
    img = cv2.imread(image_path)

    # Выполнение инференса
    results = model(img)

    # Получение результатов
    result = results[0]

    # Визуализация результатов
    annotated_frame = result.plot()  # Рисует маски и bounding boxes на изображении

    return annotated_frame, result

# Шаг 3: Сохранение результатов
def save_results(annotated_frame, output_path):
    """
    Сохраняет визуализированный результат сегментации.
    """
    cv2.imwrite(output_path, annotated_frame)

# Шаг 4: Дополнительная обработка (если нужно)
def extract_masks(result):
    """
    Извлекает маски для каждого класса.
    """
    masks = result.masks.data.cpu().numpy()  # Маски в виде массива [N, H, W]
    class_ids = result.boxes.cls.cpu().numpy().astype(int)  # ID классов

    # Создание словаря для хранения масок по классам
    mask_dict = {}
    for i, mask in enumerate(masks):
        class_id = class_ids[i]
        if class_id not in mask_dict:
            mask_dict[class_id] = mask
        else:
            mask_dict[class_id] += mask

    return mask_dict

# Главная функция
def main():
    # Путь к модели
    model_path = 'yolov8n-seg.pt'  # Предварительно обученная модель для сегментации
    # model_path = 'path/to/your/trained/model.pt'  # Если используете свою обученную модель

    # Путь к аэроснимку
    image_path = '2024_09_07_rRX_g201b20332_f003_0389.JPG'

    # Путь для сохранения результата
    output_path = 'segmented_aerial_image.jpg'

    # 1. Загрузка модели
    model = load_model(model_path)

    # 2. Обработка изображения
    annotated_frame, result = process_image(model, image_path)

    # 3. Сохранение результатов
    save_results(annotated_frame, output_path)

    # 4. Дополнительная обработка (если нужно)
    mask_dict = extract_masks(result)

    # Пример: Сохранение маски для первого класса
    if 0 in mask_dict:
        mask_class_0 = mask_dict[0].astype(np.uint8) * 255
        cv2.imwrite("mask_class_0.jpg", mask_class_0)

    print(f"Результаты сохранены в {output_path}")

if __name__ == "__main__":
    main()