from django.urls import path
from falcon_admin import views

urlpatterns = [
    path('admin_navbar', views.admin_navbar, name='admin_navbar'),
    path('dashboard', views.dashboard, name='dashboard'),                   #dashboard
    path('users', views.users, name='all-users'),                               #users
    path('users/create', views.create_user, name='create_user'),            #user create
    path('users/save', views.save_user, name='save_user'),                  #save user
    path('users/view/<int:id>',views.view_user,name="view_user"),
    path('users/update/<int:id>',views.update_user,name="update_user"),
    path('users/updatePasscord/<int:id>',views.updatePasscord,name="updatePasscord"),
    path('users/statusUpdate/<int:id>/<str:type>',views.statusUpdate,name="statusUpdate"),
    path('users/updateGroup/<int:id>',views.updateUserGruop,name="updateUserGruop"),
    path('users/updateSign/<int:id>',views.updateUserSign,name="updateUserSign"),

    path('designation',views.designation,name="designation"),               #designation
    path('save_designation',views.save_designation,name="save_designation"),
    path('delete_designation/<int:id>',views.delete_designation,name="delete_designation"),

    path('groups',views.groups,name="groups"),                              #groups
    path('save_group',views.save_group,name="save_group"),
    path('delete_group/<int:id>',views.delete_group,name="delete_group"),

    path('category', views.category, name='category'),                      #category
    path('save_category',views.save_category,name="save_category"),
    path('delete_category/<int:id>',views.delete_category,name="delete_category"),

    path('file-manager',views.filemanager,name="filemanager"),              #filemanager
    path('file-manager/upload',views.fileupload,name="fileupload"),
    path('savefile',views.savefile,name="savefile"), 
    path('file-manager/view/<int:id>',views.viewfile,name="viewfile"),
    path('change_file_status/<int:id>',views.change_file_status,name="change_file_status"),
    path('update_details_pdf/<int:id>',views.update_details_pdf,name="update_details_pdf"),
    path('delete_file/<int:id>',views.delete_file,name="delete_file"),

    path('delete-multiple-files/', views.delete_multiple_files, name='delete_multiple_files'),

 
    path('update',views.admin_update_details,name="admin_update_details"),
    path('admin_update_save',views.admin_update_save,name="admin_update_save"),

    path('apps',views.home_apps,name="home_apps"),
    path('save_app',views.save_app,name="save_app"),
    path('update_app/<int:id>',views.update_app,name="update_app"),
    path('delete_app/<int:id>',views.delete_app,name="delete_app"),
    
# Module 2
    path('forms',views.forms,name="forms"),
    path('form',views.form,name="form"),
    path('form/view',views.viewForm,name="viewForm"),
    
    path('forms/manage/signform', views.dailyForm ,name="dailyForm"),

    path('save_dailyForm',views.save_dailyForm,name="save_dailyForm"),
    path('update_dailyForm/<int:id>',views.update_dailyForm,name="update_dailyForm"),
    path('delete_signFile/<int:id>',views.delete_signFile,name="delete_signFile"),
    
    
# New Update Create an new admin
    path('admins', views.new_admins ,name="new_admins"),
    path('save_new_user', views.save_new_user ,name="save_new_user"),
    path('update_new_user/<int:id>', views.update_new_user ,name="update_new_user"),
    path('delete_new_user/<int:id>', views.delete_new_user ,name="delete_new_user"),
    
 
]