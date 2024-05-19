from django.template.loader import render_to_string


def render_link(text, url, classes=None, target=None):
    classes = f"class='{classes}'" if classes else ""
    target = f"target='{target}'" if target else ""
    return f"<a href='{url}' {target} {classes}>{text}</a>"


def render_table(data, id=None, classes=None, names=None):
    return render_to_string("components/flex_table.html", {"names": names, "data": data, "id": id, "classes": classes})
