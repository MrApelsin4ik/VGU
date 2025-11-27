from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class CustomUserManager(BaseUserManager):
    def create_user(self, email, username='', password=None):
        if not email:
            raise ValueError("Email обязателен")


        email = self.normalize_email(email)
        user = self.model(email=email, username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username='', password=None):
        user = self.create_user(email, username, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=False, blank=True, default='')
    full_name = models.CharField(max_length=70, blank=True, default='')
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)


    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        return self.username



class Section(models.Model):
    """
    Разделы и подразделы (рекурсивная иерархия).
    """

    class SectionType(models.TextChoices):
        MAIN = "main", "Главное"
        NEWS = "news", "Новости"
        ANNOUNCEMENT = "announcement", "Объявления"

    title = models.CharField("Название раздела", max_length=255)
    parent = models.ForeignKey(
        "self",
        verbose_name="Родительский раздел",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    section_type = models.CharField(
        "Принадлежность",
        max_length=20,
        choices=SectionType.choices,
        default=SectionType.MAIN,
    )


    class Meta:
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"

    def __str__(self):
        return self.title


class News(models.Model):
    """
    Новость: тема, краткое описание + изображения, подробное описание (текст + base64-изображения),
    прикреплённые файлы, привязка к разделу/подразделу.
    """

    section = models.ForeignKey(
        Section,
        verbose_name="Раздел",
        on_delete=models.PROTECT,
        related_name="news",
    )
    title = models.CharField("Тема", max_length=255)


    short_description = models.TextField("Краткое описание")


    body = models.TextField()

    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата изменения", auto_now=True)
    is_published = models.BooleanField("Опубликовано", default=True)

    class Meta:
        verbose_name = "Новость"
        verbose_name_plural = "Новости"
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class NewsImage(models.Model):
    """
    Изображения, привязанные к новости (для краткого описания/превью и т.п.).
    """

    news = models.ForeignKey(
        News,
        verbose_name="Новость",
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        "Изображение",
        upload_to="news/images/",
    )
    is_preview = models.BooleanField(
        "Использовать как превью",
        default=False,
    )
    sort_order = models.PositiveIntegerField(
        "Порядок",
        default=0,
    )

    class Meta:
        verbose_name = "Изображение новости"
        verbose_name_plural = "Изображения новостей"
        ordering = ("sort_order", "id")

    def __str__(self):
        return f"Изображение для: {self.news.title}"


class NewsAttachment(models.Model):
    """
    Файлы, прикреплённые к новости
    """

    news = models.ForeignKey(
        News,
        verbose_name="Новость",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(
        "Файл",
        upload_to="news/attachments/",
    )
    original_name = models.CharField(
        "Оригинальное имя файла",
        max_length=255,
        blank=True,
    )

    class Meta:
        verbose_name = "Файл новости"
        verbose_name_plural = "Файлы новостей"

    def __str__(self):
        return self.original_name or self.file.name


class Announcement(models.Model):
    """
    Объявление: тема, описание + изображения + файлы, ссылка для перехода.
    """

    section = models.ForeignKey(
        Section,
        verbose_name="Раздел",
        on_delete=models.PROTECT,
        related_name="announcements",
        null=True,
        blank=True,

    )
    title = models.CharField("Тема", max_length=255)


    body = models.TextField(
        "Описание",

    )


    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Дата изменения", auto_now=True)
    is_active = models.BooleanField("Активно", default=True)

    class Meta:
        verbose_name = "Объявление"
        verbose_name_plural = "Объявления"
        ordering = ("-created_at",)

    def __str__(self):
        return self.title


class AnnouncementImage(models.Model):
    """
    Изображения, привязанные к объявлению.
    """

    announcement = models.ForeignKey(
        Announcement,
        verbose_name="Объявление",
        on_delete=models.CASCADE,
        related_name="images",
    )
    image = models.ImageField(
        "Изображение",
        upload_to="announcements/images/",
    )
    sort_order = models.PositiveIntegerField("Порядок", default=0)

    class Meta:
        verbose_name = "Изображение объявления"
        verbose_name_plural = "Изображения объявлений"
        ordering = ("sort_order", "id")

    def __str__(self):
        return f"Изображение для: {self.announcement.title}"


class AnnouncementAttachment(models.Model):
    """
    Файлы, прикреплённые к объявлению.
    """

    announcement = models.ForeignKey(
        Announcement,
        verbose_name="Объявление",
        on_delete=models.CASCADE,
        related_name="attachments",
    )
    file = models.FileField(
        "Файл",
        upload_to="announcements/attachments/",
    )
    original_name = models.CharField(
        "Оригинальное имя файла",
        max_length=255,
        blank=True,
    )

    class Meta:
        verbose_name = "Файл объявления"
        verbose_name_plural = "Файлы объявлений"

    def __str__(self):
        return self.original_name or self.file.name



