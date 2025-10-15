#IRL Detect
import csv
import datetime
import time
import os
import schedule
from plyer import notification
# Lydfil #
import winsound

def play_sound(sound_file="bad-to-the-bone.wav"):
    """Spil en brugerdefineret .wav fil i Windows."""
    if not os.path.exists(sound_file):
        print(f"(Lyfil '{sound_file}' ikke fundet.)")
        return

    try:
        winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    except Exception as e:
        print("Kunne ike afspil lyd:", e)
#-----------------------------#
BIRTHDAY_FILE = "fødselsdage.csv"
CHECK_TIME = "09:00"  # Dagtid for at tjeke fødselsdage
REMINDER_DAYS = [0, 1, 7]  # Notifikation 1 day før, og 7 days før

#Fødselsdag Alarm
class Person:
    def __init__(self, navn, day, month, year=None):
        self.navn = str(navn)
        self.day = int(day)
        self.month = int(month)
        self.year = int(year) if year not in (None, "", "Intet") else None

    def næste_fødselsdag(self):
        """Returner personets næste fødselsdag."""
        today = datetime.date.today()
        year = int(today.year)
        try:
            fday = datetime.date(year, self.month, self.day)
        except ValueError:
            # handler Feb 29 fødselsdag på skudåre
            fday = datetime.date(year, 2, 28)

        if fday < today:
            try:
                fday = datetime.date(year + 1, self.month, self.day)
            except ValueError:
                fday = datetime.date(year + 1, 2, 28)
        return fday

    def days_indtil_fødselsdag(self):
        """Dage indtil næste fødselsdag."""
        return (self.næste_fødselsdag() - datetime.date.today()).days

    def nuværende_alder(self, today=None):
        if self.year is None:
            return None
        if today is None:
            today = datetime.date.today()
        Alder = today.year - self.year
        if (today.month, today.day) < (self.month, self.day):
            Alder -= 1
        return Alder

    def to_list(self):
        """Returner CSV som en list"""
        return [self.navn, self.month, self.day, self.year if self.year else ""]

    @staticmethod
    def from_list(row):
        """Kreer Person objekt fra CSV"""
        return Person(row[0], row[1], row[2], row[3] if len(row) > 3 else None)

# ---------- Fil Ledning ----------
def indlæs_fødselsdag():
    if not os.path.exists(BIRTHDAY_FILE):
        return []
    fødselsdag = []
    with open(BIRTHDAY_FILE, "r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader, None)
        for row in reader:
            if len(row) >= 3:
                fødselsdag.append(Person.from_list(row))
    return fødselsdag

def gem_fødselsdag(fødselsdag):
    with open(BIRTHDAY_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["navn", "month", "day", "year"])
        for p in fødselsdag:
            writer.writerow(p.to_list())

# ---------- Kerne Elementer ----------
def tilføj_fødselsdag(fødselsdag):
    print("\n--- Tiljøj en fødselsdag ---")
    navn = input("Angiv navn: ").strip()
    month = int(input("Angiv måned (1-12): "))
    day = int(input("Angiv dag (1-31): "))
    year_input = input("Angiv fødsels år (valgfri): ").strip()
    year = int(year_input) if year_input else None

    person = Person(navn, month, day, year)
    fødselsdag.append(person)
    gem_fødselsdag(fødselsdag)
    print(f"Tilføjet {navn}s fødselsdag ({month}/{day}/{year or '----'})!")

def vise_fødselsdag(fødselsdag):
    print("\n=-=-=-=- Fødselsdagslist -=-=-=-=")
    if not fødselsdag:
        print("Ingen fødselsdag tilføjet endnu.")
        return
    for p in fødselsdag:
        alder_text = f", Alder: {p.nuværende_alder()}" if p.nuværende_alder() is not None else ""
        y = f" ({p.year})" if p.year else ""
        print(f"- {p.navn}: {p.month:02d}-{p.day:02d}{y}{alder_text}")

def tjek_fødselsdag(fødselsdag):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}] Tjeker fødselsdage...") #sætter op en skabelon for et dato
    alerts = []
    for person in fødselsdag:
        days_tilbage = person.days_indtil_fødselsdag()
        if days_tilbage in REMINDER_DAYS:
            alder_text = ""
            if days_tilbage == 0 and person.nuværende_alder() is not None:
                alder_text = f" — de bliver {person.nuværende_alder()}!"
            when = "I dag" if days_tilbage == 0 else f"om {days_tilbage} dage"
            alerts.append(f"{person.navn}s fødselsdag er {when}{alder_text}")

    if alerts:
        message = "\n".join(alerts)
        print(message)
        notification.notify(
            title="FØDSELSDAG PÅMINDELSE!!!",
            message=message,
            timeout=10
        )
        play_sound("bad-to-the-bone.wav")
    else:
        print("Intet kommende fødselsdag...")

def daily_scheduler(fødselsdag):
    schedule.clear()
    schedule.every().day.at(CHECK_TIME).do(tjek_fødselsdag, fødselsdag=fødselsdag)
    print(f"\nDaglig fødselsdag tjek tidsplanlagt til {CHECK_TIME}. (Press Ctrl+C to stop)")
    tjek_fødselsdag(fødselsdag)
    try:
        while True:
            schedule.run_pending()
            time.sleep(10)
    except KeyboardInterrupt:
        print("Forlader tidsplanen.")

# ---------- Main Menu ----------
def main():
    fødselsdag = indlæs_fødselsdag()

    while True:
        print("\n=-> Fødselsdag Alarm Menu :D <-=")
        print("1. Vis alle fødselsdage")
        print("2. Tilføj en fødselsdag")
        print("3. Tjek fødselsdage nu")
        print("4. Kør daglig påmindelse")
        print("5. Afslut program")
        print("==-=-=-=-=-=-=-=-=-=-=-=-=-=-==")

        choice = input("Vælge en mulighed: ").strip()

        if choice == "1":
            vise_fødselsdag(fødselsdag)
        elif choice == "2":
            tilføj_fødselsdag(fødselsdag)
        elif choice == "3":
            tjek_fødselsdag(fødselsdag)
        elif choice == "4":
            daily_scheduler(fødselsdag)
        elif choice == "5":
            print("Farvel!")
            break
        else:
            print("Ugyldig valgmulighed. Prøv igen.")
        print("==-=-=-=-=-=-=-=-=-=-=-=-=-=-==")


if __name__ == "__main__":
    main()