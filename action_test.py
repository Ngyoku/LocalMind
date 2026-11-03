
from action_manager import actions

print("=" * 45)
print("LOCALMIND - TEST DES ACTIONS")
print("=" * 45)

while True:
    print("\n1. Ouvrir la caméra")
    print("2. Ouvrir la calculatrice")
    print("3. Ouvrir le Bloc-notes")
    print("4. Tester une action interdite")
    print("0. Quitter")

    choice = input("\nChoisis une action : ").strip()

    if choice == "1":
        result = actions.execute("open_camera")

    elif choice == "2":
        result = actions.execute("open_calculator")

    elif choice == "3":
        result = actions.execute("open_notepad")

    elif choice == "4":
        result = actions.execute("delete_all_files")

    elif choice == "0":
        break

    else:
        print("Choix invalide.")
        continue

    print("\nRésultat :", result)
