# from app.api import permissions, views

# from . import models

#
# Model Endpoints
#
# views.generate(
#     models.Message,
#     permission_classes=[permissions.OutreachPermissions],
#     filter_fields={
#         "id": "id",
#         "created": "date_time",
#         "updated": "date_time",
#         "contact__organization__name": "short_text",
#         "contact__organization__link": "link",
#         "contact__organization__description": "long_text",
#         "contact__organization__employees": "number",
#         "contact__organization__industry": "short_text",
#         "contact__organization__revenue": "number",
#         "contact__organization__total_funding": "number",
#         "contact__organization__last_funding_stage": "short_text",
#         "contact__organization__last_funding": "number",
#         "contact__organization__last_raised_at": "date",
#         "contact__first_name": "short_text",
#         "contact__last_name": "short_text",
#         "contact__email": "link",
#         "contact__phone": "short_text",
#         "contact__city": "short_text",
#         "contact__province": "short_text",
#         "contact__country": "short_text",
#         "contact__title": "short_text",
#         "contact__seniority": "short_text",
#         "contact__linkedin": "link",
#     },
#     ordering_fields=["-created"],
#     search_fields=[
#         "contact__organization__name",
#         "contact__organization__link",
#         "contact__organization__description",
#         "contact__organization__industry",
#         "contact__title",
#         "contact__first_name",
#         "contact__last_name",
#         "contact__email",
#         "contact__phone",
#         "contact__city",
#         "contact__province",
#         "contact__country",
#         "contact__seniority",
#     ],
#     view_fields=[
#         "id",
#         "created",
#         "updated",
#         "subject",
#         "body",
#         "sent",
#         "failed",
#         "skipped"
#     ],
#     save_fields=[
#         "subject",
#         "body",
#         "sent",
#         "failed",
#         "skipped"
#     ],
#     relation_fields=["campaign", "contact"],
# )
