import folium
import json
import os
from pathlib import Path

def visualize_geojson(file_path, output_html="map.html"):
    path = Path(file_path)

    # Проверка: файл существует?
    if not path.exists():
        print(f"❌ Файл не найден: {path.absolute()}")
        return

    print(f"✅ Файл найден: {path.absolute()}")

    # Чтение файла
    try:
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"📄 Файл прочитан. Длина: {len(content)} символов.")
    except Exception as e:
        print(f"❌ Ошибка чтения файла: {e}")
        return

    # Исправим возможные обрывы (если файл не завершён)
    content = content.strip()
    if not content.endswith('}'):
        content += '}'  # попробуем закрыть
        print("⚠️  Файл был обрезан — добавлено закрытие объекта")

    # Парсим JSON
    try:
        data = json.loads(content)
        print("✅ GeoJSON успешно загружен")
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return

    # Определяем центр карты (средние координаты)
    all_coords = []

    def extract_coords(geom):
        if geom["type"] == "MultiPolygon":
            for polygon in geom["coordinates"]:
                for ring in polygon:
                    all_coords.extend(ring)
        elif geom["type"] == "Polygon":
            for ring in geom["coordinates"]:
                all_coords.extend(ring)

    # Собираем все координаты
    features = data["features"] if data["type"] == "FeatureCollection" else [data]
    for feature in features:
        if "geometry" in feature:
            extract_coords(feature["geometry"])

    if not all_coords:
        print("❌ Не удалось найти координаты для отображения")
        return

    # Вычисляем центр
    lats = [c[1] for c in all_coords]
    lons = [c[0] for c in all_coords]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    # Создаём карту
    m = folium.Map(location=[center_lat, center_lon], zoom_start=14, tiles="OpenStreetMap")

    # Цвета по типу объекта
    color_map = {
        "Пахотные земли": "green",
        "Залежи (травы)": "orange",
        "Залежи (кустарник, деревья)": "darkred",
        "Леса и лесополосы": "darkgreen",
        "Дороги": "gray",
        "Необрабатываемые ввиду особенностей рельефа, увлажнения и пр": "beige"
    }

    # Добавляем каждый участок
    for feature in features:
        props = feature.get("properties", {})
        geom = feature.get("geometry")

        name = props.get("nm", "Без названия")
        obj_type = props.get("object", "Неизвестно")
        area = props.get("area_ga", 0)
        fid = props.get("fid", "N/A")

        # Цвет по типу
        color = color_map.get(obj_type, "blue")

        # Всплывающая подсказка
        popup_text = f"""
        <b>Участок:</b> {name}<br>
        <b>Тип:</b> {obj_type}<br>
        <b>Площадь:</b> {area:.3f} га<br>
        <b>FID:</b> {fid}
        """
        popup = folium.Popup(popup_text, max_width=300)

        # Подпись на карте
        tooltip = f"{obj_type} ({area:.2f} га)"

        # Добавляем полигон
        if geom and geom["type"] in ["Polygon", "MultiPolygon"]:
            folium.GeoJson(
                feature,
                style_function=lambda x, col=color: {"fillColor": col, "color": col, "weight": 2, "fillOpacity": 0.5},
                tooltip=tooltip,
                popup=popup
            ).add_to(m)

    # Сохраняем и открываем
    m.save(output_html)
    print(f"🌍 Карта сохранена: {os.path.abspath(output_html)}")
    print("✅ Открой файл в браузере!")

# Запуск
if __name__ == "__main__":
    file_path = "class_part.geojson"  # Убедись, что файл так называется и лежит рядом
    visualize_geojson(file_path, "land_map.html")