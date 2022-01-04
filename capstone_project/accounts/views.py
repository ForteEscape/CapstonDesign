"""
accounts/views.py

계정(user data) 관련 처리 앱 view
로그인, 로그아웃, 회원가입의 처리를 실시합니다.

#1
현재 user = authenticate(request, email=email, password=password) 코드는 기존 User 모델을 사용하며
이로 인하여 로그인 시 User 모델에 등록된 username과 password를 이용하여 로그인을 하는 동작을 취함
따라서 이를 해결하기 위해서 custom User 모델을 구현하고, authenticate 함수를 재정의하여 id와 password를
이용하여 로그인 가능하게 수정해야 함

2022-01-04 01:38 AM
#1 이슈 User 모델 재정의로 해결함

2022-01-04 19:35 PM
#3 이슈(https://github.com/ForteEscape/CapstonDesign/issues/3#issue-1093208587 참조)
E-mail 중복 확인 및 로그인 실패 시 사유 알람 구현
"""

from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth import login, authenticate
from .models import User


# Create your views here.
def signin(request):
    """
    :param request: log in에 필요한 input data(user id, password)
    :return: 로그인 성공 시 index로 리다이랙트 반환
    """

    if request.method == 'POST':
        username = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            messages.error(request, 'E-mail 또는 비밀번호가 틀립니다.')
            return render(request, 'accounts/login.html')

    return render(request, 'accounts/login.html')


def logout(request):
    auth.logout(request)
    return redirect('/')


def signup(request):
    """
    :param request: 회원가입 요청 데이터(회원 id, 이름, password)
    :return: 회원가입 완료 시 index 리다이렉트 아닐 시 해당 페이지 return
    """

    if request.method == 'POST':
        if request.POST['user-password'] == request.POST['user-confirm-pw']:

            # 사용자 id가 이미 존재하는 경우를 검사
            if User.objects.filter(email=request.POST['user-email']).exists():
                messages.error(request, '이미 존재하는 E-mail 입니다.')
                return render(request, 'accounts/signup.html')

            user = User.objects.create_user(
                username=request.POST['user-name'],
                email=request.POST['user-email'],
                password=request.POST['user-password']
            )
            user.save()

            return redirect('/')
        else:
            messages.error(request, '비밀번호가 서로 다릅니다.')
            return render(request, 'accounts/signup.html')
    return render(request, 'accounts/signup.html')

