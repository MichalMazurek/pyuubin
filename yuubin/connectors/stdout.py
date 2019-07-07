import html2text

from pyuubin.models import Mail
from pyuubin.templates import Templates


async def send(mail: Mail, templates: Templates) -> str:

    print(f"To: {mail.to}")
    print(f"CC: {mail.cc}")
    print(f"BCC: {mail.bcc}")
    print(f"Subject: {mail.subject}")
    print(f"Template id: {mail.template_id}")
    if mail.template_id:
        print("HTML::")
        html = await templates.render(mail.template_id, mail.parameters)
        print("\n".join(f"\t{line}" for line in html.splitlines()))
        print("TEXT::")
        text = html2text.HTML2Text().handle(html)
        print("\n".join(f"\t{line}" for line in text.splitlines()))
    else:
        print("HTML::")
        print("\n".join(f"\t{line}" for line in templates.html.splitlines()))
        print("TEXT::")
        print(templates.text)
        print("\n".join(f"\t{line}" for line in templates.text.splitlines()))

    print(f"Meta: {mail.meta}")
