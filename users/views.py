from django.shortcuts import render, redirect
from django.contrib import messages
from collections import OrderedDict
from django.urls import reverse
from django.http import HttpResponseRedirect
from django.views import View
from django.contrib.auth import login, authenticate, logout
from snowplowrouting.models import InviteEmployee
from django.contrib.auth.decorators import user_passes_test

from .forms import RegisterForm, RegisterEmployeeForm, LoginForm
from .fusioncharts import FusionCharts


def logout_users(request):
    if request.method == "POST":
        logout(request)
        return HttpResponseRedirect(reverse('login'))


def login_users(request):
    if request.method == 'GET':
        form = LoginForm()
        context = {'form': form}
        return render(request, 'login.html', context)
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                if user.is_authenticated and user.profile.is_admin:
                    return HttpResponseRedirect(reverse('admin_profile'))
                elif user.is_authenticated and not user.profile.is_admin:
                    return HttpResponseRedirect(reverse('worker_profile'))
        else:
            print("Form not valid: ", form.errors)
            messages.success(request, "Error")
            context = {'form': form}
            return render(request, 'login.html', context)
    form = LoginForm()
    context = {'form': form}
    return render(request, 'login.html', context)

def register_admin(request):
    if request.method == 'GET':
        form = RegisterForm()
        map = myMapRom()
        context = {'form': form,
                   'map': map.render()}
        return render(request, 'register_admin.html', context)
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        map = myMapRom()
        if form.is_valid():
            user = form.save()
            user.refresh_from_db()
            user.profile.is_admin = True
            user.profile.county = form.cleaned_data.get('county')
            user.profile.validator_token = form.cleaned_data.get('validator_token')
            user.save()
            return HttpResponseRedirect(reverse('login'))
        else:
            print("Form not valid")
            messages.success(request, "Error")
            context = {'form': form,
                       'map': map.render()}
            return render(request, 'register_admin.html', context)
        return render(request, 'register_admin.html', {})

def register_employee(request):
    if request.method == 'GET':
        form = RegisterEmployeeForm()
        context = {'form': form}
        return render(request, 'register_employee.html', context)
    if request.method == 'POST':
        form = RegisterEmployeeForm(request.POST)
        if form.is_valid():
            employee = InviteEmployee.objects.filter(email=form.cleaned_data['email']).values()
            form.cleaned_data['county'] = employee[0]['county']
            user = form.save()
            user.refresh_from_db()
            user.profile.is_admin = False
            user.profile.county = employee[0]['county']
            user.profile.validator_token = form.cleaned_data.get('validator_token')
            user.save()
            return HttpResponseRedirect(reverse('login'))
        else:
            print("Form not valid:", form.errors)
            messages.success(request, "Error")
            context = {'form': form}
            return render(request, 'register_employee.html', context)
    return render(request, 'register_employee.html', {})

def myMapRom():

    fusionMap = FusionCharts("maps/romania", "myMapRom", "650", "550", "myMap-container", "json", [])
    fusionMap.addEvent("entityClick", "onEntityMapClick")

    return fusionMap
