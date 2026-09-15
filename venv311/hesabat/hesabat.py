import os
from datetime import datetime


class Transaction:
    """Bir əməliyyatı (gəlir və ya xərc) təmsil edir."""

    def __init__(self, ttype, amount, description, date=None):
        self.ttype = ttype  # "gəlir" və ya "xərc"
        self.amount = amount
        self.description = description
        # Tarix verilməyibsə, bugünkü tarixi götürürük
        self.date = date if date else datetime.now().strftime("%Y-%m-%d")

    def to_dict(self):
        """Obyekti dict formatına çevirir (siyahıda saxlamaq üçün)."""
        return {
            "ttype": self.ttype,
            "amount": self.amount,
            "description": self.description,
            "date": self.date,
        }

    def to_line(self):
        """Faylda saxlamaq üçün bir sətir formatına çevirir."""
        return f"{self.ttype}|{self.amount}|{self.description}|{self.date}"

    @staticmethod
    def from_line(line):
        """Fayldan oxunan sətri Transaction obyektinə çevirir."""
        ttype, amount, description, date = line.strip().split("|")
        return Transaction(ttype, float(amount), description, date)

    def __str__(self):
        return f"[{self.date}] {self.ttype.upper():6} | {self.amount:>10.2f} AZN | {self.description}"


class BudgetManager:
    """Bütün əməliyyatları və balansı idarə edir (balans encapsulated)."""

    def __init__(self, filename="transactions.txt"):
        self.__filename = filename
        self.__balance = 0.0          # encapsulated - birbaşa xaricdən dəyişilmir
        self.__transactions = []      # list of Transaction obyektləri
        self.load_from_file()

    # ---------- Encapsulation üçün getter ----------
    def get_balance(self):
        return self.__balance

    # ---------- Gəlir/Xərc əlavə etmək ----------
    def add_transaction(self, ttype, amount, description, date=None):
        try:
            amount = float(amount)  # mətn ədəd kimi daxil edilibsə burda ValueError yaranacaq
            if amount <= 0:
                raise ValueError("Məbləğ müsbət ədəd olmalıdır!")
        except ValueError as e:
            print(f"XƏTA: Yanlış məbləğ daxil edildi -> {e}")
            return False

        transaction = Transaction(ttype, amount, description, date)
        self.__transactions.append(transaction)

        if ttype == "gəlir":
            self.__balance += amount
        elif ttype == "xərc":
            self.__balance -= amount

        self.save_to_file()
        print("Əməliyyat uğurla əlavə olundu.")
        return True

    # ---------- Tarixə görə filtrasiya (loop ilə) ----------
    def filter_by_date(self, start_date, end_date):
        result = []
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
        except ValueError:
            print("XƏTA: Tarix formatı YYYY-MM-DD şəklində olmalıdır!")
            return result

        for t in self.__transactions:  # dövrə (loop) ilə filtrasiya
            t_date = datetime.strptime(t.date, "%Y-%m-%d")
            if start <= t_date <= end:
                result.append(t)
        return result

    # ---------- Hesabatı göstərmək ----------
    def show_report(self, transactions=None):
        transactions = transactions if transactions is not None else self.__transactions
        if not transactions:
            print("Heç bir əməliyyat tapılmadı.")
            return
        print("-" * 55)
        for t in transactions:
            print(t)
        print("-" * 55)
        print(f"Cari balans: {self.__balance:.2f} AZN")

    # ---------- Fayla yazmaq ----------
    def save_to_file(self):
        try:
            with open(self.__filename, "w", encoding="utf-8") as f:
                for t in self.__transactions:
                    f.write(t.to_line() + "\n")
        except IOError as e:
            print(f"XƏTA: Fayla yazarkən problem yarandı -> {e}")

    # ---------- Fayldan oxumaq ----------
    def load_from_file(self):
        if not os.path.exists(self.__filename):
            return
        try:
            with open(self.__filename, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        t = Transaction.from_line(line)
                        self.__transactions.append(t)
                        if t.ttype == "gəlir":
                            self.__balance += t.amount
                        elif t.ttype == "xərc":
                            self.__balance -= t.amount
        except (IOError, ValueError) as e:
            print(f"XƏTA: Fayl oxunarkən problem yarandı -> {e}")

    # ---------- Cədvəli sıfırlamaq ----------
    def reset(self):
        """Bütün əməliyyatları və balansı sıfırlayır, transactions.txt-ni boşaldır."""
        self.__transactions = []
        self.__balance = 0.0
        self.save_to_file()
        print("Cədvəl sıfırlandı. Bütün əməliyyatlar silindi, balans 0-a endirildi.")


def menu():
    manager = BudgetManager()

    while True:
        print("\n===== ŞƏXSI BÜDCƏ İDARƏETMƏ SİSTEMİ =====")
        print("1. Gəlir əlavə et")
        print("2. Xərc əlavə et")
        print("3. Bütün əməliyyatları göstər")
        print("4. Tarixə görə filtrasiya et")
        print("5. Cari balansı göstər")
        print("6. Cədvəli sıfırla")
        print("7. Çıxış")

        choice = input("Seçiminizi daxil edin (1-7): ").strip()

        if choice == "1":
            amount = input("Məbləği daxil edin: ")
            description = input("Açıqlama: ")
            date = input("Tarix (YYYY-MM-DD) [boş buraxsanız bugünkü tarix]: ").strip()
            manager.add_transaction("gəlir", amount, description, date if date else None)

        elif choice == "2":
            amount = input("Məbləği daxil edin: ")
            description = input("Açıqlama: ")
            date = input("Tarix (YYYY-MM-DD) [boş buraxsanız bugünkü tarix]: ").strip()
            manager.add_transaction("xərc", amount, description, date if date else None)

        elif choice == "3":
            manager.show_report()

        elif choice == "4":
            start_date = input("Başlanğıc tarix (YYYY-MM-DD): ").strip()
            end_date = input("Son tarix (YYYY-MM-DD): ").strip()
            filtered = manager.filter_by_date(start_date, end_date)
            manager.show_report(filtered)

        elif choice == "5":
            print(f"Cari balans: {manager.get_balance():.2f} AZN")

        elif choice == "6":
            confirm = input("Əminsiniz? Bütün data silinəcək (b/x): ").strip().lower()
            if confirm == "b":
                manager.reset()
            else:
                print("Sıfırlama ləğv edildi.")

        elif choice == "7":
            print("Proqramdan çıxılır. Bütün məlumatlar transactions.txt faylında saxlanıldı.")
            break

        else:
            print("Yanlış seçim! Zəhmət olmasa 1-7 arası ədəd daxil edin.")


if __name__ == "__main__":
    menu()