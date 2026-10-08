from encryption_service import EncryptionService
from interface import RekoApp
from tkinter import *

def main():
    root = Tk()
    app = RekoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
