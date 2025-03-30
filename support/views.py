from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import ContactForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            # Save the support request
            support_request = form.save()
            support_request.email = request.user.email if request.user.is_authenticated else form.cleaned_data["email"]
            support_request.save()
            # Send email notification
            try:
                send_support_notification(support_request)
                messages.success(
                    request, "Your message has been sent. We'll get back to you soon!"
                )
            except Exception as e:
                # Log the error but don't show the technical details to the user
                print(f"Error sending email: {e}")
                messages.success(
                    request,
                    "Your message has been received, but there was an issue with the email notification. Our team has been notified.",
                )

            return redirect("contact_success")
        else:
            messages.error(request, "Please correct the errors below.")
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return render(
                request,
                "support/contact.html",
                {"form": form},
            )
    else:
        form = ContactForm()

    return render(request, "support/contact.html", {"form": form})


def contact_success_view(request):
    """Success page after submitting contact form"""
    return render(request, "support/contact_success.html")


def send_support_notification(support_request):
    """Send email notification for new support requests"""
    subject = f"New Support Request: {support_request.subject}"

    # Prepare context for templates
    context = {
        "support_request": support_request,
        "admin_url": (
            f"{settings.SITE_URL}/admin/support/supportrequest/{support_request.id}/change/"
            if hasattr(settings, "SITE_URL")
            else None
        ),
    }

    # Render email templates
    html_content = render_to_string(
        "support/email_templates/support_request.html", context
    )
    text_content = render_to_string(
        "support/email_templates/support_request.txt", context
    )

    # Create email message
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=["support@aassist.ai"],
        reply_to=[support_request.email],
    )

    # Attach HTML content
    email.attach_alternative(html_content, "text/html")

    # Send email
    email.send()
