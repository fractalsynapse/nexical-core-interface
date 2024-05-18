from app.api import views

from . import models

views.generate(
    models.Feedback,
    filter_fields={
        "id": "id",
        "created": "date_time",
        "path": "short_text",
        "rating": "number",
        "message": "long_text",
        "user__email": "short_text",
        "user__first_name": "short_text",
        "user__last_name": "short_text",
    },
    ordering=["-created"],
)
