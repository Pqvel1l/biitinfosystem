from django.shortcuts import render, redirect
from .models import User, File_Upload, Category
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

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
    if 'user' not in request.session:
        if request.method == 'POST':
            email = request.POST['email']
            pwd = request.POST['pwd']
            userExists = User.objects.filter(email=email, pwd=pwd)
            if userExists.exists():
                request.session["user"] = email
                return redirect('index')
            else:
                messages.warning(request, "Неверный E-Mail или пароль!")
        return render(request, 'login.html')
    else:
        return redirect('index')

def logout(request):
    del request.session['user']
    return redirect('login')

def signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        pwd = request.POST['pwd']
        gender = request.POST['gender']
        if not User.objects.filter(email=email).exists():
            create_user = User.objects.create(name=name, email=email, pwd=pwd, gender=gender)
            create_user.save()
            messages.success(request, "Ваш аккаунт успешно создан! Войдите в него!")
            return redirect('login')
        else:
            messages.warning(request, "E-Mail уже зарегистрирован!")
    return render(request, 'signup.html')

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

