#!/usr/bin/env python3

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.presentation.gui.main_window import MainWindow


def main():
    try:
        app = MainWindow()
        app.run()
    except KeyboardInterrupt:
        print("\nAplicación cerrada por el usuario")
    except Exception as e:
        print(f"Error fatal: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()