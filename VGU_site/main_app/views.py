# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_GET
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect
from .models import Section, News, NewsImage, NewsAttachment, Announcement
from django.contrib.auth import authenticate, login, logout
from django.urls import reverse

def admin_login(request):
    error = ""
    if request.user.is_authenticated:
        # Уже залогинен
        if request.user.is_staff:
            return redirect(reverse("admin_news_create"))
        else:
            # На всякий случай вылогиним, чтобы не путаться
            logout(request)

    if request.method == "POST":
        email = (request.POST.get("email") or "").strip().lower()
        password = request.POST.get("password") or ""

        # Важно: ModelBackend ожидает параметр username,
        # но внутри использует USERNAME_FIELD = "email"
        user = authenticate(request, username=email, password=password)

        if user is None:
            error = "Неверный email или пароль."
        else:
            if not user.is_staff:
                error = "У вас нет прав администратора."
            else:
                login(request, user)
                return redirect(reverse("admin_news_create"))

    return render(request, "admin/admin_login.html", {"error": error})


@require_GET
def main_page(request):

    news_qs = News.objects.filter(is_published=True)
    announcements_sidebar = Announcement.objects.filter(is_active=True)[:15]

    context = {
        "news_list": news_qs[:20],
        "announcements_sidebar": announcements_sidebar,
    }
    return render(request, "main.html", context)


@require_GET
def search(request):
    query = request.GET.get("q", "").strip()

    if not query:
        return JsonResponse({"news": [], "announcements": []})

    news_qs = News.objects.filter(is_published=True).filter(
        Q(title__icontains=query)
        | Q(short_description__icontains=query)
        | Q(body__icontains=query)
    )[:10]

    ann_qs = Announcement.objects.filter(is_active=True).filter(
        Q(title__icontains=query) | Q(body__icontains=query)
    )[:10]

    data = {
        "news": [
            {
                "id": n.id,
                "title": n.title,
                "short_description": (
                    (n.short_description[:150] + "...")
                    if len(n.short_description) > 150
                    else n.short_description
                ),
            }
            for n in news_qs
        ],
        "announcements": [
            {
                "id": a.id,
                "title": a.title,
                "body": (a.body[:150] + "...") if len(a.body) > 150 else a.body,
            }
            for a in ann_qs
        ],
    }
    return JsonResponse(data)



@require_GET
def news_detail(request, pk: int):
    news = get_object_or_404(News, pk=pk, is_published=True)
    return render(request, "news_detail.html", {"news": news})


@require_GET
def announcement_detail(request, pk: int):
    announcement = get_object_or_404(Announcement, pk=pk, is_active=True)
    return render(request, "announcement_detail.html", {"announcement": announcement})






def staff_required(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(staff_required)
def admin_news_create(request):

    sections = Section.objects.all().order_by("title")
    errors = {}
    old = {}
    success = False

    if request.method == "POST":
        section_id = request.POST.get("section")
        title = (request.POST.get("title") or "").strip()
        short_description = (request.POST.get("short_description") or "").strip()
        body = (request.POST.get("body") or "").strip()
        is_published = request.POST.get("is_published") == "on"


        old = {
            "section": section_id,
            "title": title,
            "short_description": short_description,
            "body": body,
            "is_published": is_published,
        }


        section = None
        if not section_id:
            errors["section"] = "Выберите раздел."
        else:
            try:
                section = Section.objects.get(pk=section_id)
            except Section.DoesNotExist:
                errors["section"] = "Выбранный раздел не найден."

        if not title:
            errors["title"] = "Укажите тему новости."
        if not short_description:
            errors["short_description"] = "Заполните краткое описание."
        if not body:
            errors["body"] = "Заполните текст новости."

        if not errors:

            news = News.objects.create(
                section=section,
                title=title,
                short_description=short_description,
                body=body,
                is_published=is_published,
            )


            images = request.FILES.getlist("images")
            for idx, img in enumerate(images):
                NewsImage.objects.create(
                    news=news,
                    image=img,
                    is_preview=(idx == 0),
                    sort_order=idx,
                )


            attachments = request.FILES.getlist("attachments")
            for f in attachments:
                NewsAttachment.objects.create(
                    news=news,
                    file=f,
                    original_name=f.name,
                )

            success = True
            errors = {}
            old = {}  # очищаем форму

    context = {
        "sections": sections,
        "errors": errors,
        "old": old,
        "success": success,
    }
    return render(request, "admin/news_create.html", context)