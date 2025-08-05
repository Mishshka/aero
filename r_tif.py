import rasterio
import matplotlib.pyplot as plt
from pathlib import Path
import numpy as np

def visualize_large_dem_tif(file_path, downscale_factor=10):
    path = Path(file_path)

    # Проверка: файл существует?
    if not path.exists():
        print(f"❌ Файл не найден: {path.absolute()}")
        return

    print(f"✅ Файл найден: {path.absolute()}")

    try:
        with rasterio.open(path) as src:
            # Уменьшаем размер при чтении
            width = src.width // downscale_factor
            height = src.height // downscale_factor

            # Читаем первый канал с уменьшением
            band1 = src.read(1, out_shape=(height, width), resampling=rasterio.enums.Resampling.bilinear)

            print(f"📊 Форма данных после уменьшения: {band1.shape} (высота x ширина)")
            print(f"📏 Исходный размер: {src.width}x{src.height} → Уменьшено в {downscale_factor} раз")

            # Заменяем NoData на NaN
            if src.nodata is not None:
                band1 = band1.astype('float32')
                band1[band1 == src.nodata] = np.nan

            # Убираем выбросы для лучшего контраста
            min_val = np.nanpercentile(band1, 1)
            max_val = np.nanpercentile(band1, 99)
            print(f"📉 Диапазон высот (1–99%): {min_val:.2f} м – {max_val:.2f} м")

            # Визуализация
            plt.figure(figsize=(12, 8))
            img = plt.imshow(band1, cmap='gist_earth', vmin=min_val, vmax=max_val)
            plt.colorbar(img, label='Высота (м)')
            plt.title("Цифровая модель высот (DEM) - уменьшенное разрешение", fontsize=14)
            plt.xlabel("Пиксели (уменьшено)")
            plt.ylabel("Пиксели (уменьшено)")
            plt.tight_layout()
            plt.show()

    except Exception as e:
        print(f"❌ Ошибка: {e}")

# === ЗАПУСК ===
if __name__ == "__main__":
    file_path = "dem_part.tif"
    #file_path = "ortho 4 cm part.tif"
    visualize_large_dem_tif(file_path, downscale_factor=10)  # Можно поставить 5, если хочешь больше деталей