from django.core import mail

def send_sub_notification(email, comment):
    try:
        if comment != '':
            subject = f"[САЙТ: пользователь оставил комментарий]"
        else:
            subject = f"[САЙТ: пользователь подписался на рассылку]"
        mail.send_mail(
            subject=subject,
            message=f"Подписчик: {email}\r\n\nКомментарий: '{comment}'",
            from_email=email,
            recipient_list=['kmu@cosmos.ru'],
            fail_silently=False
        )
    except Exception as e:
        print(e)

def send_unsub_notification(email):
    try:
        mail.send_mail(
            subject="[САЙТ: пользователь отказался от рассылки]",
            message=f"Подписчик '{email}' отписался",
            from_email=email,
            recipient_list=['kmu@cosmos.ru'],
            fail_silently=False
        )
    except Exception as e:
        print(e)

def send_email(subscriber):
    html_content = f"<html><body>\
    <div>Спасибо, что подписались на рассылку Конференции молодых учёных ИКИ РАН!</div><br>\
    <div>Мы сообщим вам об открытии регистрации на КМУ 2026. Если у вас есть вопросы — вы можете задать их в ответном письме.</div><br>\
    <div>Чтобы отписаться от рассылки, <a href='https://kmu.cosmos.ru/unsubscribe/{subscriber.id}/'>перейдите по ссылке</a>.</div><br>\
    <div>С уважением,</div>\
    <div>Оргкомитет КМУ 2026</div>\
    </body></html>"

    try:
        msg = mail.EmailMessage("КМУ 2026: Подписка на рассылку", html_content, from_email='kmu@cosmos.ru')
        msg.content_subtype = "html"
        msg.to = [subscriber.email]
        msg.send(fail_silently=False)

    except Exception as e:
        print(e)
