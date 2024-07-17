from django_axe import settings
from django.template.loader import render_to_string
import logging

logger = logging.getLogger("django_axe")


class DjangoAxeScriptMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        # Check if the response has 'text/html' content type
        if "text/html" in response.get("Content-Type", "") and not request.META.get(
            "axe_ignore"
        ):
            try:
                html = response.content.decode("utf-8")
                script = render_to_string(
                    request=request,
                    template_name="django_axe/script.html",
                    context={"settings": settings},
                )
                closing_body_tag_index = html.rfind("</body>")
                if closing_body_tag_index != -1:
                    # Insert script before </body> tag
                    html = (
                        html[:closing_body_tag_index]
                        + script
                        + html[closing_body_tag_index:]
                    )
                    response.content = html.encode("utf-8")
                    # Update 'Content-Length' header, if it exists
                    if "Content-Length" in response:
                        response["Content-Length"] = str(len(response.content))
            except Exception as e:
                logger.info(f"Error while injecting axe script: {e}")
        return response
