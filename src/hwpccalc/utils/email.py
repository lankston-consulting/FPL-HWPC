import os

# import base64
import boto3
from botocore.exceptions import ClientError
from hwpccalc.hwpc import names


class Email(object):
    # def __init__(self) -> None:
    #     super().__init__()
    #     json = nm.Output.scenario_info
    #     print(json)

    @staticmethod
    def send_email():
        # Replace sender@example.com with your "From" address.
        # This address must be verified with Amazon SES.
        SENDER = "contact@lankstonconsulting.com"

        # Replace recipient@example.com with a "To" address. If your account
        # is still in the sandbox, this address must be verified.
        print(names.Names.Output.scenario_info["email"])
        RECIPIENT = names.Names.Output.scenario_info["email"]

        # Specify a configuration set. If you do not want to use a configuration
        # set, comment the following variable, and the
        # ConfigurationSetName=CONFIGURATION_SET argument below.
        # CONFIGURATION_SET = "ConfigSet"

        # If necessary, replace us-west-2 with the AWS Region you're using for Amazon SES.
        AWS_REGION = "us-west-2"

        # The subject line for the email.
        SUBJECT = "HWPCarbon Results"
        link_url = (
            "<a href='https://www.hwpcarbon.com/output?p="
            + names.Names.Output.scenario_info["user_string"]
            + "&q="
            + names.Names.Output.scenario_info["scenario_name"]
            + "'>Your Results</a>"
        )

        # The email body for recipients with non-HTML email clients.
        BODY_TEXT = link_url

        # The HTML body of the email.
        BODY_HTML = (
            """<html>
        <head></head>
        <body>
        <h1>Thank you user, your Hwpcarbon simulation is complete and is ready to be downloaded. To recieve your files, click the link below.</h1>
        """
            + link_url
            + """
        <p>This email was sent with
            <a href='https://aws.amazon.com/ses/'>Amazon SES</a> using the
            <a href='https://aws.amazon.com/sdk-for-python/'>
            AWS SDK for Python (Boto)</a>.</p>
        </body>
        </html>
                    """
        )

        # The character encoding for the email.
        CHARSET = "UTF-8"

        # Create a new SES resource and specify a region.
        client = boto3.client("ses", region_name=AWS_REGION)

        # Try to send the email.
        try:
            # Provide the contents of the email.
            response = client.send_email(
                Destination={
                    "ToAddresses": [
                        RECIPIENT,
                    ],
                },
                Message={
                    "Body": {
                        "Html": {
                            "Charset": CHARSET,
                            "Data": BODY_HTML,
                        },
                        "Text": {
                            "Charset": CHARSET,
                            "Data": BODY_TEXT,
                        },
                    },
                    "Subject": {
                        "Charset": CHARSET,
                        "Data": SUBJECT,
                    },
                },
                Source=SENDER,
                # If you are not using a configuration set, comment or delete the
                # following line
                # ConfigurationSetName=CONFIGURATION_SET,
            )
        # Display an error if something goes wrong.
        except ClientError as e:
            print(e.response["Error"]["Message"])
        else:
            print("Email sent! Message ID:"),
            print(response["MessageId"])
    

#     def send_email(self, user_email):

#         message = Mail(
#             from_email="contact@lankstonconsulting.com",
#             to_emails=user_email,
#             subject="Hwpcarbon Run Results",
#             html_content="<p>Thank you user, your Hwpcarbon simulation is complete and is ready to be downloaded. To recieve your files, click the link below.</p><br>"
#             + "<a href ="
#             + "https://storage.googleapis.com/hwpcarbon-data/"
#             + nm.Output.output_path
#             + "/results/"
#             + nm.Output.run_name
#             + ".zip>Download</a><br>"
#             + "<p>Your link will remain active for 30 days, please make sure to save your data before then, as the download cannot be repeated once the time is up.</p>",
#         )

#         try:
#             sg = SendGridAPIClient(os.environ.get("SENDGRID_API_KEY"))
#             response = sg.send(message)
#             print(response.status_code)
#             print(response.body)
#             print(response.headers)
#         except Exception as e:
#             print(e.message)
