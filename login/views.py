from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpRequest
from .models import User, ConfirmString
from .forms import UserForm, RegisterForm
import hashlib
import datetime
from RegisterAndLogin import settings


# Create your views here.

def index(request):
	return render(request, 'login/index.html')


# def login(request):
# 	if request.method == 'POST':
# 		username = request.POST.get('username')
# 		password = request.POST.get('password')
# 		message = '所有字段必须填写'
# 		if username and password:
# 			username = username.strip()
# 			password = password.strip()
# 			try:
# 				user = User.objects.get(name=username)
# 				print(user, user.password, sep='\t')
# 				if user.password == password:
# 					print('username={},password={}'.format(username, password))
# 					return HttpResponseRedirect(reverse('login:index'))
# 				else:
# 					message = '密码不正确'
# 			except:
# 				message = '用户名不存在'
# 		return render(request, 'login/login.html', {'message': message})
# 	return render(request, 'login/login.html')

def login(request):
	if request.session.get('is_login', None):
		return HttpResponseRedirect(reverse('login:index'))

	if request.method == 'POST':
		login_form = UserForm(request.POST)
		message = '请检查需要填写的内容'
		if login_form.is_valid():
			username = login_form.cleaned_data.get('username')
			password = login_form.cleaned_data.get('password')
			try:
				username = username.strip()
				user = User.objects.get(name=username)
				if not user.has_confirmed:
					message = '用户还未确认通过'
					return render(request, 'login/login.html', locals())
				if user.password == hash_code(password):
					request.session['is_login'] = True
					request.session['user_id'] = user.id
					request.session['user_name'] = user.name
					return HttpResponseRedirect(reverse('login:index'))
				else:
					message = '密码不正确'
			except:
				message = '用户不存在'
		return render(request, 'login/login.html', locals())

	login_form = UserForm()
	return render(request, 'login/login.html', locals())


def register(request):
	if request.session.get('is_login', None):
		return redirect('/login/index.html')

	if request.method == 'POST':
		register_form = RegisterForm(request.POST)
		message = '请检查填写的内容'
		if register_form.is_valid():
			username = register_form.cleaned_data.get('username')
			password1 = register_form.cleaned_data.get('password1')
			password2 = register_form.cleaned_data.get('password2')
			email = register_form.cleaned_data.get('email')
			sex = register_form.cleaned_data.get('sex')
			if password1 != password2:
				message = '两次输入密码不一致'
				return render(request, 'login/register.html', locals())
			else:
				same_name_user = User.objects.filter(name=username)
				if same_name_user:
					message = '用户名已存在，请重新填写用户名'
					return render(request, 'login/register.html', locals())
				same_email_user = User.objects.filter(email=email)
				if same_email_user:
					message = '该邮箱已被使用，请重新填写邮箱'
					return render(request, 'login/register.html', locals())

				new_user = User.objects.create()
				new_user.name = username
				new_user.password = hash_code(password1)
				new_user.email = email
				new_user.sex = sex
				new_user.save()

				code = make_confirm_string(new_user)
				send_email(email, code)
				message = '请前往邮箱进行确认'

				return redirect('/login/login/')
	register_form = RegisterForm()
	return render(request, 'login/register.html', locals())


def logout(request):
	# return redirect('/login/index/')
	if not request.session.get('is_login', None):
		return HttpResponseRedirect(reverse('login:index'))
	request.session.flush()
	return HttpResponseRedirect(reverse('login:index'))


def user_confirm(request):
	code = request.GET.get('code', None)
	message = ''

	print('code = {}'.format(code))

	try:
		confirm = ConfirmString.objects.get(code=code)
	except:
		message = '无效请求'
		return render(request, 'login/confirm.html', locals())

	c_time = confirm.c_time
	now = datetime.datetime.now()
	if now > c_time + datetime.timedelta(settings.CONFIRM_DAYS):
		confirm.user.delete()
		message = '您的邮件已过期，请重新注册'
		return render(request, 'login/confirm.html', locals())
	else:
		confirm.user.has_confirmed = True
		confirm.user.save()
		confirm.delete()
		message = '感些确认，请使用账户登录'
		return render(request, 'login/confirm.html', locals())


def hash_code(s, salt='RegisterAndLogin'):
	h = hashlib.sha256()
	s += salt
	h.update(s.encode())
	return h.hexdigest()


def make_confirm_string(user):
	now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
	code = hash_code(user.name, now)
	ConfirmString.objects.create(code=code, user=user)
	return code


def send_email(email, code):
	from django.core.mail import EmailMultiAlternatives
	subject = '来自flynngod@sina.com的注册确认邮件'
	text_content = '如果看到了该条消息，则说明不提供HTML链接功能'
	html_content = '<p><a href="http://{}/login/confirm/?code={}" target=blank>点击此链接完成注册，该链接有效期为{}天</a></p>'.format(
		'127.0.0.1:8000',
		code, settings.CONFIRM_DAYS)

	msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, [email])
	msg.attach_alternative(html_content, 'text/html')
	msg.send()
