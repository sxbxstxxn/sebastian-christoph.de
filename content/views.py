from django.conf import settings
from django.contrib import messages
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render

from .forms import ContactForm


def page_not_found(request, exception):
    return render(request, "404.html", status=404)


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)

        if form.is_valid():
            name = form.cleaned_data["name"]
            email = form.cleaned_data["email"]
            message = form.cleaned_data["message"]
            recipient = settings.CONTACT_EMAIL

            if not recipient:
                form.add_error(None, "Das Kontaktformular ist noch nicht vollstaendig konfiguriert.")
            else:
                email_message = EmailMessage(
                    subject=f"Kontaktanfrage von {name}",
                    body=(
                        f"Name: {name}\n"
                        f"E-Mail: {email}\n\n"
                        f"Nachricht:\n{message}"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[recipient],
                    reply_to=[email],
                )
                email_message.send(fail_silently=False)
                messages.success(request, "Danke, deine Nachricht wurde gesendet.")
                return redirect("contact")
    else:
        form = ContactForm()

    return render(request, "content/contact.html", {"form": form})
