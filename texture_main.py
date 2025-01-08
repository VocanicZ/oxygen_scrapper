import texture_crop as crop
import safe_open

def main():
    scale = 16
    size = 16
    ls = safe_open.r("database/db_map.json")
    solid = ls.get("solid", {})
    for key, value in solid.items():
        try:
            crop.process_and_crop_image(key+".png", size, scale, value)
        except Exception as e:
            print(f"Error: {e}")
            continue

main()