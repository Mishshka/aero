from pathlib import Path
import xml.etree.ElementTree as ET

def read_qgis_qmd_file(file_path):
    path = Path(file_path)

    # Проверка: существует ли файл?
    if not path.exists():
        print(f"❌ Файл не найден: {path.absolute()}")
        return

    print(f"✅ Файл найден: {path.absolute()}")

    try:
        tree = ET.parse(path)
        root = tree.getroot()
        print(f"📄 Файл успешно загружен. Корневой тег: {root.tag}")
    except ET.ParseError as e:
        print(f"❌ Ошибка парсинга XML: {e}")
        return

    # Извлечение данных
    def safe_find_text(element, path, default="не задано"):
        found = element.find(path)
        return found.text.strip() if found is not None and found.text else default

    print("\n📋 Метаданные QGIS:")
    print(f"  Версия QGIS: {root.get('version', 'не указана')}")
    print(f"  Тип: {safe_find_text(root, 'type')}")
    print(f"  Название: {safe_find_text(root, 'title')}")
    print(f"  Описание: {safe_find_text(root, 'abstract')}")
    print(f"  Язык: {safe_find_text(root, 'language')}")

    # Контакт
    contact = root.find("contact")
    if contact is not None:
        name = safe_find_text(contact, "name")
        email = safe_find_text(contact, "email")
        org = safe_find_text(contact, "organization")
        print(f"  Контакт: {name} ({org}), email: {email}")

    # CRS (система координат)
    crs = root.find("crs/spatialrefsys")
    if crs is not None:
        srid = safe_find_text(crs, "srid")
        authid = safe_find_text(crs, "authid")
        desc = safe_find_text(crs, "description")
        print(f"  CRS: SRID={srid}, AUTHID={authid}, Описание: {desc}")

    # Extent (ограничивающий прямоугольник)
    extent = root.find("extent/spatial")
    if extent is not None:
        crs = extent.get("crs", "не задано")
        minx = extent.get("minx", "?")
        maxx = extent.get("maxx", "?")
        miny = extent.get("miny", "?")
        maxy = extent.get("maxy", "?")
        print(f"  Extent (CRS: {crs}):")
        print(f"    X: {minx} → {maxx}")
        print(f"    Y: {miny} → {maxy}")

    # Временной период
    period = root.find("extent/temporal/period")
    if period is not None:
        start = safe_find_text(period, "start", "не задано")
        end = safe_find_text(period, "end", "не задано")
        print(f"  Временной период: {start} — {end}")

# Пример использования
if __name__ == "__main__":
    file_path = "class_part.qmd"  # ← замени на имя своего файла
    read_qgis_qmd_file(file_path)