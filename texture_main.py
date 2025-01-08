import texture_crop as crop
import safe_open

def main():
    scale = 1
    size = 128
    ls = safe_open.r("database/db_map.json")
    override = safe_open.r("texture_override.json")
    override_material = override.get("solid", {}).get("override", {})
    solid = ls.get("solid", {})
    for key, value in solid.items():
        if key in override_material:
            k = override_material[key]
        else:
            k = key
        try:
            crop.process_and_crop_image(k+".png", size, scale, value)
        except Exception as e:
            print(f"Error: {e}")
            continue

main()