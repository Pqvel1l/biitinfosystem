from django.shortcuts import render, redirect
from .models import User, File_Upload, Category
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from captcha.fields import CaptchaField
from django import forms

class SignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    pwd = forms.CharField(widget=forms.PasswordInput)
    gender = forms.ChoiceField(choices=[('1', 'Мужской'), ('2', 'Женский')])
    captcha = CaptchaField()

class LoginForm(forms.Form):
    email = forms.EmailField()
    pwd = forms.CharField(widget=forms.PasswordInput)
    captcha = CaptchaField()
def index(request):
    # Проверяем, установлена ли сессия для пользователя
    if 'user' not in request.session:
        # Если сессия не установлена, перенаправляем на страницу входа
        return redirect('login')

    query = request.GET.get('query', '')
    category_id = request.GET.get('category', '')
    files_list = File_Upload.objects.all().order_by('-id')

    if query:
        files_list = files_list.filter(title__icontains=query)

    if category_id:
        files_list = files_list.filter(category__id=category_id)

    # Пагинация
    paginator = Paginator(files_list, 5)  # Показывать по 5 файлов на странице
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all()
    return render(request, 'index.html', {'page_obj': page_obj, 'categories': categories})
def search(request):
    query = request.GET.get('query', '')
    if query:
        results = File_Upload.objects.filter(title__icontains=query)
    else:
        results = File_Upload.objects.none()
    return render(request, 'search_results.html', {'results': results})
def login(request):
    if 'user' in request.session:
        return redirect('index')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            pwd = form.cleaned_data['pwd']
            user = User.objects.filter(email=email, pwd=pwd).first()
            if user:
                request.session['user'] = user.email
                return redirect('index')
            else:
                messages.warning(request, "Неверный E-Mail или пароль!")
        else:
            messages.error(request, "Ошибка ввода капчи или других данных формы.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})
def logout(request):
    del request.session['user']
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            pwd = form.cleaned_data['pwd']
            gender = form.cleaned_data['gender']
            if not User.objects.filter(email=email).exists():
                User.objects.create(name=name, email=email, pwd=pwd, gender=gender)
                messages.success(request, "Ваш аккаунт успешно создан! Войдите в него!")
                return redirect('login')
            else:
                messages.warning(request, "E-Mail уже зарегистрирован!")
        else:
            messages.error(request, "Ошибка ввода капчи или других данных формы.")
    else:
        form = SignupForm()
    return render(request, 'signup.html', {'form': form})
@login_required
def file_upload(request):
    if not request.user.is_superuser:
        return HttpResponseForbidden("Только администратор может загружать файлы")

    if request.method == 'POST':
        title_name = request.POST['title']
        description_name = request.POST['description']
        file_name = request.FILES['file_to_upload']
        category_id = request.POST.get('category', None)

        category_obj = None
        if category_id:
            category_obj = Category.objects.get(id=category_id)

        new_file = File_Upload.objects.create(
            user=request.user,
            title=title_name,
            description=description_name,
            file_field=file_name,
            category=category_obj
        )
        messages.success(request, "File is uploaded successfully!")
        new_file.save()

    categories = Category.objects.all()
    return render(request, 'file_upload.html', {'categories': categories})
def delete_file(request, id):
    if 'user' in request.session:
        file_obj = File_Upload.objects.get(id=id)
        file_obj.delete()
        return redirect('settings')
    else:
        return redirect('login')
def test(request):
    return render(request, 'test.html')

