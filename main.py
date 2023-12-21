import csv
import os
import smtplib
import threading
from email.message import EmailMessage

import requests

from passwords import password


def images():
    folder_path = "peoples"
    os.makedirs(folder_path, exist_ok=True)

    genders = ["men", "women"]

    for gender in genders:
        for i in range(1, 101):
            image_url = f"https://randomuser.me/api/portraits/{gender}/{i}.jpg"
            image_filename = f"{folder_path}/{gender}_{i}.jpg"

            try:
                response = requests.get(image_url)
                response.raise_for_status()

                with open(image_filename, "wb") as image_file:
                    image_file.write(response.content)
                print(f"{gender} {i} rasm saqlandi.")
            except requests.exceptions.RequestException as e:
                print(f"{gender} {i} rasmni yuklab bolmadi. Xatolik: {e}")

    print("Barcha rasmlar yuklandi.")


def send_email_function(send_email, reciever_emails, password, subject, content_urls):
    server = "smtp.gmail.com"
    msg = EmailMessage()
    msg["From"] = send_email
    msg["To"] = reciever_emails
    msg["Subject"] = subject

    for file in content_urls:
        with open(file, "rb") as f:
            msg.add_attachment(f.read(), maintype="image", subtype="jpeg", filename=f.name.split("/")[-1])

    with smtplib.SMTP_SSL(server, 465) as server:
        server.login(send_email, password)
        server.send_message(msg)
        print("Xabar jo'natildi :) {0}".format(" ".join(reciever_emails)))


def send_email():
    os.chdir("peoples")

    images = [os.path.abspath(file) for file in os.listdir()]

    os.chdir("..")

    with open("emails.csv", "r") as f:
        reader = csv.DictReader(f)
        emails = [row['email'].strip() for row in reader]
    send_email_function(send_email="hakimjonovjahongir0@gmail.com", password=password, reciever_emails=emails,
                        subject="Yangi rasmlar", content_urls=images)


if __name__ == '__main__':
    thread = threading.Thread(target=images)
    thread.start()
    thread.join()
    send_email()
