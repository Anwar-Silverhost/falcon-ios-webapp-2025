from datetime import datetime
import random
import re
import string
from django.shortcuts import render,redirect
from django.contrib.auth.models import User 
from django.http import JsonResponse
from app.models import *
import os
from django.conf import settings
from django.contrib.auth import authenticate
from django.db.models import Count, Q


regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
 

def admin_navbar(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        # admin = User.objects.filter(id=Adm_id)
        admin = User.objects.filter(id=Adm_id, is_active=True)
        if not admin:
            return redirect('/')
        return render(request, 'admin/admin_navbar.html', {'admin': admin})
    else:
        return redirect('/')
 
 

 

def dashboard(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        # admin = User.objects.filter(id=Adm_id)
        admin = User.objects.filter(id=Adm_id, is_active=True)
        if not admin:
            return redirect('/')
        # print(admin.username)
  

        user_count = AppUser.objects.all().count()
        files_count = PDFfiles.objects.all().count()
        category_count = Category.objects.all().count()
        desig_count = Designation.objects.all().count()
        group_count = Group.objects.all().count() 
        #live count
        live_count = AppUser.objects.filter(device_token='login').count()

        notify = Notification_db.objects.all().order_by('-id')[:10]
 
        saved_message = request.session.pop('saved_message', None)
        return render(request, 'admin/dashboard.html', {'admin': admin,'saved_message':saved_message,'user_count':user_count,'files_count':files_count,'category_count':category_count,'desig_count':desig_count,'group_count':group_count,'notify':notify,'live_count':live_count})
    else:
        return redirect('/')


# users
def users(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        # admin = User.objects.filter(id=Adm_id)
        admin = User.objects.filter(id=Adm_id, is_active=True)
        if not admin:
            return redirect('/')
        user = AppUser.objects.all().order_by('-id')

         
        user_count = user.count()
        user_active_count = user.filter(user_status = 1).count()
        user_inactive_count = user.filter(user_status = 0).count()


        saved_message = request.session.pop('saved_message', None)
        return render(request, 'admin/users.html', {'admin': admin,'saved_message':saved_message,'user':user ,'user_count':user_count,'user_active_count':user_active_count,'user_inactive_count':user_inactive_count})
    else:
        return redirect('/')

def create_user(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        # admin = User.objects.filter(id=Adm_id) 
        admin = User.objects.filter(id=Adm_id, is_active=True)
        if not admin:
            return redirect('/')
        des = Designation.objects.all()
        group = Group.objects.filter(parent_group__isnull=True)
        saved_message = request.session.pop('saved_message', None)
        return render(request, 'admin/create_user.html', {'admin': admin,'saved_message':saved_message,'des':des,'groups':group})
    else:
        return redirect('/')

def save_user(request):
    if 'Adm_id' in request.session:
        if request.method == 'POST':
            fields = {
                'firstname': 'First name is required',
                'phone': 'Phone number is required',
                'email': 'Email is required',
                'username': 'Username is required',
                'password': 'Password is required',
                'confirm_password': 'Confirm Password is required',
                'dob': 'Date of birth is required',
                'desig': 'Designation is required',
                'weight': 'Weight is required'
            }
            for field, message in fields.items():
                if not request.POST.get(field):
                    return JsonResponse({'success': False, 'message': message})
            firstname = request.POST.get('firstname')
            lastname = request.POST.get('lastname')
            phone = request.POST.get('phone')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            gender = request.POST.get('gender')
            dob = request.POST.get('dob')
            location = request.POST.get('location')
            desigid = request.POST.get('desig')
            # group = request.POST.get('group')
            weight = request.POST.get('weight')
            desig = Designation.objects.get(id=desigid)


            # group = Group.objects.get(id=group)

            group_ids = request.POST.getlist('groups') 
            groups = Group.objects.filter(id__in=group_ids)  


            profilepic = request.FILES.get('profilepic', False)
            if profilepic: 
                original_filename = profilepic.name 
                sanitized_filename = re.sub(r'[^\w\-_\.]', '', original_filename.replace(' ', '_')) 
                profilepic.name = sanitized_filename
            else:
                profilepic = 'images/default.jpg'

            usersign = request.FILES.get('usersign',False)
            if usersign:
                original_sign_filename = usersign.name
                sanitized_sign_filename = re.sub(r'[^\w\-_\.]', '', original_sign_filename.replace(' ', '_')) 
                usersign.name = sanitized_sign_filename
            else:
                return JsonResponse({'success': False, 'message': 'Signature is required'})

            if(re.fullmatch(regex, email)):
                print("Valid Email") 
            else:
                return JsonResponse({'success': False, 'message': 'Invalid Email ID'})

            # if re.match("^(0|91)?[6-9][0-9]{9}$", phone):
            #      print("Valid Number") 
            # else:
            #     return JsonResponse({'success': False, 'message': 'Invalid Phone Number'})
 
            if password != confirm_password:
                return JsonResponse({'success': False, 'message': 'Passwords do not match'})

            if AppUser.objects.filter(username=username).exists():
                return JsonResponse({'success': False, 'message': 'User already exists'}) 

            if AppUser.objects.filter(email=email).exists():
                return JsonResponse({'success': False, 'message': 'Email already exists'}) 

            try:
                dob = datetime.strptime(dob, '%Y-%m-%d').date()
            except ValueError:
                return JsonResponse({'success': False, 'message': 'Invalid date format. Use YYYY-MM-DD.'})

            a = AppUser(firstname=firstname,lastname=lastname,phone=phone,email=email,username=username,password=password,gender=gender,dob=dob,location=location,designation=desig,profile_pic=profilepic,user_sign=usersign,weight=weight)
            a.save()
            userId = a.id

            a.groups.set(groups)
            a.save()

            desig = a.designation
            desig.count = AppUser.objects.filter(designation=desig).count()
            desig.save()

            saveNotify(f"{firstname} {lastname} user Created Success",'success')
 
            return JsonResponse({'success': True,'id':userId,'message': 'User created successfully'})
    return JsonResponse({'success': False, 'message': 'Invalid request'})

def view_user(request,id):
    try:
        if 'Adm_id' in request.session:
            if request.session.has_key('Adm_id'):
                Adm_id = request.session['Adm_id']
            # admin = User.objects.filter(id=Adm_id) 
            admin = User.objects.filter(id=Adm_id, is_active=True)
            if not admin:
                return redirect('/')
            user = AppUser.objects.get(id=id)
            group = Group.objects.filter(parent_group__isnull=True)
            groups = Group.objects.all()
            user_groups_ids = user.groups.values_list('id', flat=True)
            saved_message = request.session.pop('saved_message', None)
            return render(request, 'admin/view_user.html', {'admin': admin,'saved_message':saved_message,'user':user,'groups':group,'user_groups_ids':user_groups_ids})
        else:
            return redirect('/')
    except Exception as e:
        request.session['saved_message'] = 'User Not Found'
        print(str(e)) 
        return redirect(users)
    

def update_user(request,id): 
    try:
        if 'Adm_id' in request.session:
            if request.session.has_key('Adm_id'):
                Adm_id = request.session['Adm_id']
                admin = User.objects.filter(id=Adm_id)
                user = AppUser.objects.get(id=id)
                if request.method == 'POST':
                    firstname = request.POST.get('firstname')
                    lastname = request.POST.get('lastname')
                    phone = request.POST.get('phone')
                    email = request.POST.get('email') 
                    gender = request.POST.get('gender')
                    dob = request.POST.get('dob')
                    location = request.POST.get('location')
                    weight = request.POST.get('weight')

                    if AppUser.objects.filter(email=email).exclude(id=id).exists():
                        request.session['saved_message'] = 'Email already exists'
                        return redirect('view_user', id=id) 
    
                    user.firstname = firstname
                    user.lastname = lastname
                    user.phone = phone
                    user.email = email
                    user.gender = gender
                    user.dob = dob
                    user.location = location
                    user.weight = weight
                    user.save()

                    saveNotify(f"{firstname} {lastname} Details Updated",'info')

                    request.session['saved_message'] = 'Details Updated Successfully'

                    return redirect(view_user,int(user.id))
    except Exception as e:
        print( str(e))
        request.session['saved_message'] = 'Invalid Details'
        return redirect(users)

def updatePasscord(request,id):
    try:
        if 'Adm_id' in request.session:
            if request.session.has_key('Adm_id'):
                Adm_id = request.session['Adm_id']
                admin = User.objects.filter(id=Adm_id)
                user = AppUser.objects.get(id=id)
                if request.method == 'POST':
                    oldpassword = request.POST.get('current_password')
                    newpassword = request.POST.get('new_password')
                    confirmnewpassword = request.POST.get('confirm_new_password')
                    if oldpassword == user.password:
                        if newpassword == confirmnewpassword: 
                            if oldpassword == newpassword:
                                request.session['saved_message'] = 'Old Password and New Password are Same!'
                                return redirect(view_user,int(user.id))
                            else:
                                user.password = newpassword
                                user.save()

                                saveNotify(f"{user.firstname} {user.lastname} Password Updated",'info')

                                request.session['saved_message'] = 'Password Updated Successfully'
                                return redirect(view_user,int(user.id))
                        else:
                            request.session['saved_message'] = 'Password does not match'
                            return redirect(view_user,int(user.id))
                    else:
                        request.session['saved_message'] = 'Old Password is incorrect'
                        return redirect(view_user,int(user.id))
    except Exception as e:
        request.session['saved_message'] = 'Invalid Details'
        return redirect(view_user,int(user.id))

def statusUpdate(request,id,type):
    try:
        if 'Adm_id' in request.session:
            if request.session.has_key('Adm_id'):
                Adm_id = request.session['Adm_id']
                admin = User.objects.filter(id=Adm_id)
                user = AppUser.objects.get(id=id)

                if type == 'sts':
                    if user.user_status == '1':

                        user.user_status = '0'
                        saveNotify(f"{user.firstname} {user.lastname} Status Updated",'info') 
                        request.session['saved_message'] = 'User Status Updated to Inactive Successfully'
                    else:
                        user.user_status = '1'
                        saveNotify(f"{user.firstname} {user.lastname} Status Updated",'info')

                        request.session['saved_message'] = 'User Status Updated to Active Successfully' 
                    user.save()
                    return redirect(view_user,int(user.id))
                elif type == 'del':
                    user.delete()
                    saveNotify(f"{user} User Deleted Successfully",'danger')
                    request.session['saved_message'] = 'User Deleted Successfully' 
                    return redirect(users)
 
    except Exception as e:
        print(e)
        request.session['saved_message'] = 'Invalid Details'
        return redirect(view_user,int(user.id))


def updateUserGruop(request,id):
    try:
        if 'Adm_id' in request.session:
            if request.session.has_key('Adm_id'):
                Adm_id = request.session['Adm_id']
                admin = User.objects.filter(id=Adm_id)
                user = AppUser.objects.get(id=id)

                if request.method == 'POST':
                    group_ids = request.POST.getlist('groups')  # Get the list of selected groups
                    groups = Group.objects.filter(id__in=group_ids)  # Fetch the Group objects

                    user.groups.set(groups)
                    user.save()  
                saveNotify(f"{user.firstname} {user.lastname} Aircraft type Updated Successfully",'info')
                request.session['saved_message'] = 'User Aircraft type Updated Successfully'
                return redirect(view_user,int(user.id))
    except Exception as e:
        print(e)
        request.session['saved_message'] = 'Invalid Details'
        return redirect(view_user,int(user.id))
        

def updateUserSign(request,id):
    try:
        if 'Adm_id' in request.session:
            if request.session.has_key('Adm_id'):
                Adm_id = request.session['Adm_id']
                admin = User.objects.filter(id=Adm_id)
                user = AppUser.objects.get(id=id)

                if request.method == 'POST':
                    usersign = request.FILES.get('usersign',False)
                    if usersign:
                        original_sign_filename = usersign.name
                        sanitized_sign_filename = re.sub(r'[^\w\-_\.]', '', original_sign_filename.replace(' ', '_')) 
                        usersign.name = sanitized_sign_filename
                        user.user_sign = usersign
                        user.save()  
                saveNotify(f"{user.firstname} {user.lastname} Signature Updated Successfully",'info')
                request.session['saved_message'] = 'User Signature Updated Successfully'
                return redirect(view_user,int(user.id))
    except Exception as e:
        print(e)
        request.session['saved_message'] = 'Invalid Details'
        return redirect(view_user,int(user.id))
    





#Designatoin
def designation(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        # admin = User.objects.filter(id=Adm_id)
        admin = User.objects.filter(id=Adm_id, is_active=True)
        if not admin:
            return redirect('/')
        des = Designation.objects.all()
        saved_message = request.session.pop('saved_message', None)
        return render(request, 'admin/designation.html', {'admin': admin,'saved_message':saved_message,'des':des})
    else:
        return redirect('/')

def save_designation(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
            admin = User.objects.filter(id=Adm_id)
            if request.method == 'POST':
                des = request.POST.get('designation')
                if des:
                    designation_obj = Designation.objects.filter(designation=des)
                    if designation_obj:
                        request.session['saved_message'] = 'Designation Already Exists'
                        return redirect(designation)
                    else:
                        designation_obj = Designation(designation=des,count = '0')
                        designation_obj.save() 
                        saveNotify(f"{des} Designation Added Successfully",'success')

                        request.session['saved_message'] = 'Designation Added Successfully'
                        return redirect(designation)

def delete_designation(request,id):
    des = Designation.objects.get(id=id)
    des.delete()
    saveNotify(f"{des} Designation Deleted Successfully",'danger')

    request.session['saved_message'] = 'Designation Deleted Successfully'
    return redirect(designation)

 # group
# def groups(request):
#     if 'Adm_id' in request.session:
#         if request.session.has_key('Adm_id'):
#             Adm_id = request.session['Adm_id']
#         admin = User.objects.filter(id=Adm_id)
#         groups = Group.objects.all()
#         groups = Group.objects.filter(parent_group__isnull=True).prefetch_related('child_groups')
#         saved_message = request.session.pop('saved_message', None)
#         return render(request, 'admin/group.html', {'admin': admin,'saved_message':saved_message,'groups':groups})
#     else:
#         return redirect('/')

def groups(request):
    if 'Adm_id' in request.session:
        Adm_id = request.session['Adm_id']
        # admin = User.objects.filter(id=Adm_id)
        admin = User.objects.filter(id=Adm_id, is_active=True)
        if not admin:
            return redirect('/')
        groups = Group.objects.filter(parent_group__isnull=True).prefetch_related('child_groups')

        for group in groups: 
            group.has_pdf = PDFfiles.objects.filter(
                Q(group_is=group) | Q(group_is__in=group.child_groups.all())
            ).exists() 
            for subgroup in group.child_groups.all():
                subgroup.has_pdf = PDFfiles.objects.filter(group_is=subgroup).exists()

        saved_message = request.session.pop('saved_message', None)
        return render(request, 'admin/group.html', {'admin': admin, 'saved_message': saved_message, 'groups': groups})
    else:
        return redirect('/')

def save_group(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
            admin = User.objects.filter(id=Adm_id)
            if request.method == 'POST':
                group_name = request.POST.get('group')
                parent_group_id = request.POST.get('parent_group')

                group_name_obj = Group.objects.filter(group_name=group_name)
                # if group_name_obj:
                #     request.session['saved_message'] = 'Group Already Exists'
                #     return redirect(groups) 
                if group_name:
                    parent_group = None
                    if parent_group_id:
                        parent_group = Group.objects.get(id=parent_group_id) 
                    new_group = Group(group_name=group_name, parent_group=parent_group)
                    new_group.save() 

                    saveNotify(f"{group_name} Aircraft type saved successfully",'success')

                    request.session['saved_message'] = 'Aircraft type saved successfully!'
                    return redirect(groups)   
                else:
                    request.session['saved_message'] =  'Aircraft type name is required.'
                    return redirect(groups) 
            else:
                return redirect(groups)
    else:
        return redirect('/')

def delete_group(request,id):
    group = Group.objects.get(id=id)

   
    group.delete()
    saveNotify(f"{group} Aircraft type Deleted Successfully",'danger')

    request.session['saved_message'] = 'Aircraft type Deleted Successfully'
    return redirect(groups)

# category
def category(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
            admin = User.objects.filter(id=Adm_id, is_active=True)
            if not admin:
                return redirect('/')
            saved_message = request.session.pop('saved_message', None)
            categories = Category.objects.all() 
            return render(request, 'admin/category.html', {'admin': admin, 'categories': categories, 'saved_message': saved_message})
    else:
        return redirect('/')

        
# def save_category(request):
#     if 'Adm_id' in request.session:
#         if request.method == 'POST':
#             category_name = request.POST.get('category_name')
#             main_category_id = request.POST.get('main_category') 
#             parent_category_id = request.POST.get('parent_category') 
#             sub_parent_category_id = request.POST.get('sub_parent_category') 

#             print(category_name)
#             print(main_category_id)
#             print(parent_category_id)
#             print(sub_parent_category_id)

#             if ((main_category_id == '0')):
#                 new_category = Category(category_name=category_name)
#                 new_category.save()
#                 request.session['saved_message'] = 'Main category saved successfully!'
#                 return redirect(category)

#             elif ((main_category_id != '0') and (parent_category_id == '0')):
#                 main_category_id = Category.objects.get(id=main_category_id)
#                 new_category = Category(category_name=category_name, parent_category=main_category_id)
#                 new_category.save()
#                 request.session['saved_message'] = 'Parent category saved successfully!'
#                 return redirect(category)

#             elif ((main_category_id != '0') and (parent_category_id != '0') and (sub_parent_category_id == '0')):
#                 main_category_id = Category.objects.get(id=main_category_id)
#                 parent_category_id = Category.objects.get(id=parent_category_id)
#                 new_category = Category(category_name=category_name, sub_parent_category=parent_category_id, parent_category= main_category_id)
#                 new_category.save()
#                 request.session['saved_message'] = 'Sub parent category saved successfully!'
#                 return redirect(category)
 
#             elif ((main_category_id != '0') and (parent_category_id != '0') and (sub_parent_category_id != '0')):
#                 main_category_id = Category.objects.get(id=main_category_id)
#                 parent_category_id = Category.objects.get(id=parent_category_id)
#                 sub_parent_category_id = Category.objects.get(id=sub_parent_category_id)
#                 new_category = Category(category_name=category_name, sub_parent_category=parent_category_id, parent_category= main_category_id,subchild_parent_category=sub_parent_category_id)
#                 new_category.save()
#                 request.session['saved_message'] = 'Sub child parent category saved successfully!'
#                 return redirect(category)

#             else:
#                 request.session['saved_message'] = 'You can not allow this method'
#                 return redirect(category) 
#         else:
#             return redirect('category') 
#     else:
#         return redirect('/')


              
def save_category(request):
    if 'Adm_id' in request.session:
        if request.method == 'POST':
            category_name = request.POST.get('category_name')
            main_category_id = request.POST.get('main_category') 
            parent_category_id = request.POST.get('parent_category') 
            sub_parent_category_id = request.POST.get('sub_parent_category') 

            print(category_name)
            print(main_category_id)
            print(parent_category_id)
            print(sub_parent_category_id)

            if ((main_category_id == '0')):
                new_category = Category(category_name=category_name)
                new_category.save()
                saveNotify(f"{category_name} category saved successfully",'success')
                request.session['saved_message'] = 'Main category saved successfully!'
                return redirect(category)

            elif ((main_category_id != '0') and (parent_category_id == '0')):  
                main_category_id = Category.objects.get(id=main_category_id)
                new_category = Category(category_name=category_name, parent_category=main_category_id)
                new_category.save()
                saveNotify(f"{category_name} Parent category saved successfully",'success')

                request.session['saved_message'] = 'Parent category saved successfully!'
                return redirect(category)

            elif ((main_category_id != '0') and (parent_category_id != '0') and (sub_parent_category_id == '0')):
                parent_category_id = Category.objects.get(id=parent_category_id)
                new_category = Category(category_name=category_name,  parent_category= parent_category_id)
                new_category.save()
                saveNotify(f"{category_name} Parent category saved successfully",'success')

                request.session['saved_message'] = 'Sub parent category saved successfully!'
                return redirect(category)
 
            elif ((main_category_id != '0') and (parent_category_id != '0') and (sub_parent_category_id != '0')): 
                sub_parent_category_id = Category.objects.get(id=sub_parent_category_id)
                new_category = Category(category_name=category_name, parent_category= sub_parent_category_id,)
                new_category.save()
                saveNotify(f"{category_name} Sub child parent category saved successfully",'success')

                request.session['saved_message'] = 'Sub child parent category saved successfully!'
                return redirect(category)

            else:
                request.session['saved_message'] = 'You can not allow this method'
                return redirect(category) 
        else:
            return redirect('category') 
    else:
        return redirect('/')

def delete_category(request,id):
    cate = Category.objects.get(id=id)
    cate.delete()
    saveNotify(f"{cate} Category Deleted Successfully",'danger')
    request.session['saved_message'] = 'Category Deleted Successfully'
    return redirect(category)


def filemanager(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
            # admin = User.objects.filter(id=Adm_id)
            admin = User.objects.filter(id=Adm_id, is_active=True)
            if not admin:
                return redirect('/')
            saved_message = request.session.pop('saved_message', None)
            categories = Category.objects.all() 
            pdffiles = PDFfiles.objects.all().order_by('-id')
            return render(request, 'admin/file_manager.html', {'admin': admin,'pdffiles':pdffiles, 'categories': categories, 'saved_message': saved_message})
    else:
        return redirect('/')


def fileupload(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
            # admin = User.objects.filter(id=Adm_id)
            admin = User.objects.filter(id=Adm_id, is_active=True)
            if not admin:
                return redirect('/')
            saved_message = request.session.pop('saved_message', None)
            categories = Category.objects.all()  
            groups = Group.objects.all() 

            return render(request, 'admin/upload-pdf.html', {'admin': admin, 'categories': categories, 'saved_message': saved_message,'groups':groups})
    else:
        return redirect('/')

#old save file without multiple files save
# def savefile(request):
#     if 'Adm_id' in request.session:
#         if request.method == 'POST':
#             maingroup = request.POST.get('maingroup')
#             subgroup = request.POST.get('subgroup')
#             pdfname = request.POST.get('pdfname')
#             maincategory = request.POST.get('maincategory')
#             parentcategory = request.POST.get('parentcategory')
#             category = request.POST.get('category')
#             subcategory = request.POST.get('subcategory') 
#             pdffile = request.FILES.get('pdffile', False)
 
#             if (subgroup != '0'):
#                 group_id = Group.objects.get(id=subgroup)
#             elif (maingroup != '0'):
#                 group_id = Group.objects.get(id=maingroup)
#             else:
#                 request.session['saved_message'] = 'Please Select Aircraft type Field' 
#                 return redirect(fileupload) 

#             if (subcategory != '0'):
#                 category_id = Category.objects.get(id=subcategory)
#             elif (category != '0'):
#                 category_id = Category.objects.get(id=category)
#             elif (parentcategory != '0'):
#                 category_id = Category.objects.get(id=parentcategory)
#             elif (maincategory != '0'):
#                 category_id = Category.objects.get(id=maincategory)
#             else:
#                 request.session['saved_message'] = 'Please Select Main Menu Field' 
#                 return redirect(fileupload)

#             try:
#                 p = PDFfiles()
#                 p.group_is = group_id  
#                 p.category_is = category_id
#                 p.pdf_name = pdfname
#                 p.pdf_file = pdffile
#                 p.save()
 
#                 random_string = ''.join(random.choices(string.ascii_letters, k=10))
#                 new_file_name = f"{p.id}{random_string}.pdf" 
#                 old_file_path = p.pdf_file.path 
#                 new_file_path = os.path.join(os.path.dirname(old_file_path), new_file_name) 
#                 os.rename(old_file_path, new_file_path) 
#                 p.pdf_file.name = os.path.join(os.path.dirname(p.pdf_file.name), new_file_name)
#                 p.save()

#                 saveNotify(f"{pdfname} File uploaded successfully",'success')
                

#                 request.session['saved_message'] = 'File uploaded successfully'
#                 return redirect(filemanager)
#             except Exception as e:
#                 request.session['saved_message'] = 'Error in uploading file' + str(e)
#                 return redirect(fileupload)
#         else: 
#             request.session['saved_message'] = 'Something wrong check the entered value' 
#             return redirect(fileupload)
#     else:
#         return redirect('filemanager')
        
        
        

def savefile(request):
    if 'Adm_id' in request.session:
        if request.method == 'POST':
            maingroup = request.POST.get('maingroup')
            pdfname = request.POST.get('pdfname')
            maincategory = request.POST.get('maincategory')
            parentcategory = request.POST.get('parentcategory')
            category = request.POST.get('category')
            subcategory = request.POST.get('subcategory') 
            pdffile = request.FILES.get('pdffile', False)
            if (subcategory != '0'):
                category_id = Category.objects.get(id=subcategory)
            elif (category != '0'):
                category_id = Category.objects.get(id=category)
            elif (parentcategory != '0'):
                category_id = Category.objects.get(id=parentcategory)
            elif (maincategory != '0'):
                category_id = Category.objects.get(id=maincategory)
            else:
                request.session['saved_message'] = 'Please Select Main Menu Field' 
                return redirect(fileupload)
                
            Adm_id = request.session['Adm_id']
            autheradmin = User.objects.get(id=Adm_id) 
            if autheradmin.is_staff:
                roleis = "admin"
            else:
                roleis = "superadmin"    
                
            if (maingroup == 'allaircrafts'):
                try:
                    groups = Group.objects.all()
                    for group in groups:
                        if group.parent_group: 
                            # print(f"Group: {group.group_name} | Parent Group: {group.parent_group.group_name}")
                            group_id = Group.objects.get(id=group.id)
                            p = PDFfiles()
                            p.group_is = group_id
                            p.category_is = category_id
                            p.pdf_name = pdfname
                            p.pdf_file = pdffile
                            p.author = autheradmin
                            p.role = roleis
                            p.save()

                            # Rename the file to avoid conflicts
                            random_string = ''.join(random.choices(string.ascii_letters, k=10))
                            new_file_name = f"{p.id}{random_string}.pdf" 
                            old_file_path = p.pdf_file.path 
                            new_file_path = os.path.join(os.path.dirname(old_file_path), new_file_name) 
                            os.rename(old_file_path, new_file_path) 
                            p.pdf_file.name = os.path.join(os.path.dirname(p.pdf_file.name), new_file_name)
                            p.save()
                except Exception as e:
                    request.session['saved_message'] = 'Error in uploading file' + str(e)
                    return redirect(fileupload)
            else:
                subgroup = request.POST.get('subgroup')
                if (subgroup != '0'):
                    group_id = Group.objects.get(id=subgroup)
                elif (maingroup != '0'):
                    group_id = Group.objects.get(id=maingroup)
                else:
                    request.session['saved_message'] = 'Please Select Aircraft type Field' 
                    return redirect(fileupload) 
                try:
                    p = PDFfiles()
                    p.group_is = group_id  
                    p.category_is = category_id
                    p.pdf_name = pdfname
                    p.pdf_file = pdffile
                    p.author = autheradmin
                    p.role = roleis
                    p.save()
                    random_string = ''.join(random.choices(string.ascii_letters, k=10))
                    new_file_name = f"{p.id}{random_string}.pdf" 
                    old_file_path = p.pdf_file.path 
                    new_file_path = os.path.join(os.path.dirname(old_file_path), new_file_name) 
                    os.rename(old_file_path, new_file_path) 
                    p.pdf_file.name = os.path.join(os.path.dirname(p.pdf_file.name), new_file_name)
                    p.save()
                except Exception as e:
                    request.session['saved_message'] = 'Error in uploading file' + str(e)
                    return redirect(fileupload)
            saveNotify(f"{pdfname} File uploaded successfully",'success')
            request.session['saved_message'] = 'File uploaded successfully'
            return redirect(filemanager)
        else: 
            request.session['saved_message'] = 'Something wrong check the entered value' 
            return redirect(fileupload)
    else:
        return redirect('filemanager')
        

        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        

def viewfile(request, id):
    try:
        if 'Adm_id' in request.session:
            if request.session.has_key('Adm_id'):
                Adm_id = request.session['Adm_id']
                admin = User.objects.filter(id=Adm_id)
                saved_message = request.session.pop('saved_message', None) 
                p = PDFfiles.objects.get(id=id) 
                group = Group.objects.all()
                category = Category.objects.all()

                # Prepare hierarchical data
                category_hierarchy = []
                cat = p.category_is
                while cat and len(category_hierarchy) < 4:
                    category_hierarchy.append(cat)
                    cat = cat.parent_category
                
                category_hierarchy.reverse()  
                
                return render(request, 'admin/view_file.html', {
                    'admin': admin,
                    'group': group,
                    'groups': group,
                    'category': category,
                    'categories': category,
                    'pdf': p,
                    'saved_message': saved_message,
                    'category_hierarchy': category_hierarchy
                })
            else:
                return redirect('/')
    except Exception as e:
        print(str(e))
        request.session['saved_message'] = 'File matching query does not exist'
        return redirect(filemanager)


def change_file_status(request,id):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
            admin = User.objects.filter(id=Adm_id)
            p = PDFfiles.objects.get(id=id) 
            if request.method == 'POST':
                status = request.POST.get('status')
                p.status = status
                p.save()
                saveNotify(f"{p} File status changed successfully",'success')
                
                request.session['saved_message'] = 'File status changed successfully' 
                return redirect(viewfile,int(p.id))
        else:
            return redirect('/')
    else:
        return redirect('/')

def update_details_pdf(request,id):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
            admin = User.objects.filter(id=Adm_id)
            p = PDFfiles.objects.get(id=id)  
            if request.method == 'POST': 
                which_type = request.GET.get('type')  
                if which_type == '1':
                    p.pdf_name = request.POST.get('pdfname')
                    p.save()
                    saveNotify(f"{p} File name updated successfully",'info')

                    request.session['saved_message'] = 'File name updated successfully'
                    return redirect(viewfile,int(p.id))

                elif which_type == '2':
                    p.pdf_file = request.FILES.get('pdffile', False)
                    p.save()

                    random_string = ''.join(random.choices(string.ascii_letters, k=10))
                    new_file_name = f"{p.id}{random_string}.pdf" 
                    old_file_path = p.pdf_file.path 
                    new_file_path = os.path.join(os.path.dirname(old_file_path), new_file_name) 
                    os.rename(old_file_path, new_file_path) 
                    p.pdf_file.name = os.path.join(os.path.dirname(p.pdf_file.name), new_file_name)
                    p.save()
                    
                    saveNotify(f"{p} File updated successfully",'info')

                    request.session['saved_message'] = 'File updated successfully'
                    return redirect(viewfile,int(p.id))

                elif which_type == '3': 
                    maingroup = request.POST.get('maingroup')
                    subgroup = request.POST.get('subgroup')
                    if (subgroup != '0'):
                        p.group_is = Group.objects.get(id=subgroup)
                    elif (maingroup != '0'):
                        p.group_is = Group.objects.get(id=maingroup)
                    else:
                        request.session['saved_message'] = 'Please Select Aircraft type Field' 
                        return redirect(viewfile,int(p.id)) 
                    p.save()
                    saveNotify(f"Aircraft type updated successfully",'info')

                    request.session['saved_message'] = 'Aircraft type updated successfully' 
                    return redirect(viewfile,int(p.id))

                elif which_type == '4': 
                    maincategory = request.POST.get('maincategory')
                    parentcategory = request.POST.get('parentcategory')
                    category = request.POST.get('category')
                    subcategory = request.POST.get('subcategory') 
                    if (subcategory != '0'):
                        p.category_is = Category.objects.get(id=subcategory)
                    elif (category != '0'):
                        p.category_is = Category.objects.get(id=category)
                    elif (parentcategory != '0'):
                        p.category_is = Category.objects.get(id=parentcategory)
                    elif (maincategory != '0'):
                        p.category_is = Category.objects.get(id=maincategory)
                    else:
                        request.session['saved_message'] = 'Please Select Main Menu Field' 
                        return redirect(viewfile,int(p.id)) 
                    p.save()
                    saveNotify(f"Category updated successfully",'info') 
                    
                    request.session['saved_message'] = 'Category updated successfully'
                    return redirect(viewfile,int(p.id))

            request.session['saved_message'] = 'Something wrong please check'
            return redirect(viewfile,int(p.id))
        else:
            return redirect('/')
    else:
        return redirect('/')

def delete_file(request, id):
    p = PDFfiles.objects.get(id=id) 
    if p.pdf_file:
        file_path = os.path.join(settings.MEDIA_ROOT, p.pdf_file.name)
        if os.path.exists(file_path):
            os.remove(file_path) 
    p.delete() 
    saveNotify(f"{p} File deleted successfully",'danger') 
    request.session['saved_message'] = 'File deleted successfully' 
    return redirect(filemanager)

def delete_multiple_files(request):
    """Deletes multiple files."""
    if request.method == 'POST':
        file_ids = request.POST.getlist('file_ids')
        deleted_files_count = 0
        for file_id in file_ids:
            try:
                p = PDFfiles.objects.get(id=file_id)
                if p.pdf_file:
                    file_path = os.path.join(settings.MEDIA_ROOT, p.pdf_file.name)
                    if os.path.exists(file_path):
                        os.remove(file_path)
                p.delete()
                deleted_files_count += 1
            except PDFfiles.DoesNotExist:
                continue
        saveNotify(f"{deleted_files_count} files deleted successfully.", 'danger')
        request.session['saved_message'] = f"{deleted_files_count} files deleted successfully."
    return redirect(filemanager)

    
    
    

def saveNotify(word,color): 
    n = Notification_db()
    n.notification = str(word)
    n.color = color
    n.save()
    return

def admin_update_details(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        admin = User.objects.filter(id=Adm_id)
        adminx = User.objects.get(id=Adm_id)
        saved_message = request.session.pop('saved_message', None)
        return render(request, 'admin/update_admin_profile.html', {'adminx': adminx,'admin': admin, 'saved_message': saved_message})
    else:
        return redirect('/')

def admin_update_save(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
            admin = User.objects.get(id=Adm_id)
            if request.method == 'POST': 
                cpassword = request.POST.get('cpassword') 
                npassword = request.POST.get('npassword') 
                confirm_password = request.POST.get('confirm_password')  
                if admin.check_password(cpassword):
                    if npassword == confirm_password:  
                        # admin.username = request.POST.get('username') 
                        # admin.email = request.POST.get('email') 
                        # admin.first_name = request.POST.get('name')  
                        admin.set_password(npassword)
                        admin.save()
                        
                        user = authenticate(request, username=admin.username, password=npassword)
                        if user is not None:
                            request.session['Adm_id'] = user.id
                            saveNotify(f" Admin password updated successfully",'success')
                            request.session['saved_message'] = 'Admin password updated successfully' 
                            return redirect(admin_update_details)
                    else: 
                        request.session['saved_message'] = 'Password and confirm password does not match'
                        return redirect(admin_update_details)
                else: 
                    request.session['saved_message'] = 'Current password is incorrect'
                    return redirect(admin_update_details) 
            return redirect(admin_update_details)


def home_apps(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        # admin = User.objects.filter(id=Adm_id)
        admin = User.objects.filter(id=Adm_id, is_active=True)
        if not admin:
            return redirect('/')
        adminx = User.objects.get(id=Adm_id)
        saved_message = request.session.pop('saved_message', None)
        apps = Apps_db.objects.all()
        return render(request, 'admin/home_apps.html', {'apps':apps,'adminx': adminx,'admin': admin, 'saved_message': saved_message})
    else:
        return redirect('/')

def save_app(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
            admin = User.objects.get(id=Adm_id)
            if request.method == 'POST':
                app_name = request.POST.get('appname')
                app_color = request.POST['app_color']
                app_url = request.POST.get('applink')
                app_icon = request.FILES.get('appicon', False)

                a = Apps_db()
                a.app_name = app_name
                a.color = app_color
                a.app_url = app_url
                a.app_icon = app_icon
                a.save()

                request.session['saved_message'] = 'New app added successfully'
                saveNotify(f" New app added successfully",'success')
                return redirect(home_apps) 
        else:
            return redirect('/')

def update_app(request,id):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
            admin = User.objects.get(id=Adm_id)
            if request.method == 'POST':
                app_name = request.POST.get('appname')
                app_color = request.POST['app_color']
                app_url = request.POST.get('applink')
                app_icon = request.FILES.get('appicon', False)

                a = Apps_db.objects.get(id=id)
                a.app_name = app_name
                a.color = app_color
                a.app_url = app_url 
                a.save()

                if app_icon:
                    a.app_icon = app_icon
                    a.save() 
                request.session['saved_message'] = 'App Updated successfully'
                saveNotify(f"App Updated successfully",'warning')
                return redirect(home_apps) 
        else:
            return redirect('/')

def delete_app(request,id):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
            admin = User.objects.get(id=Adm_id)
            a = Apps_db.objects.get(id=id)
            a.delete()
            request.session['saved_message'] = 'App deleted successfully'
            saveNotify(f"App deleted successfully",'danger')
            return redirect(home_apps)
        else:
            return redirect('/')






# Module 2 :

FORM_LIST = [
    ("FAF01", "Aircraft Search Checklist"),
    ("FAF02", "Rotary Wing Journey Log"),
    ("FAF03", "OFP"),  
    ("FAF04", "CFR"),
    ("FAF05", "Discretion Report"),
    ("FAF06", "Rotary Wing Flight Plan Envelope")
]


def forms(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        # admin = User.objects.filter(id=Adm_id)
        admin = User.objects.filter(id=Adm_id, is_active=True)
        if not admin:
            return redirect('/')
        adminx = User.objects.get(id=Adm_id)
        saved_message = request.session.pop('saved_message', None) 
        return render(request, 'admin/forms.html', {'adminx': adminx,'admin': admin, 'saved_message': saved_message})
    else:
        return redirect('/')

def form(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        # admin = User.objects.filter(id=Adm_id)
        admin = User.objects.filter(id=Adm_id, is_active=True)
        if not admin:
            return redirect('/')
        adminx = User.objects.get(id=Adm_id)

        formid = request.GET.get('id') 
        form_exists = any(formid == form[0] for form in FORM_LIST) 

        if not form_exists:
            request.session['saved_message'] = f"Form does not exist in the list."
            print(f"Form ID {formid} does not exist in the list.")
            return redirect(forms)
        
        form_name = next((form[1] for form in FORM_LIST if form[0] == formid), None)

        #fetch the al form in slecet form id based

        current_forms = Forms_db.objects.filter(form_Id = formid).filter(status = 'completed').order_by('-id')
 
        formData = {
            "formId" : formid,
            "formName" : form_name
        }
  
        saved_message = request.session.pop('saved_message', None) 
        return render(request, 'admin/form.html', {'adminx': adminx,'admin': admin,'formData':formData, 'saved_message': saved_message,'current_forms':current_forms})
    else:
        return redirect('/')
    

def viewForm(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        admin = User.objects.filter(id=Adm_id)

        formid = request.GET.get('id')  

        formdata_is = Forms_db.objects.get(form_ref_no=formid)

        formID = formdata_is.form_Id
 
        print(formdata_is.formData)
      
        saved_message = request.session.pop('saved_message', None) 
        return render(request, 'admin/view_form.html', {'admin': admin, 'saved_message': saved_message,'formid':formid,'formdata_is':formdata_is,'formID':formID})
    else:
        return redirect('/')





# Daily form Section  .order_by('-id')
def dailyForm(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        # admin = User.objects.filter(id=Adm_id) 
        admin = User.objects.filter(id=Adm_id, is_active=True)
        if not admin:
            return redirect('/')
        groups = Group.objects.all() 

        # signfiles = SignPDFFiles_db.objects.all().order_by('signfile_Date')
        signfiles = SignPDFFiles_db.objects.all().order_by('-id')

        signedUsers = SignedCaptFiles_db.objects.all()
        
        saved_message = request.session.pop('saved_message', None) 
        return render(request, 'admin/daily_sign_forms.html', {'admin': admin, 'saved_message': saved_message,'groups':groups,'signfiles':signfiles,'signedUsers':signedUsers})
    else:
        return redirect('/')



def save_dailyForm(request):    
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        admin = User.objects.filter(id=Adm_id) 
        

        if request.method == 'POST':

            date = request.POST.get('date')
            maingroup = request.POST.get('maingroup')
            subgroup = request.POST.get('subgroup')
            pdfname = request.POST.get('pdfname')
            pdffile = request.FILES.get('pdffile', False)

            if (maingroup != '0'):
                group_id1 = Group.objects.get(id=maingroup)
            else:
                request.session['saved_message'] = 'Please Select Aircraft type Field' 
                return redirect(dailyForm) 
            
            if (subgroup != '0'):
                group_id2 = Group.objects.get(id=subgroup)
            else:
                request.session['saved_message'] = 'Please Select Aircraft reg. Field' 
                return redirect(dailyForm)  
            

            existing_record = SignPDFFiles_db.objects.filter(
                signfile_Date=date,
                Aircraft_Type=group_id1,
                Aircraft_Reg=group_id2
            ).exists()

            if existing_record:
                request.session['saved_message'] = 'File with this information already exists'
                return redirect(dailyForm)
          
            try:
                s = SignPDFFiles_db() 
                s.signfile_Date = date   
                s.Aircraft_Type = group_id1   
                s.Aircraft_Reg = group_id2   
                s.signfile_Name = pdfname
                s.signpdf_file = pdffile
                s.save()
 
                random_string = ''.join(random.choices(string.ascii_letters, k=10))
                new_file_name = f"{s.id}{random_string}.pdf" 
                old_file_path = s.signpdf_file.path 
                new_file_path = os.path.join(os.path.dirname(old_file_path), new_file_name) 
                os.rename(old_file_path, new_file_path) 
                s.signpdf_file.name = os.path.join(os.path.dirname(s.signpdf_file.name), new_file_name)
                s.signfile_Id = f"{s.id}" + ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                s.save()

                saveNotify(f"{pdfname} File uploaded successfully",'success')
                
                request.session['saved_message'] = 'File uploaded successfully'
                saveNotify(f"Signature file save successfully",'success')
                return redirect(dailyForm)
            except Exception as e:
                request.session['saved_message'] = 'Error in uploading file' + str(e)
                return redirect(dailyForm)
        else: 
            request.session['saved_message'] = 'Something wrong check the entered value' 
            return redirect(dailyForm)
 
    else:
        return redirect('/')
    



def update_dailyForm(request, id):    
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        admin = User.objects.filter(id=Adm_id) 
        

        if request.method == 'POST':

            date = request.POST.get('date')
            maingroup = request.POST.get('maingroup')
            subgroup = request.POST.get('subgroup')
            pdfname = request.POST.get('pdfname')
            pdffile = request.FILES.get('pdffile', False)

            if (maingroup != '0'):
                group_id1 = Group.objects.get(id=maingroup)
                
            if (subgroup != '0'):
                group_id2 = Group.objects.get(id=subgroup)




       
            try:
                s = SignPDFFiles_db.objects.get(id=id)


                existing_record = SignPDFFiles_db.objects.filter(
                    signfile_Date=date,
                    Aircraft_Type=s.Aircraft_Type,
                    Aircraft_Reg=s.Aircraft_Reg
                ).exclude(id=id).exists()

                if existing_record:
                    request.session['saved_message'] = 'File with this information already exists'
                    return redirect(dailyForm)



                s.signfile_Date = date   

                if (maingroup != '0'):
                    group_id1 = Group.objects.get(id=maingroup)            
                    s.Aircraft_Type = group_id1   

                if (subgroup != '0'):
                    group_id2 = Group.objects.get(id=subgroup)                 
                    s.Aircraft_Reg = group_id2   

                s.signfile_Name = pdfname 
                s.save()

                

                if pdffile:
                    # Save the new file
                    s.signpdf_file = pdffile
                    s.save()  # Save first to ensure the file is uploaded to the specified location

                    # Generate a new file name
                    random_string = ''.join(random.choices(string.ascii_letters, k=10))
                    new_file_name = f"{s.id}{random_string}.pdf"

                    # Construct the old and new file paths
                    old_file_path = s.signpdf_file.path
                    new_file_path = os.path.join(os.path.dirname(old_file_path), new_file_name)

                    # Check if the file exists before renaming
                    if os.path.exists(old_file_path):
                        os.rename(old_file_path, new_file_path)
                        s.signpdf_file.name = os.path.join(os.path.dirname(s.signpdf_file.name), new_file_name)
                        s.save()
                    else:
                        print(f"Error: File does not exist at {old_file_path}")
                        request.session['saved_message'] = f"File update failed. Original file not found."
                        return redirect(dailyForm)


                saveNotify(f"{pdfname} File uploaded successfully",'success')
                
                request.session['saved_message'] = 'File updated successfully'
                return redirect(dailyForm)
            except Exception as e:
                print(str(e))
                request.session['saved_message'] = 'Error in uploading file' + str(e)
                return redirect(dailyForm)
        else: 
            request.session['saved_message'] = 'Something wrong check the entered value' 
            return redirect(dailyForm)

  
    else:
        return redirect('/')
    

def delete_signFile(request,id): 
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
            admin = User.objects.get(id=Adm_id)
            s = SignPDFFiles_db.objects.get(id=id)
            s.delete()
            request.session['saved_message'] = 'Sign file deleted successfully'
            saveNotify(f"Sign file deleted successfully",'danger')
            return redirect(dailyForm)
        else:
            return redirect('/')






# New Update Create an new admin

def new_admins(request):
    if 'Adm_id' in request.session:
        Adm_id = request.session['Adm_id'] 
        try:
            admins = User.objects.get(id=Adm_id)  
            # admin = User.objects.filter(id=Adm_id) 
            admin = User.objects.filter(id=Adm_id, is_active=True)
            if not admin:
                return redirect('/')
        except User.DoesNotExist:
            request.session['saved_message'] = 'Invalid admin ID'
            return redirect('/') 
        if not admins.is_superuser:  
            request.session['saved_message'] = 'You are not a superadmin'
            return redirect(dashboard)  
        adminusers = User.objects.filter(is_superuser=False)
        saved_message = request.session.pop('saved_message', None) 
        return render(request, 'admin/new_admins.html', {'saved_message':saved_message,'admins': admins,'admin':admin,'adminusers':adminusers}) 
    return redirect('/')


def save_new_user(request):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        admin = User.objects.filter(id=Adm_id)  
        if request.method == 'POST':
            name = request.POST.get('name')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            status = request.POST.get('status')

            if User.objects.filter(username=username).exists():
                request.session['saved_message'] = 'User username already exists'
                return redirect(new_admins)

            if User.objects.filter(email=email).exists():
                request.session['saved_message'] = 'User email already exists'
                return redirect(new_admins)
 
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = name 
            user.last_name = password  
            user.is_superuser = False
            user.is_staff = True   
            user.is_active = status     
            user.save()

            request.session['saved_message'] = 'New user created successfully'
            return redirect(new_admins)
        
    return redirect('/')



def update_new_user(request, id):
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id']
        
        admin = User.objects.filter(id=Adm_id)  
        user =User.objects.get(id=id) 
        
        if request.method == 'POST':
            name = request.POST.get('name')
            email = request.POST.get('email')
            username = request.POST.get('username')
            password = request.POST.get('password')
            status = request.POST.get('status')


            if User.objects.filter(username=username).exclude(id=id).exists():
                request.session['saved_message'] = 'Update Error : User username already exists'
                return redirect(new_admins)

            if User.objects.filter(email=email).exclude(id=id).exists():
                request.session['saved_message'] = 'Update Error : User email already exists'
                return redirect(new_admins)
            
            # Update user details
            user.first_name = name
            user.email = email
            user.username = username
            if password: 
                user.set_password(password)
            user.is_active = status
            user.last_name = password
            user.save()

            request.session['saved_message'] = 'User updated successfully'
            return redirect(new_admins)  
        
    return redirect('/')



def delete_new_user(request, id): 
    if 'Adm_id' in request.session:
        if request.session.has_key('Adm_id'):
            Adm_id = request.session['Adm_id'] 
        admin = User.objects.filter(id=Adm_id)  
        user =User.objects.get(id=id) 
        user.delete() 
        request.session['saved_message'] = 'User deleted successfully'
        return redirect(new_admins)  
    return redirect('/')

 