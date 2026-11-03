from hardware_detector import hardware
import json

print("=" * 50)
print("LOCALMIND - ANALYSE DU MATÉRIEL")
print("=" * 50)

information = hardware.get_hardware_info()

print(json.dumps(
    information,
    indent=4,
    ensure_ascii=False
))
