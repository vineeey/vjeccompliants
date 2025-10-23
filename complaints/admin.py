from __future__ import annotations

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Complaint, ComplaintAttachment, Department, CategoryDepartmentMapping, DepartmentMembership


class ComplaintAttachmentInline(admin.TabularInline):
    model = ComplaintAttachment
    extra = 0
    readonly_fields = ("uploaded_at", "mime_type")


def export_as_csv(modeladmin, request, queryset):
    """Re-add CSV export (if previously removed)."""
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="complaints.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "id", "title", "description", "created_by", "anonymous",
        "department", "status", "category", "priority", "summary",
        "model_version", "confidence", "created_at", "updated_at",
    ])
    for obj in queryset:
        writer.writerow([
            obj.id, obj.title, obj.description, getattr(obj.created_by, "username", ""),
            obj.anonymous, getattr(obj.department, "name", ""), obj.status, obj.category,
            obj.priority, obj.summary, obj.model_version, obj.confidence,
            obj.created_at.isoformat(), obj.updated_at.isoformat(),
        ])
    return response


def export_as_json(modeladmin, request, queryset):
    import json
    from django.http import HttpResponse

    data = []
    for obj in queryset:
        data.append({
            "id": obj.id,
            "title": obj.title,
            "description": obj.description,
            "created_by": getattr(obj.created_by, "username", None),
            "anonymous": obj.anonymous,
            "department": getattr(obj.department, "name", None),
            "status": obj.status,
            "category": obj.category,
            "priority": obj.priority,
            "summary": obj.summary,
            "model_version": obj.model_version,
            "confidence": obj.confidence,
            "created_at": obj.created_at.isoformat(),
            "updated_at": obj.updated_at.isoformat(),
        })
    response = HttpResponse(json.dumps(data, indent=2), content_type="application/json")
    response["Content-Disposition"] = 'attachment; filename="complaints.json"'
    return response


def export_as_pdf(modeladmin, request, queryset):
        """Optional PDF export via WeasyPrint; if unavailable, inform the user."""
        try:
                from weasyprint import HTML, CSS  # type: ignore
        except Exception:
                modeladmin.message_user(request, "WeasyPrint is not installed. Install 'weasyprint' to enable PDF export.")
                return None

        from django.http import HttpResponse

        # Render a simple HTML with basic styling (constructed inline to avoid templates)
        # Build HTML manually to avoid requiring a template file
        rows = []
        for obj in queryset:
            desc_html = (obj.description or "").replace("\n", "<br/>")
            summ_html = (obj.summary or "").replace("\n", "<br/>")
            rows.append(f"""
            <section class='card'>
                <h2>#{obj.id} - {obj.title}</h2>
                <p><strong>Status:</strong> {obj.status} | <strong>Priority:</strong> {obj.priority} | <strong>Category:</strong> {obj.category or '-'} | <strong>Dept:</strong> {getattr(obj.department, 'name', '-')}
                <br><strong>Anonymous:</strong> {obj.anonymous} | <strong>By:</strong> {getattr(obj.created_by, 'username', '-')}</p>
                <p><strong>Created:</strong> {obj.created_at.strftime('%Y-%m-%d %H:%M')} | <strong>Updated:</strong> {obj.updated_at.strftime('%Y-%m-%d %H:%M')}</p>
                <h3>Description</h3>
                <p>{desc_html}</p>
                <h3>Summary</h3>
                <p>{summ_html}</p>
            </section>
            <hr/>
            """)

        full_html = f"""
        <html>
        <head>
            <meta charset='utf-8'/>
            <style>
                body {{ font-family: Arial, sans-serif; font-size: 12px; }}
                h1 {{ text-align: center; }}
                .card {{ page-break-inside: avoid; margin-bottom: 12px; }}
                hr {{ border: 0; border-top: 1px solid #ccc; margin: 16px 0; }}
            </style>
        </head>
        <body>
            <h1>Complaints Export</h1>
            {''.join(rows)}
        </body>
        </html>
        """

        pdf = HTML(string=full_html).write_pdf()
        response = HttpResponse(pdf, content_type="application/pdf")
        response["Content-Disposition"] = 'attachment; filename="complaints.pdf"'
        return response


def generate_reply_draft(modeladmin, request, queryset):
    """Admin action: generate simple reply drafts for selected complaints."""
    count = 0
    for obj in queryset:
        if not obj.reply_draft:
            greeting = "Hello,"
            if getattr(obj.created_by, "first_name", ""):
                greeting = f"Hello {obj.created_by.first_name},"
            obj.reply_draft = (
                f"{greeting}\n\n"
                f"We have received your complaint titled '{obj.title}'. Our team is reviewing it and will update the status from '{obj.status}' as soon as possible.\n\n"
                f"Summary: {obj.summary or '(pending)'}\n"
                f"Category: {obj.category or '(pending)'} | Priority: {obj.priority or '(pending)'}\n\n"
                f"Thank you for your patience.\n"
            )
            obj.save(update_fields=["reply_draft"])
            count += 1
    modeladmin.message_user(request, f"Reply drafts generated for {count} complaints.")


export_as_csv.short_description = "Export selected complaints as CSV"
export_as_json.short_description = "Export selected complaints as JSON"
export_as_pdf.short_description = "Export selected complaints as PDF (WeasyPrint)"
generate_reply_draft.short_description = "Generate reply draft"


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(CategoryDepartmentMapping)
class CategoryDepartmentMappingAdmin(admin.ModelAdmin):
    list_display = ("category", "department")
    search_fields = ("category", "department__name")


@admin.register(Complaint)
class ComplaintAdmin(SimpleHistoryAdmin):
    list_display = ("id", "title", "status", "priority", "category", "department", "assigned_to", "anonymous", "created_by", "created_at")
    list_filter = ("status", "priority", "category", "department", "assigned_to", "anonymous", "created_at")
    search_fields = ("title", "description", "summary", "category")
    inlines = [ComplaintAttachmentInline]
    readonly_fields = ("model_version", "confidence", "summary", "created_at", "updated_at", "reply_draft")
    actions = [export_as_csv, export_as_json, export_as_pdf, generate_reply_draft]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # Filter by department memberships if any
        dept_ids = list(DepartmentMembership.objects.filter(user=request.user).values_list("department_id", flat=True))
        if dept_ids:
            return qs.filter(department_id__in=dept_ids)
        return qs


@admin.register(DepartmentMembership)
class DepartmentMembershipAdmin(admin.ModelAdmin):
    list_display = ("user", "department", "role")
    list_filter = ("role", "department")
    search_fields = ("user__username", "department__name")