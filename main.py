
import xml.etree.ElementTree as ET
from pathlib import Path

def read_kml_file_advanced(file_path):
    path = Path(file_path)
    if not path.exists():
        print(f"❌ Файл не найден: {path.absolute()}")
        return

    print(f"✅ Файл найден: {path.absolute()}")

    try:
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        print(f"📄 Файл прочитан. Длина: {len(content)} символов.")
    except Exception as e:
        print(f"❌ Ошибка чтения: {e}")
        return

    # Убираем namespace для простоты (основная причина проблем!)
    content_clean = content
    # Удаляем xmlns, но сохраняем теги
    content_clean = content_clean.replace('xmlns="http://www.opengis.net/kml/2.2"', '')
    content_clean = content_clean.strip()

    try:
        root = ET.fromstring(content_clean)
    except ET.ParseError as e:
        print(f"❌ Ошибка парсинга XML: {e}")
        return

    print(f"✅ XML распаршен. Корневой тег: {root.tag}")

    placemarks = root.findall(".//Placemark")
    print(f"📍 Найдено Placemark: {len(placemarks)}")

    for i, pm in enumerate(placemarks):
        name_elem = pm.find("name")
        name = (name_elem.text if name_elem is not None and name_elem.text else f"Placemark_{i}")

        print(f"\n📌 {name}:")

        # Поиск координат в разных типах геометрии
        found = False

        # 1. Point
        point = pm.find("Point")
        if point is not None:
            coord_elem = point.find("coordinates")
            if coord_elem is not None and coord_elem.text:
                coords = coord_elem.text.strip()
                try:
                    lon, lat, *alt = map(str.strip, coords.split(','))
                    lat = float(lat)
                    lon = float(lon)
                    alt = float(alt[0]) if alt else "Н/Д"
                    print(f"  📍 Точка: широта={lat:.6f}, долгота={lon:.6f}, высота={alt}")
                    found = True
                except:
                    print(f"  ⚠️  Ошибка парсинга координат: {coords}")

        # 2. LineString (часто — трек полета)
        linestring = pm.find("LineString")
        if linestring is not None:
            coord_elem = linestring.find("coordinates")
            if coord_elem is not None and coord_elem.text:
                coords_text = coord_elem.text.strip()
                print(f"  🛤️ Линия (LineString): найдены координаты (всего точек: {coords_text.count(',') + 1})")
                # Покажем первую и последнюю
                points = [p.strip().split(',') for p in coords_text.split() if p.strip()]
                if points:
                    first = points[0]
                    last = points[-1]
                    try:
                        flon, flat = float(first[0]), float(first[1])
                        llon, llat = float(last[0]), float(last[1])
                        print(f"    Начало: {flat:.6f}, {flon:.6f}")
                        print(f"    Конец:  {llat:.6f}, {llon:.6f}")
                        if len(points) > 10:
                            print(f"    Всего точек: {len(points)}")
                        found = True
                    except:
                        print(f"    ⚠️  Ошибка при разборе координат линии")

        # 3. Polygon (область съемки)
        polygon = pm.find("Polygon")
        if polygon is not None:
            outer = polygon.find("outerBoundaryIs/LinearRing/coordinates")
            if outer is not None and outer.text:
                coords_text = outer.text.strip()
                print(f"  🟦 Полигон: внешняя граница (точек: {coords_text.count(',') + 1})")
                points = [p.strip().split(',') for p in coords_text.split() if p.strip()]
                if points:
                    first = points[0]
                    try:
                        flon, flat = float(first[0]), float(first[1])
                        print(f"    Первая точка: {flat:.6f}, {flon:.6f}")
                        print(f"    Всего вершин: {len(points)}")
                        found = True
                    except:
                        print(f"    ⚠️  Ошибка разбора координат полигона")

        if not found:
            print("  ❌ Нет поддерживаемой геометрии (Point, LineString, Polygon)")

# Запуск
if __name__ == "__main__":
    file_path = "2024_09_07_rRX_g201b20332_f003_.kml"
    read_kml_file_advanced(file_path)
