from users.models import AuthLink, AuthCode
from django.core import mail
from django.urls import reverse
from kmu.utils import NOW, year
import datetime as dt
from django.utils.translation import gettext_lazy as _


def send_verification_email(user, html_link):

    html_content = "<html><body><div>" + _("Перейдите по ссылке") + " <a href='" + html_link + "'>" + html_link + "}</a>" + _(", чтобы завершить регистрацию на сайте КМУ ") +"</div></body></html>"

    try:
        msg = mail.EmailMessage(_("КМУ ") + str(year()) + _(": Подтверждение регистрации на сайте"), html_content, from_email='kmu@cosmos.ru')
        msg.content_subtype = "html"
        msg.to = [user.email] 
        msg.send(fail_silently=False)
    except Exception as e:
        print(e)


def send_code_email(user, code):

    html_content = f"<html><body><div>" + _("Ваш код для изменения пароля на сайте КМУ ") + str(year()) + f": <b>{code}</b></div></body></html>"

    try:
        msg = mail.EmailMessage(_("КМУ ") + str(year()) + _(": Изменение пароля на сайте"), html_content, from_email='kmu@cosmos.ru')
        msg.content_subtype = "html"
        msg.to = [user.email] 
        msg.send(fail_silently=False)
    except Exception as e:
        print(e)


def issue_verification(user, request):
    
    # check for less then 24-hour links
    deadline = NOW() + dt.timedelta(hours=24)
    links = user.auth_links.filter(created__lt=deadline)

    if links.count() == 1:
        # send email with it
        send_link = links.first()
    else:
        # remove all associated links
        links = AuthLink.objects.filter(user=user)
        links.delete()
        # create a new one
        send_link = AuthLink(user=user)
        send_link.save()

    html_link = request.build_absolute_uri(reverse('confirm_registration', kwargs={'auth_link_id' : send_link.id}))
    send_verification_email(user, html_link)


def issue_code(user):

    # check for less then 24-hour links
    deadline = NOW() + dt.timedelta(hours=24)
    codes = user.auth_codes.filter(created__lt=deadline)

    if codes.count() == 1:
        send_code = codes.first()
    else:
        codes = AuthCode.objects.filter(user=user)
        codes.delete()
        send_code = AuthCode(user=user)
        send_code.save()

    send_code_email(user, send_code.issue_code())

    return send_code.id


