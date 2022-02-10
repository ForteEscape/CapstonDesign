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

2022-01-04 21:16 PM
#3 이슈에서 이름 등에 특수 문자가 입력될 시 다시 입력하도록 구현
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import auth, messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import check_password
from .models import User, CompanySearch


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


@login_required(login_url='/accounts/login')
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

            # 특수문자 필터링
            if not request.POST['user-name'].isalpha():
                messages.error(request, '이름에 특수문자 입력은 제한됩니다.')
                return render(request, 'accounts/signup.html')

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
            messages.error(request, '비밀번호가 틀립니다.')
            return render(request, 'accounts/signup.html')

    return render(request, 'accounts/signup.html')


# my page가 불러올 때 CompanySearch 테이블에서 사용자의 검색 기록들을 훑어 가장 많이 검색한 3개 회사를 출력한다.
@login_required(login_url='/accounts/login')
def mypage(request):
    rank_data = CompanySearch.objects.filter(email=request.user).all().order_by('-search_count')

    rank_list = ["None", "None", "None"]
    rank_count_list = [0, 0, 0]
    rank_list_index = 0

    for index in rank_data:
        if rank_list_index >= 3:
            rank_list.append(index.company_name)
            rank_count_list.append(index.search_count)
        else:
            rank_list[rank_list_index] = index.company_name
            rank_count_list[rank_list_index] = index.search_count
            rank_list_index += 1

    return render(request, 'accounts/mypage.html', {
        'first': rank_list[0],
        'second': rank_list[1],
        'third': rank_list[2],
        'label': rank_list,
        'data': rank_count_list,
        'min': 0,
        'max': max(rank_count_list)
    })


@login_required(login_url='/accounts/login')
def pwd_change(request):
    """
    :param request: 비밀번호 변경을 위한 유저 확인용 파라메터
    :return: 비밀번호 변경 성공 시 비밀번호를 변경함과 동시에 로그아웃시켜 home으로 redirect
    """
    if request.method == 'POST':
        current_pwd = request.POST['current_pwd']
        user = request.user

        if check_password(current_pwd, user.password):
            new_pwd = request.POST['new_pwd']
            new_pwd_confirm = request.POST['new_pwd_confirm']

            if new_pwd == new_pwd_confirm:
                user.set_password(new_pwd)
                user.save()

                return redirect('/')
            else:
                messages.error(request, '새 비밀번호의 확인이 잘못되었습니다.')
                return render(request, 'accounts/pwd_change.html')
        else:
            messages.error(request, '기존 비밀번호를 명확히 입력해주세요.')

    return render(request, 'accounts/pwd_change.html')


@login_required(login_url='/accounts/login')
def membership_withdraw(request):
    if request.method == 'POST':
        input_pwd = request.POST['current_pwd']
        user = request.user

        if check_password(input_pwd, user.password):
            user.delete()
            return redirect('/')
        else:
            messages.error(request, 'Please check your password')
            return render(request, 'accounts/withdraw.html')

    return render(request, 'accounts/withdraw.html')

