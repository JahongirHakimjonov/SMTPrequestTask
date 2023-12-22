import asyncio
import csv
import logging
import os
from email.message import EmailMessage

import aiofiles
import aiohttp
from aiosmtplib import SMTP

from passwords import password

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def download_image(session, gender, i):
    folder_path = "peoples"
    os.makedirs(folder_path, exist_ok=True)

    image_url = f"https://randomuser.me/api/portraits/{gender}/{i}.jpg"
    image_filename = os.path.join(folder_path, f"{gender}_{i}.jpg")

    try:
        async with session.get(image_url) as response:
            response.raise_for_status()
            image_content = await response.read()

            async with aiofiles.open(image_filename, "wb") as image_file:
                await image_file.write(image_content)

            logger.info(f"{gender} {i} rasm saqlandi.")
    except aiohttp.ClientError as e:
        logger.error(f"{gender} {i} rasmni yuklab bolmadi. Xatolik: {e}")


async def download_images():
    folder_path = "peoples"
    os.makedirs(folder_path, exist_ok=True)

    genders = ["men", "women"]

    async with aiohttp.ClientSession() as session:
        tasks = [asyncio.create_task(download_image(session, gender, i)) for gender in genders for i in range(1, 100)]
        await asyncio.gather(*tasks)

    logger.info("Barcha rasmlar yuklandi.")


async def send_email_function(send_email, receiver_emails, password, subject, content_urls):
    server = "smtp.gmail.com"
    msg = EmailMessage()
    msg["From"] = send_email
    msg["To"] = receiver_emails
    msg["Subject"] = subject

    for file in content_urls:
        with open(file, "rb") as f:
            file_content = f.read()
            msg.add_attachment(file_content, maintype="image", subtype="jpeg", filename=os.path.basename(file))

    async with SMTP(hostname=server, port=465, use_tls=True) as smtp_server:
        await smtp_server.login(send_email, password)
        await smtp_server.send_message(msg)
        logger.info("Xabar jo'natildi :) {0}".format(" ".join(receiver_emails)))


async def send_email():
    os.chdir("peoples")

    images = [os.path.abspath(file) for file in os.listdir()]

    os.chdir("..")

    try:
        async with aiofiles.open("emails.csv", "r") as f:
            content = await f.read()
            reader = csv.DictReader(content.splitlines())
            emails = [row['emails'].strip() for row in reader]

        await send_email_function(
            send_email="hakimjonovjahongir0@gmail.com",
            password=password,
            receiver_emails=emails,
            subject="Yangi rasmlar",
            content_urls=images
        )
    except FileNotFoundError:
        logger.error("Emails file not found.")
    except Exception as e:
        logger.exception("An unexpected error occurred while reading the emails file: %s", e)


if __name__ == '__main__':
    try:
        asyncio.run(download_images())
        asyncio.run(send_email())
    except Exception as e:
        logger.exception("An unexpected error occurred: %s", e)
