import uuid

from django.contrib.auth.models import AbstractUser, UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class Entity(models.Model):
    class Meta:
        abstract = True

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(editable=False, auto_now_add=True)
    updated = models.DateTimeField(editable=False, auto_now=True)


class CustomUserManager(UserManager):
    def get_by_natural_key(self, username):
        case_insensitive_username_field = '{}__iexact'.format(self.model.USERNAME_FIELD)
        return self.get(**{case_insensitive_username_field: username})

    def create_user(self, first_name, last_name, email, password=None):
        if not email:
            raise ValueError('user must have email')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.row_password = password
        user.first_name = first_name
        user.last_name = last_name
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        if not email:
            raise ValueError('user must have email')

        user = self.model(
            email=self.normalize_email(email),
        )
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser, Entity):
    username = models.NOT_PROVIDED
    language = models.BooleanField('language', default=True)
    email = models.EmailField(_('email address'), unique=True)
    row_password = models.TextField(max_length=255, blank=True, null=True)
    massageText = models.TextField('نص رسالة المعايدة', null=True, blank=True, default=' ')

    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = CustomUserManager()

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return self.is_superuser

    def has_module_perms(self, app_label):
        return True


class Customer(models.Model):
    user = models.ForeignKey(User, verbose_name='user', related_name='customer', on_delete=models.CASCADE)
    email = models.EmailField('الايميل', max_length=255, null=True, blank=True)
    name = models.CharField('الاسم ', max_length=255)
    birthday = models.DateTimeField('يوم الميلاد')
    gender = models.CharField('الجنس ', max_length=1, null=True, blank=True)
    phone_number = models.CharField('رقم الهاتف', max_length=11, null=True, blank=True)
    telegram_id = models.CharField('معرف التليكرام', max_length=255, null=True, blank=True)

    # created = models.DateTimeField(editable=False, auto_now_add=True)

    def __str__(self):
        return f"{self.name} {self.email}"
