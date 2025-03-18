from django.db import models
from django.contrib.auth.models import User
# Create your models here. 

class Designation(models.Model):
    designation = models.CharField(max_length=100)
    count = models.CharField(max_length=20,null=True) 
    def __str__(self):
        return self.designation

class Group(models.Model):
    group_name = models.CharField(max_length=100) 
    parent_group = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='child_groups')
    def __str__(self):
        return self.group_name

class AppUser(models.Model): 
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True)
    # group_is = models.ForeignKey(Group, on_delete=models.CASCADE, null=True)
    groups = models.ManyToManyField(Group, related_name='app_users')
    firstname = models.CharField(max_length=255)
    lastname = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    gender = models.CharField(max_length=10)
    dob = models.DateTimeField(max_length=240, null=True)
    age = models.CharField(max_length=20)
    profile_pic = models.FileField(upload_to='profile/', null=True, blank=True)
    user_sign = models.FileField(upload_to='user_sign/', null=True, blank=True)
    
    weight = models.CharField(max_length=20, default = '0')
    # designation = models.CharField(max_length=200, null=True)
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    last_logined = models.DateField(null=True, blank=True)
    device_token = models.TextField()
    user_status = models.CharField(max_length=10, default='1') 
    status = models.CharField(max_length=10, default='1')

    def __str__(self):
        return self.username
 
# class Category(models.Model):
#     category_name = models.CharField(max_length=100)
#     parent_category = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='children_categories')
#     sub_parent_category = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='sub_children_categories')
#     subchild_parent_category = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='subchild_parent_categories')

#     def __str__(self):
#         return self.category_name


class Category(models.Model):
    category_name = models.CharField(max_length=100)
    parent_category = models.ForeignKey('self',on_delete=models.CASCADE,null=True,blank=True,related_name='children_categories')
    def __str__(self):
        return self.category_name

class PDFfiles(models.Model):
    group_is = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True)
    category_is = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    pdf_name = models.CharField(max_length=100)
    pdf_file = models.FileField(upload_to='pdf/', null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    role = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=10, default='1') 
    def __str__(self):
        return self.pdf_name

class Notification_db(models.Model):
    notification = models.TextField()
    color = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='1')
    def __str__(self):
        return self.notification


class Apps_db(models.Model):
    app_name = models.CharField(max_length=100,null=True)
    app_url = models.CharField(max_length=100,null=True)
    app_icon = models.FileField(upload_to='app_icons/', null=True, blank=True) 
    color = models.CharField(max_length=100,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='1')
    def __str__(self):
        return self.app_name

class Forms_db(models.Model):
    form_ref_no = models.CharField(max_length=100,null=True)
    form_Id = models.CharField(max_length=100,null=True)
    form_Name = models.CharField(max_length=240,null=True)
    form_Date = models.DateField(blank=True, null=True)
    user_is = models.ForeignKey(AppUser, on_delete=models.SET_NULL, null=True)
    Aircraft_Type = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name="aircraft_type")
    Aircraft_Reg = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name="aircraft_reg")
    formData = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='1')
    def __str__(self):
        return self.form_ref_no
        
        
# sign Form

class SignPDFFiles_db(models.Model):
    signfile_Id = models.CharField(max_length=100,null=True)
    signfile_Name = models.CharField(max_length=240,null=True)
    signfile_Date = models.DateField(blank=True, null=True)
    signature_count = models.CharField(max_length=10, default='0')
    Aircraft_Type = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name="signaircraft_type")
    Aircraft_Reg = models.ForeignKey(Group, on_delete=models.SET_NULL, null=True, related_name="signaircraft_reg")  
    signpdf_file = models.FileField(upload_to='sign-pdf/', null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='1')

    #def __str__(self):
       # return self.signfile_Name
    
class SignedCaptFiles_db(models.Model):
    signFile_is = models.ForeignKey(SignPDFFiles_db, on_delete=models.SET_NULL, null=True)
    user_is = models.ForeignKey(AppUser, on_delete=models.SET_NULL, null=True)
    signedpdf_file = models.FileField(upload_to='captsigned-files/', null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, default='1')
