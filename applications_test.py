
from agent.modules.applications import applications


def main():
    print("=" * 45)
    print("LOCALMIND - GESTION DES APPLICATIONS")
    print("=" * 45)

    while True:
        print("\n1. Ouvrir une application")
        print("2. Fermer une application")
        print("3. Rechercher une application")
        print("4. Vérifier si une application est ouverte")
        print("0. Quitter")

        choice = input("\nTon choix : ").strip()

        if choice == "0":
            print("Fermeture du test.")
            break

        elif choice == "1":
            name = input("Application à ouvrir : ")
            result = applications.open_application(name)

        elif choice == "2":
            name = input("Application à fermer : ")
            result = applications.close_application(name)

        elif choice == "3":
            name = input("Application à rechercher : ")
            result = applications.find_application(name)

        elif choice == "4":
            name = input("Application à vérifier : ")
            result = applications.is_application_running(name)

        else:
            print("Choix invalide.")
            continue

        print("\nRésultat :")
        print(result)


if __name__ == "__main__":
    main()
