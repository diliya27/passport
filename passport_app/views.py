
from django.views.generic import TemplateView,FormView
from django.views import View
from django.shortcuts import render, redirect
from django.contrib import messages
from passport_app.forms import PassportOfficerForm
from passport_app.models import PassportOfficer
from django.views.generic import TemplateView,View
from .forms import AdminLoginForm
from django.urls import reverse_lazy
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages



class IndexPageView(View):
    template_name = "index.html"
    def get(self,request,*args,**kwargs):
        return render(request,self.template_name) 
    

class AdminLogin(View):
    template_name='AdminLogin.html'
    form_class=AdminLoginForm
    def get(self,request,*args,**kwargs):
        form_instance=self.form_class()
        return render(request,self.template_name,{"form":form_instance})
    def post(self,request,*args,**kwargs):
        form_instance=self.form_class(request.POST)
        if form_instance.is_valid():
            uname=form_instance.cleaned_data.get("username")
            pwd=form_instance.cleaned_data.get("password")
            user_object=authenticate(request,username=uname,password=pwd)
            if user_object:
                login(request,user_object)
                return redirect("home")
        return render(request,self.template_name,{"form":form_instance})
    


class AdminLogout(View):
    def post(self,request,*args,**kwargs):
        logout(request)
        return redirect("admin-login")



class HomeView(TemplateView):
    template_name = "home.html"




class AddPassportOfficerView(View):
    template_name = "admin/add_passportofficer.html"

    def get(self, request):
        form = PassportOfficerForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = PassportOfficerForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Passport Officer added successfully!")
            return redirect("add_passport_officer")  # Redirect to avoid duplicate submissions
        return render(request, self.template_name, {'form': form})
    
    
    

# class ListPassportofficerView(View):

