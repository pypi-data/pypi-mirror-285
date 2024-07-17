import os
from sendgrid import SendGridAPIClient, TemplateId
from sendgrid.helpers.mail import Mail

env_keys_exist = False
try:
    SENDGRID_API_KEY = os.environ['SENDGRID_API_KEY']
    env_keys_exist = True
except Exception:
    raise Exception("add SENDGRID_API_KEY to env")


class SendgridHelpers:
    @classmethod
    def send_email(cls, from_email: str, to_email: list[str] | str, subject: str = None, content: str = None, template_id: str = None, dynamic_template_data: dict = None) -> bool:
        if template_id:
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=content
            )
            message.template_id = TemplateId(template_id=template_id)
            message.dynamic_template_data = dynamic_template_data
        else:
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=content
            )

        # send email
        try:
            sg = SendGridAPIClient(SENDGRID_API_KEY)
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False
