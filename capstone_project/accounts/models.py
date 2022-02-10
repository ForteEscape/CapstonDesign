"""
models.py

해당 스크립트는 로그인, 회원가입에 사용할 사용자 DB를 정의합니다.

Python Django에서 사용하는 User 모델을 재정의하여 사용하며 구성은 다음과 같습니다.

1. UserManager(BaseUserManager)
UserManager 클래스는 Django 빌트인 User 클래스에서 기능을 담당하는 클래스로
DB에 넣을 데이터를 생성하고 추가하는 기능을 담당합니다.

2. User
User는 사용자 DB table schema 코드로 표현한 것으로 회원가입에 사용할
데이터 및 기본 키, 외부 키를 정의합니다.

2022-01-04 원래 사용 중이던 Django 자체 User 모델을 수정하여 사용함
"""

from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser


# Create your models here.
class UserManager(BaseUserManager):
    """
    User의 기능을 담당하는 User의 Helper Class
    """
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('이메일은 회원가입 필수 요소입니다.')

        user = self.model(
            email=self.normalize_email(email),
            username=username
        )

        user.set_password(password)
        user.save(using=self.db)

        return user

    def create_superuser(self, username, email, password):
        user = self.create_user(
            username=username,
            email=email,
            password=password
        )

        user.is_admin = True
        user.save(using=self.db)

        return user


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='email',
        max_length=255,
        unique=True,
    )

    username = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = UserManager()

    # 해당 코드로 email이 로그인에 사용되도록 설정, username의 경우 부가적으로 넣을 수 있도록 설정
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class CompanySearch(models.Model):
    email = models.ForeignKey('User', on_delete=models.CASCADE, related_name='user_email')
    company_name = models.CharField(max_length=300, null=True)
    search_count = models.IntegerField(null=True)

    objects = models.Manager()

    class Meta:
        db_table = 'company'

