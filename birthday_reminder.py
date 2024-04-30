from controllers.whatsapp import Whatsapp
from controllers.rag import *
import time
from utils import *

rag = Neo4jGPTQuery(rag=True)

session = Whatsapp()

NOTIFIED = read_file_list("lists/notified.txt")

DELAY = 86400  # 1 day


def main():
    while True:
        birthdays = [
            item["p.name"]
            for item in rag.query_database(
                "MATCH (p:Family) WHERE split(p.birthday, '-')[0] = toString(date().day) AND split(p.birthday, '-')[1] = toString(date().month) RETURN p.name"
            )
        ]
        if len(birthdays) == 1:
            message = f"C'est l'anniversaire de {birthdays[0]} aujourd'hui ! Joyeux anniversaire !"
        elif len(birthdays) > 1:
            message = f"C'est l'anniversaire de {birthdays[0]}, "
            print("1 : ", message)
            for i in range(1, len(birthdays) - 1):
                message += f"{birthdays[i]}, "
                print(i, ":", message)
            message = (
                message[:-2]
                + f" et {birthdays[-1]} aujourd'hui ! Joyeux anniversaire !"
            )

        if len(birthdays) > 0:
            for number in NOTIFIED:
                print(message)
                session.send_message(id=number, message=message)
        time.sleep(DELAY)


if __name__ == "__main__":
    main()
