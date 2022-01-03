from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User

# Create your views here.
def signin(request):
    """
    :param request: log in에 필요한 input data(user id, password)
    :return: 로그인 성공 시 index로 리다이랙트 반환


    현재 user = authenticate(request, email=email, password=password) 코드는 기존 User 모델을 사용하며
    이로 인하여 로그인 시 User 모델에 등록된 username과 password를 이용하여 로그인을 하는 동작을 취함
    따라서 이를 해결하기 위해서 custom User 모델을 구현하고, authenticate 함수를 재정의하여 id와 password를
    이용하여 로그인 가능하게 수정해야 함
    """

    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            print("error")
            return render(request, 'accounts/login.html', {'error': 'username or password is incorrect'})

    return render(request, 'accounts/login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def signup(request):
    """
    :param request: 회원가입 요청 데이터(회원 id, 이름, password)
    :return: 회원가입 완료 시 index 리다이렉트 아닐 시 해당 페이지 return

    signup은 회원가입을 위한 view method로 페이지에서 user id, password, name을 입력으로 받아
    현재 장고에서 제공하는 User model을 그대로 이용하여 저장함
    """

    if request.method == 'POST':
        if request.POST['user-password'] == request.POST['user-confirm-pw']:
            user = User.objects.create_user(
                username=request.POST['user-name'],
                password=request.POST['user-password'],
                email=request.POST['user-email'],
                is_active=True,
            )
            user.save()

            return redirect('/')
        return render(request, 'accounts/signup.html')
    return render(request, 'accounts/signup.html')