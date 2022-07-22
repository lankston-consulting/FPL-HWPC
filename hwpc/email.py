import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Mail,
    Attachment,
    FileContent,
    FileName,
    FileType,
    Disposition,
    ContentId,
)
from hwpc import model_data
from config import gch
from hwpc.names import Names as nm


class Email:
    def __init__(self) -> None:
        super().__init__()

    def send_email(self, user_email):

        message = Mail(
            from_email="contact@lankstonconsulting.com",
            to_emails=user_email,
            subject="Hwpcarbon Run Results",
            html_content="<p>Thank you user, your Hwpcarbon simulation is complete and is ready to be downloaded. To recieve your files, click the link below.</p><br>"
            + "<a href ="
            + "https://storage.googleapis.com/hwpcarbon-data/"
            + nm.Output.output_path
            + "/results/"
            + nm.Output.run_name
            + ".zip>Download</a><br>"
            + "<p>Your link will remain active for 30 days, please make sure to save your data before then, as the download cannot be repeated once the time is up.</p>",
        )

        try:
            sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)
