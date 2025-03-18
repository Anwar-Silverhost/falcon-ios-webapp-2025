from collections import defaultdict
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.response import Response
from rest_framework import status
from app.models import *
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from datetime import datetime
import re

from api.v1.token import *
from api.v1.permissions import *


from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from io import BytesIO


regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


#=================================== Token Cheking ================================================



#================================================================================================== 



# LOGIN SECTION ======================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
class LoginView(APIView):
    permission_classes = [TokenBasedAuthentication]

    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        group_id = request.data.get("group")
        password = request.data.get("password")

        try:
            user = AppUser.objects.get(email=email)
            if user.user_status == '1':
                if user.password == password:
                    if user.groups.filter(id=group_id).exists(): 
                        user.last_logined = datetime.now()
                        user.device_token = 'login'
                        user.save()  
                        dob_formatted = (
                            user.dob.strftime("%Y-%m-%d") if user.dob else None
                        )
                        user_details = {
                            "status": "success",
                            "message": "Login successful",
                            "data": {
                                "id": user.id,
                                "firstname": user.firstname,
                                "lastname": user.lastname,
                                "designation":user.designation.designation,
                                "email": user.email,
                                "username": user.username,
                                "password": user.password,
                                "phone": user.phone,
                                "gender": user.gender,
                                "dob": dob_formatted,
                                "age": user.age,
                                "profile_pic": request.build_absolute_uri(user.profile_pic.url)
                                if user.profile_pic
                                else None,
                                "location": user.location,
                                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                                "last_logined": user.last_logined.strftime("%Y-%m-%d %H:%M:%S"),
                                "device_token": user.device_token,
                                "user_status": user.user_status,
                                "status": user.status,
                                "groups": list(user.groups.values("id", "group_name")),
                            },
                        }
                        return Response(user_details, status=status.HTTP_200_OK)
                    else:
                        return Response(
                            {
                                "status": "error",
                                "message": "The selected group is not recognized",
                            },
                            status=status.HTTP_400_BAD_REQUEST,
                        )
                else:
                    return Response(
                        {
                            "status": "error",
                            "message": "Invalid Password",
                        },
                        status=status.HTTP_400_BAD_REQUEST,
                    )
            else:
                return Response(
                    {
                        "status": "error",
                        "message": "This account is currently inactive",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except AppUser.DoesNotExist:
            return Response(
                {
                    "status": "error",
                    "message": "No account found with the provided detail",
                },
                status=status.HTTP_404_NOT_FOUND,
            )





# EMAIL SECTION ======================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
class EmailCheck(APIView):
    def get(self, request, *args, **kwargs):
        email = request.query_params.get("email")
        if email:
            if AppUser.objects.filter(email=email).exists():
                user = AppUser.objects.get(email=email)
 
                # refresh = RefreshToken.for_user(user)

                tokenis = generate_token(user.id)
 
                user_groups = user.groups.all()
                groups_data = [
                    {"id": group.id, "name": group.group_name} for group in user_groups
                ]
                context = {
                    "status": "success",
                    "message": "Email Exists",
                    "data": {
                        "id": user.id,
                        "name": f"{user.firstname} {user.lastname}",
                        "email": user.email,
                        "mobile": user.phone,
                        "user_status": user.user_status,
                        "groups": groups_data,
                    },
                    "token":f"{tokenis}"

                    # "tokens": {
                    #     "refresh": str(refresh),
                    #     "access": str(refresh.access_token),
                    # },
                }
                return Response(context, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"status": "error", "message": "Email Not Found"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        else:
            return Response(
                {"status": "error", "message": "Email parameter is missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )




# GROUP SECTION ======================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
class Groups(APIView): 
    # permission_classes = [IsAuthenticated]
    permission_classes = [TokenBasedAuthentication]


    def get(self, request, group_id=None):
 
        if request.resolver_match.url_name == "group-detail" and group_id:
            return self.get_group_detail(group_id)
        elif request.resolver_match.url_name == "main-group-list":
            return self.main_groups()
        elif request.resolver_match.url_name == "subgroup-list" and group_id:
            return self.sub_groups(group_id)
        else:
            return self.get_all_groups()

    def get_group_detail(self, group_id):
        group = get_object_or_404(Group, id=group_id)
        group_data = {
            "id": group.id,
            "group_name": group.group_name,
            "parent_group": group.parent_group.id if group.parent_group else None,
        }
        return Response(group_data)

    def get_all_groups(self):
        groups = Group.objects.all()
        groups_data = [
            {
                "id": group.id,
                "group_name": group.group_name,
                "parent_group": group.parent_group.id if group.parent_group else None,
            }
            for group in groups
        ]
        return Response(groups_data)

    def main_groups(self):
        main_groups = Group.objects.filter(parent_group__isnull=True)
        main_groups_data = [
            {
                "id": group.id,
                "group_name": group.group_name,
            }
            for group in main_groups
        ]
        return Response(main_groups_data)

    def sub_groups(self, group_id):
        main_group = get_object_or_404(Group, id=group_id, parent_group__isnull=True)
        sub_groups = main_group.child_groups.all()
        sub_groups_data = [
            {
                "id": group.id,
                "group_name": group.group_name,
            }
            for group in sub_groups
        ]
        return Response(sub_groups_data)



# USERS SECTION ======================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
class AllUsers(APIView):
    permission_classes = [TokenBasedAuthentication]
    def get(self, request):
        users = AppUser.objects.all() 
        users_data = [
            { 
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "designation":user.designation.designation,
                "email": user.email,
                "username": user.username,
                "password": user.password,
                "phone": user.phone,
                "gender": user.gender,
                "dob": user.dob.strftime("%Y-%m-%d") if user.dob else None,
                "age": user.age,
                "profile_pic": request.build_absolute_uri(user.profile_pic.url)
                if user.profile_pic
                else None,
                "location": user.location,
                "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") ,
                "last_logined": user.last_logined.strftime("%Y-%m-%d %H:%M:%S")if user.last_logined else None,
                "device_token": user.device_token,
                "user_status": user.user_status,
                "status": user.status,
                "groups": list(user.groups.values("id", "group_name")),
            
            }
                for user in users
                ]
        return Response({"status": "success", "message": "Fetched all users successfully",
                "users": users_data})
        
       


# USER-DETAILS SECTION ======================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
class UserDetails(APIView):
    permission_classes = [TokenBasedAuthentication]

    # Fetch user details (GET method)
    def get(self, request, user_id): 
        try:
            user = get_object_or_404(AppUser, id=user_id)
            dob_formatted = user.dob.strftime("%Y-%m-%d") if user.dob else None

            user_details = {
                "status": "success",
                "message": "User details fetched successfully",
                "data": {
                    "id": user.id,
                    "firstname": user.firstname,
                    "lastname": user.lastname,
                    "designation":user.designation.designation,
                    "email": user.email,
                    "username": user.username,
                    "password": user.password,
                    "phone": user.phone,
                    "gender": user.gender,
                    "dob": dob_formatted,
                    "age": user.age,
                    "profile_pic": request.build_absolute_uri(user.profile_pic.url)
                    if user.profile_pic
                    else None,
                    "location": user.location,
                    "created_at": user.created_at.strftime("%Y-%m-%d %H:%M:%S") ,
                    "last_logined": user.last_logined.strftime("%Y-%m-%d %H:%M:%S"),
                    "device_token": user.device_token,
                    "user_status": user.user_status,
                    "status": user.status,
                    "groups": list(user.groups.values("id", "group_name")),
                },
            }
            return Response(user_details, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {"status": "error", "message": 'Invalid User'},
                status=status.HTTP_400_BAD_REQUEST,
                )

    # Update profile details (PUT method)
    def put(self, request,user_id, *args, **kwargs):
        user = get_object_or_404(AppUser, id=user_id)
 
        # Update profile fields
        firstname = request.data.get("firstname")
        lastname = request.data.get("lastname")
        email = request.data.get("email")
        phone = request.data.get("phone")
        gender = request.data.get("gender")
        dob = request.data.get("dob") 
        location = request.data.get("location")
        profile_pic = request.FILES.get("profile_pic")

        try: 
            if firstname:
                user.firstname = firstname
            if lastname:
                user.lastname = lastname
            if phone:
                user.phone = phone
            if email:
                if AppUser.objects.filter(email=email).exclude(id=user_id).exists():
                    return Response(
                        {"status": "error", "message": "Email already exists"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )
                elif re.fullmatch(regex, email):
                    user.email = email
                else:
                    return Response(
                        {"status": "error", "message": "Invalid email address"},
                        status=status.HTTP_400_BAD_REQUEST,
                    ) 
            if gender:
                user.gender = gender
            if dob:
                try:
                    user.dob = datetime.strptime(dob, "%Y-%m-%d")
                except ValueError:
                    return Response(
                        {"status": "error", "message": "Invalid date format"},
                        status=status.HTTP_400_BAD_REQUEST,
                    )

            if location:
                user.location = location
            if profile_pic:
                print(profile_pic)
                user.profile_pic = profile_pic

            user.save()

            dob_formatted = user.dob.strftime("%Y-%m-%d") if user.dob else None

            return Response(
                {"status": "success", "message": "Profile updated successfully",
                "data": {
                "id": user.id,
                "firstname": user.firstname,
                "lastname": user.lastname,
                "designation":user.designation.designation,
                "email": user.email, 
                "phone": user.phone,
                "gender": user.gender,
                "dob": dob_formatted,
                "age": user.age,
                "profile_pic": request.build_absolute_uri(user.profile_pic.url)
                if user.profile_pic
                else None,
                "location": user.location, 
            },},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
                )


    # Change password (PATCH method)
    def patch(self, request,user_id, *args, **kwargs):
        user = get_object_or_404(AppUser, id=user_id)
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")

        try: 
            if old_password == user.password:
                if old_password != new_password:
                    user.password = new_password
                    user.save()
                    return Response(
                        {"status": "success", "message": "Password updated successfully"},
                        status=status.HTTP_200_OK,
                        ) 
                else:
                    return Response(
                    {"status": "error", "message": "New password cannot be the same as the old password"},
                    status=status.HTTP_400_BAD_REQUEST,
                ) 
            else:
                return Response(
                    {"status": "error", "message": "Old password is incorrect"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        


# CATEGORY SECTION ======================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================



class Documents(APIView):
    permission_classes = [TokenBasedAuthentication]

    def get(self, request):
        group_id = request.query_params.get("group")
  
        response_data = []

        try:
            if group_id: 
                group_instance = get_object_or_404(Group, id=group_id)
 
                main_group = group_instance
                while main_group.parent_group is not None:
                    main_group = main_group.parent_group 
                 
                group_files = PDFfiles.objects.filter(group_is=group_instance, status=1) 
                main_group_files = PDFfiles.objects.filter(group_is=main_group, status=1) 

                # Combine both querysets
                files = group_files | main_group_files
                print(files)

            else: 
                files = PDFfiles.objects.none()

            # Function to build category tree structure
            def build_category_tree(category):
                children = []
                subcategories = Category.objects.filter(parent_category=category)
                for subcategory in subcategories:
                    child_node = build_category_tree(subcategory)
                    if child_node:
                        children.append(child_node)
                if children or files.filter(category_is=category.id).exists():
                    return {
                        'name': category.category_name,
                        'type': 'folder',
                        'id': category.id,
                        'children': children
                    }
                return None

            # Function to add files to the appropriate categories
            def add_files_to_category(category_node):
                if category_node is None:
                    return False
                
                documents = files.filter(category_is=category_node['id'])
                has_files = False
                for document in documents:
                    has_files = True
                    category_node['children'].append({
                        'id': document.id,
                        'name': document.pdf_name,
                        'type': 'document',
                        'url': request.build_absolute_uri(document.pdf_file.url) if document.pdf_file else None,
                        'group': {
                            'id': document.group_is.id if document.group_is else None,
                            'name': document.group_is.group_name if document.group_is else None
                        }
                    })
                # Recursively add files to children categories
                for child in category_node['children']:
                    if child['type'] == 'folder':
                        child_has_files = add_files_to_category(child)
                        if child_has_files:
                            has_files = True
                return has_files

            # Build the final response
            def build_response():
                root_categories = Category.objects.filter(parent_category__isnull=True)
                result = []
                for root_category in root_categories:
                    category_tree = build_category_tree(root_category)
                    if add_files_to_category(category_tree):  # Only include non-empty categories
                        result.append(category_tree)
                return result

            response_data = build_response()

            return Response({
                "status": "success",
                "message": "File details collected successfully",
                "data": response_data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


#this is the old code
# class Documents(APIView):
#     permission_classes = [TokenBasedAuthentication]


#     def get(self, request):
#         group_id = request.query_params.get("group")
#         response_data = []

#         try:
#             if group_id:
#                 # Ensure the group ID is valid and filter files accordingly
#                 group_instance = get_object_or_404(Group, id=group_id)
#                 files = PDFfiles.objects.filter(group_is=group_instance, status=1)
#             else:
#                 # No group ID provided, return an empty list
#                 files = PDFfiles.objects.none()

#             def build_category_tree(category):
#                 children = []
#                 subcategories = Category.objects.filter(parent_category=category)
#                 for subcategory in subcategories:
#                     child_node = build_category_tree(subcategory)
#                     if child_node:
#                         children.append(child_node)
#                 if children or files.filter(category_is=category.id).exists():
#                     return {
#                         'name': category.category_name,
#                         'type': 'folder',
#                         'id': category.id,
#                         'children': children
#                     }
#                 return None

#             def add_files_to_category(category_node):
#                 if category_node is None:
#                     return False
                
#                 documents = files.filter(category_is=category_node['id'])
#                 has_files = False
#                 for document in documents:
#                     has_files = True
#                     category_node['children'].append({
#                         'id': document.id,
#                         'name': document.pdf_name,
#                         'type': 'document',
#                         'url': request.build_absolute_uri(document.pdf_file.url) if document.pdf_file else None,
#                         'group': {
#                             'id': document.group_is.id if document.group_is else None,
#                             'name': document.group_is.group_name if document.group_is else None
#                         }
#                     })
#                 # Recursively add files to children categories
#                 for child in category_node['children']:
#                     if child['type'] == 'folder':
#                         child_has_files = add_files_to_category(child)
#                         if child_has_files:
#                             has_files = True
#                 return has_files

#             def build_response():
#                 root_categories = Category.objects.filter(parent_category__isnull=True)
#                 result = []
#                 for root_category in root_categories:
#                     category_tree = build_category_tree(root_category)
#                     if add_files_to_category(category_tree):  # Only include non-empty categories
#                         result.append(category_tree)
#                 return result

#             response_data = build_response()

#             return Response({
#                 "status": "success",
#                 "message": "File details collected successfully",
#                 "data": response_data
#             }, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": str(e)},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )



#     # def get(self, request):
#     #     group_id = request.query_params.get("group")
#     #     response_data = []

#     #     try:
#     #         if group_id:
#     #             # Ensure the group ID is valid and filter files accordingly
#     #             group_instance = get_object_or_404(Group, id=group_id)
#     #             files = PDFfiles.objects.filter(group_is=group_instance, status=1)
#     #         else:
#     #             # No group ID provided, return an empty list
#     #             files = PDFfiles.objects.none()

#     #         def build_category_tree(category):
#     #             children = []
#     #             subcategories = Category.objects.filter(parent_category=category)
#     #             for subcategory in subcategories:
#     #                 children.append(build_category_tree(subcategory))
#     #             return {
#     #                 'name': category.category_name,
#     #                 'type': 'folder',
#     #                 'id': category.id,
#     #                 'children': children
#     #             }

#     #         def add_files_to_category(category_node):
#     #             # Add files that belong to this category
#     #             documents = files.filter(category_is=category_node['id'])
#     #             for document in documents:
#     #                 category_node['children'].append({
#     #                     'name': document.pdf_name,
#     #                     'type': 'document',
#     #                     'url': request.build_absolute_uri(document.pdf_file.url) if document.pdf_file else None,
#     #                     'group': {
#     #                         'id': document.group_is.id if document.group_is else None,
#     #                         'name': document.group_is.group_name if document.group_is else None
#     #                     }
#     #                 })
#     #             # Recursively add files to children categories
#     #             for child in category_node['children']:
#     #                 if child['type'] == 'folder':
#     #                     add_files_to_category(child)

#     #         def build_response():
#     #             root_categories = Category.objects.filter(parent_category__isnull=True)
#     #             result = []
#     #             for root_category in root_categories:
#     #                 category_tree = build_category_tree(root_category)
#     #                 add_files_to_category(category_tree)
#     #                 result.append(category_tree)
#     #             return result

#     #         response_data = build_response()

#     #         return Response({
#     #             "status": "success",
#     #             "message": "File details collected successfully",
#     #             "data": response_data
#     #         }, status=status.HTTP_200_OK)

#     #     except Exception as e:
#     #         return Response(
#     #             {"status": "error", "message": str(e)},
#     #             status=status.HTTP_400_BAD_REQUEST,
#     #         )



#     # def get(self, request):
#     #     group_id = request.query_params.get("group")

#     #     if not group_id:
#     #         return Response(
#     #             {"status": "error", "message": "Group ID is required"},
#     #             status=status.HTTP_400_BAD_REQUEST
#     #         )

#     #     try:
#     #         group_instance = get_object_or_404(Group, id=group_id)

#     #         def get_group_path(group):
#     #             path = []
#     #             while group:
#     #                 path.append({"id": group.id, "name": group.group_name})
#     #                 group = group.parent_group
#     #             return path[::-1]

#     #         def get_files(category):
#     #             return [
#     #                 {
#     #                     "name": file.pdf_name,
#     #                     "type": "document",
#     #                     "url": request.build_absolute_uri(file.pdf_file.url)
#     #                 }
#     #                 for file in PDFfiles.objects.filter(
#     #                     category_is=category,
#     #                     group_is=group_instance,
#     #                     status=1
#     #                 )
#     #             ]

#     #         def construct_hierarchy(category):
#     #             hierarchy = {
#     #                 "name": category.category_name,
#     #                 "type": "folder",
#     #                 "children": []
#     #             }

#     #             # Add files of the current category
#     #             hierarchy['children'].extend(get_files(category))
                
#     #             # Add subcategories recursively
#     #             for subcategory in category.children_categories.all():
#     #                 hierarchy['children'].append(construct_hierarchy(subcategory))
                    
#     #             return hierarchy

#     #         # Collect top-level categories for the specific group
#     #         top_level_categories = Category.objects.filter(parent_category__isnull=True)
#     #         category_data = [construct_hierarchy(category) for category in top_level_categories]

#     #         # Get the group path for the response
#     #         group_path = get_group_path(group_instance)

#     #         # Formulate the response
#     #         response = {
#     #             "status": "success",
#     #             "message": "File details collected successfully",
#     #             "group": {
#     #                 "group": {
#     #                     "id": group_instance.id,
#     #                     "name": group_instance.group_name
#     #                 },
#     #                 "group_path": group_path
#     #             },
#     #             "folder": category_data
#     #         }

#     #         return Response(response, status=status.HTTP_200_OK)

#     #     except Exception as e:
#     #         return Response(
#     #             {"status": "error", "message": str(e)},
#     #             status=status.HTTP_500_INTERNAL_SERVER_ERROR
#     #         )
    
    
    
    
    
    
    
    
#     # # def get(self, request):
#     #     group_id = request.query_params.get("group")

#     #     print(group_id)
        
#     #     try:
#     #         # Ensure that group_id is provided
#     #         if group_id:
#     #             group_instance = get_object_or_404(Group, id=group_id)
#     #         else:
#     #             return Response(
#     #                 {"status": "error", "message": "Group ID is required"},
#     #                 status=status.HTTP_400_BAD_REQUEST
#     #             )

#     #         # Define method to get the group path
#     #         def get_group_path(group):
#     #             path = []
#     #             while group:
#     #                 path.append({"id": group.id, "name": group.group_name})
#     #                 group = group.parent_group
#     #             return path[::-1]

#     #         # Define method to get files for a given category and group
#     #         def get_files(category):
#     #             files = []
#     #             for file in PDFfiles.objects.filter(category_is=category, group_is=group_instance, status=1):
#     #                 files.append({
#     #                     "name": file.pdf_name,
#     #                     "type": "document",
#     #                     "url": request.build_absolute_uri(file.pdf_file.url)
#     #                 })
#     #             return files

#     #         # Define method to construct the hierarchy
#     #         def construct_hierarchy(category):
#     #             hierarchy = {
#     #                 "name": category.category_name,
#     #                 "type": "folder",
#     #                 "children": []
#     #             }

#     #             # Add files of the current category
#     #             files = get_files(category)
#     #             hierarchy['children'].extend(files)
                
#     #             # Add subcategories recursively
#     #             for subcategory in category.children_categories.all():
#     #                 subcategory_hierarchy = construct_hierarchy(subcategory)
#     #                 hierarchy['children'].append(subcategory_hierarchy)
                    
#     #             return hierarchy

#     #         # Collect top-level categories and their hierarchies for the specific group
#     #         top_level_categories = Category.objects.filter(parent_category__isnull=True)
#     #         category_data = [construct_hierarchy(category) for category in top_level_categories]

#     #         # Get the group path for the response
#     #         group_path = get_group_path(group_instance)

#     #         # Formulate the response
#     #         response = {
#     #             "status": "success",
#     #             "message": "File details collected successfully",
#     #             "group": {
#     #                 "group": {
#     #                     "id": group_instance.id,
#     #                     "name": group_instance.group_name
#     #                 },
#     #                 "group_path": group_path
#     #             },
#     #             "folder": category_data
#     #         }

#     #         return Response(response, status=status.HTTP_200_OK)

#     #     except Exception as e:
#     #         return Response(
#     #             {"status": "error", "message": str(e)},
#     #             status=status.HTTP_400_BAD_REQUEST,
#     #         )




# class Documents(APIView):
#     permission_classes = [TokenBasedAuthentication]

#     def get(self, request):
#         group_id = request.query_params.get("group")
        
#         try:
#             # Ensure that group_id is provided
#             if group_id:
#                 group_instance = get_object_or_404(Group, id=group_id)
#             else:
#                 return Response(
#                     {"status": "error", "message": "Group ID is required"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#             # Define the method to get the group path
#             def get_group_path(group): 
#                 path = []
#                 while group:
#                     path.append({"id": group.id, "name": group.group_name})
#                     group = group.parent_group
#                 return path[::-1]

#             # Define method to get subcategories
#             def get_subcategories(category):
#                 subcategories = []
#                 for subcategory in category.children_categories.all():
#                     subcategories.append({
#                         "id": subcategory.id,
#                         "name": subcategory.category_name,
#                         "files": get_files(subcategory),
#                         "subcategories": get_subcategories(subcategory)
#                     })
#                 return subcategories

#             # Define method to get files for the given category and group
#             def get_files(category):
#                 files = []
#                 for file in PDFfiles.objects.filter(category_is=category, group_is=group_instance, status=1):
#                     files.append({
#                         "id": file.id,
#                         "pdf_name": file.pdf_name,
#                         "pdf_file": request.build_absolute_uri(file.pdf_file.url),
#                         "created_at": file.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#                         "status": file.status,
#                     })
#                 return files

#             # Collect categories and their files for the specific group
#             category_data = []
#             for category in Category.objects.filter(parent_category__isnull=True):
#                 subcategories = get_subcategories(category)
#                 category_files = get_files(category)

#                 if subcategories or category_files:  # Include only if there are relevant subcategories or files
#                     category_data.append({
#                         "id": category.id,
#                         "name": category.category_name,
#                         "files": category_files,
#                         "subcategories": subcategories
#                     })

#             # Get the group path for the response
#             group_path = get_group_path(group_instance)

#             # Formulate the response
#             response = {
#                 "status": "success",
#                 "message": "File details collected successfully",
#                 "group": {
#                     "group": {
#                         "id": group_instance.id,
#                         "name": group_instance.group_name
#                     },
#                     "group_path": group_path
#                 },
#                 "folder": category_data
#             }

#             return Response(response, status=status.HTTP_200_OK)

#         except Exception as e:
#             return Response(
#                 {"status": "error", "message": str(e)},
#                 status=status.HTTP_400_BAD_REQUEST,
#             )














    # def get(self, request):
    #     group_id = request.query_params.get("group")
        
    #     try:
    #         # Fetch the group object based on the group_id
    #         if group_id: 
    #             group_instance = get_object_or_404(Group, id=group_id)
    #             files = PDFfiles.objects.filter(group_is=group_instance, status=1)
    #         else: 
    #             return Response(
    #                 {"status": "error", "message": "Group ID is required"},
    #                 status=status.HTTP_400_BAD_REQUEST
    #             )

    #         def get_group_path(group): 
    #             path = []
    #             while group:
    #                 path.append({"id": group.id, "name": group.group_name})
    #                 group = group.parent_group
    #             return path[::-1]   

    #         def get_category_path(category): 
    #             path = []
    #             while category:
    #                 path.append({"id": category.id, "name": category.category_name})
    #                 category = category.parent_category
    #             return path[::-1]

    #         def get_subcategories(category, group_instance):
    #             subcategories = []
    #             for subcategory in category.children_categories.all():
    #                 subcategories.append({
    #                     "id": subcategory.id,
    #                     "name": subcategory.category_name,
    #                     "files": get_files(subcategory, group_instance),
    #                     "subcategories": get_subcategories(subcategory, group_instance)
    #                 })
    #             return subcategories

    #         def get_files(category, group_instance):
    #             files = []
    #             for file in PDFfiles.objects.filter(category_is=category, group_is=group_instance, status=1):
    #                 files.append({
    #                     "id": file.id,
    #                     "pdf_name": file.pdf_name,
    #                     "pdf_file": request.build_absolute_uri(file.pdf_file.url),
    #                     "created_at": file.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    #                     "status": file.status,
    #                 })
    #             return files

    #         # Collect categories, files, and subcategories filtered by group
    #         category_data = []
    #         for category in Category.objects.filter(parent_category__isnull=True):
    #             subcategories = get_subcategories(category, group_instance)
    #             category_files = get_files(category, group_instance)
                
    #             if subcategories or category_files:  # Include only if there are relevant subcategories or files
    #                 category_data.append({
    #                     "id": category.id,
    #                     "name": category.category_name,
    #                     "files": category_files,
    #                     "subcategories": subcategories
    #                 })

    #         group_path = get_group_path(group_instance)

    #         # Formulate the response
    #         response = {
    #             "status": "success",
    #             "message": "File details collected successfully",
    #             "group": {
    #                 "group": {
    #                     "id": group_instance.id,
    #                     "name": group_instance.group_name
    #                 },
    #                 "group_path": group_path
    #             },
    #             "folder": category_data
    #         }

    #         return Response(response, status=status.HTTP_200_OK)

    #     except Exception as e:
    #         return Response(
    #             {"status": "error", "message": str(e)},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )



  
    # def get(self, request):
    #     group = request.query_params.get("group")
    #     response_data = []
 
    #     try:
    #         if group: 
    #             aircrafttype_instance = get_object_or_404(Group, id=group)
    #             files = PDFfiles.objects.filter(group_is=aircrafttype_instance).filter(status = 1)
    #         else: 
    #             files = PDFfiles.objects.all().filter(status = 1)

    #         def get_group_path(group): 
    #             path = []
    #             while group:
    #                 path.append({"id": group.id, "name": group.group_name})
    #                 group = group.parent_group
    #             return path[::-1]   

    #         def get_category_path(category): 
    #             path = []
    #             while category:
    #                 path.append({"id": category.id, "name": category.category_name})
    #                 category = category.parent_category
    #             return path[::-1]  

    #         for file in files: 
    #             group_path = get_group_path(file.group_is) if file.group_is else []
    #             category_path = get_category_path(file.category_is) if file.category_is else [] 
    #             file_data = {
    #                 "id": file.id,
    #                 "pdf_name": file.pdf_name,
    #                 "pdf_file": request.build_absolute_uri(file.pdf_file.url) if file.pdf_file else None,
    #                 "created_at": file.created_at.strftime("%Y-%m-%d %H:%M:%S"),
    #                 "status": file.status,
    #                 "group": {
    #                     "id": file.group_is.id if file.group_is else None,
    #                     "name": file.group_is.group_name if file.group_is else None
    #                 },
    #                 "group_path": group_path,
    #                 "category": {
    #                     "id": file.category_is.id if file.category_is else None,
    #                     "name": file.category_is.category_name if file.category_is else None
    #                 }, 
    #                 "category_path": category_path
    #             }
    #             response_data.append(file_data)

    #         return Response({"status": "success", "message": "File details collected successfully", "data": response_data}, status=status.HTTP_200_OK)

    #     except Exception as e:
    #         return Response(
    #             {"status": "error", "message": str(e)},
    #             status=status.HTTP_400_BAD_REQUEST,
    #         )






# Application SECTION ======================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================

class Application(APIView):
    permission_classes = [TokenBasedAuthentication]

    def get(self, request):
        try: 
            apps = Apps_db.objects.all() 
            apps_data = []
            for app in apps:
                app_icon_url = request.build_absolute_uri(app.app_icon.url) if app.app_icon else None
                
                apps_data.append({
                    'app_name': app.app_name,
                    'app_url': app.app_url,
                    'app_icon': app_icon_url,
                    'color': app.color,
                    'created_at': app.created_at,
                    'status': app.status,
                })

            return Response(
                {"status": "success","message": "Application fetched successfully", "data": apps_data},
                status=status.HTTP_200_OK
            )

        except Exception as e:
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )







# module 2 :

# FORM SECTION ======================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
class FormData(APIView):
    permission_classes = [TokenBasedAuthentication]

  
    def get(self, request): 
        formid = request.query_params.get('formid')  
        date = request.query_params.get('date')  
        user_id = request.query_params.get('userid')  

        aircrafttype = request.query_params.get('aircrafttype')  
        aircraftreg = request.query_params.get('aircraftreg')  


        try:
            user = AppUser.objects.get(id=user_id)
            parsed_date = datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")
            aircrafttype = Group.objects.get(id=aircrafttype)
            aircraftreg = Group.objects.get(id=aircraftreg)

        except AppUser.DoesNotExist:
            return Response(
                {"status": "error", "message": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )
 
 
         
        if formid == 'FAF01': 
            parsed_date_obj = datetime.strptime(parsed_date, "%Y-%m-%d").date()
            formdata = Forms_db.objects.filter(user_is=user, form_Id=formid, form_Date=parsed_date_obj).first()

            if formdata:
                response_data = {
                    "formId": formdata.id,
                    "form_ref_no": formdata.form_ref_no,
                    "form_id": formdata.form_Id,
                    "form_name": formdata.form_Name,
                    "form_date": formdata.form_Date,
                    "form_data":formdata.formData,
                    "form_status": formdata.status,
                }
                return Response({
                    "status": "success",
                    "message": "File details collected successfully",
                    "data": response_data
                }, status=status.HTTP_200_OK)
            else:
                f = Forms_db()
                f.user_is = user
                f.form_Id = formid
                f.form_Name = "Aircraft Search Checklist"
                f.form_Date = parsed_date_obj
                f.Aircraft_Type = aircrafttype
                f.Aircraft_Reg = aircraftreg
                f.status = 'notcompleted'
                f.save()
                f.form_ref_no = "FA-ASC" + str(f.id).zfill(3)
                f.save()

                formdata = Forms_db.objects.get(id=f.id)

                context = {
                    "formId": formdata.id,
                    "form_ref_no": formdata.form_ref_no,
                    "form_id": formdata.form_Id,
                    "form_date": formdata.form_Date, 
                    "form_status": formdata.status,
                }

                return Response({
                    "status": "success",
                    "message": "File created successfully",
                    "data": context
                }, status=status.HTTP_200_OK)
            

        elif formid == 'FAF02': 
            parsed_date_obj = datetime.strptime(parsed_date, "%Y-%m-%d").date()
            formdata = Forms_db.objects.filter(user_is=user, form_Id=formid, form_Date=parsed_date_obj).first()

            if formdata:
                response_data = {
                    "formId": formdata.id,
                    "form_ref_no": formdata.form_ref_no,
                    "form_id": formdata.form_Id,
                    "form_name": formdata.form_Name,
                    "form_date": formdata.form_Date,
                    "form_data":formdata.formData,
                    "form_status": formdata.status,
                }
                return Response({
                    "status": "success",
                    "message": "File details collected successfully",
                    "data": response_data
                }, status=status.HTTP_200_OK)
            else:
                f = Forms_db()
                f.user_is = user
                f.form_Id = formid
                f.form_Name = "Rotary Wing Journy Log"
                f.form_Date = parsed_date_obj
                f.Aircraft_Type = aircrafttype
                f.Aircraft_Reg = aircraftreg
                f.status = 'notcompleted'
                f.save()
                f.form_ref_no = "FA-RWJL" + str(f.id).zfill(3)
                f.save()

                formdata = Forms_db.objects.get(id=f.id)

                context = {
                    "formId": formdata.id,
                    "form_ref_no": formdata.form_ref_no,
                    "form_id": formdata.form_Id,
                    "form_date": formdata.form_Date, 
                    "form_status": formdata.status,
                }

                return Response({
                    "status": "success",
                    "message": "File created successfully",
                    "data": context
                }, status=status.HTTP_200_OK)

        elif formid == 'FAF03': 
            parsed_date_obj = datetime.strptime(parsed_date, "%Y-%m-%d").date()
            formdata = Forms_db.objects.filter(user_is=user, form_Id=formid, form_Date=parsed_date_obj).first()

            if formdata:
                response_data = {
                    "formId": formdata.id,
                    "form_ref_no": formdata.form_ref_no,
                    "form_id": formdata.form_Id,
                    "form_name": formdata.form_Name,
                    "form_date": formdata.form_Date,
                    "form_data":formdata.formData,
                    "form_status": formdata.status,
                }
                return Response({
                    "status": "success",
                    "message": "File details collected successfully",
                    "data": response_data
                }, status=status.HTTP_200_OK)
            else:
                f = Forms_db()
                f.user_is = user
                f.form_Id = formid
                f.form_Name = "Operational Flight Plan"
                f.form_Date = parsed_date_obj
                f.Aircraft_Type = aircrafttype
                f.Aircraft_Reg = aircraftreg
                f.status = 'notcompleted'
                f.save()
                f.form_ref_no = "FA-OFP" + str(f.id).zfill(3)
                f.save()

                formdata = Forms_db.objects.get(id=f.id)

                context = {
                    "formId": formdata.id,
                    "form_ref_no": formdata.form_ref_no,
                    "form_id": formdata.form_Id,
                    "form_date": formdata.form_Date,  
                    "form_status": formdata.status,
                }

                return Response({
                    "status": "success",
                    "message": "File created successfully",
                    "data": context
                }, status=status.HTTP_200_OK)

        elif formid == 'FAF04': 
            parsed_date_obj = datetime.strptime(parsed_date, "%Y-%m-%d").date()
            formdata = Forms_db.objects.filter(user_is=user, form_Id=formid, form_Date=parsed_date_obj).first()

            if formdata:
                response_data = {
                    "formId": formdata.id,
                    "form_ref_no": formdata.form_ref_no,
                    "form_id": formdata.form_Id,
                    "form_name": formdata.form_Name,
                    "form_date": formdata.form_Date,
                    "form_data":formdata.formData,
                    "form_status": formdata.status,
                }
                return Response({
                    "status": "success",
                    "message": "File details collected successfully",
                    "data": response_data
                }, status=status.HTTP_200_OK)
            else:
                f = Forms_db()
                f.user_is = user
                f.form_Id = formid
                f.form_Name = "Commercial Flight Record"
                f.form_Date = parsed_date_obj
                f.Aircraft_Type = aircrafttype
                f.Aircraft_Reg = aircraftreg
                f.status = 'notcompleted'
                f.save()
                f.form_ref_no = "FA-CFR" + str(f.id).zfill(3)
                f.save()

                formdata = Forms_db.objects.get(id=f.id)

                context = {
                    "formId": formdata.id,
                    "form_ref_no": formdata.form_ref_no,
                    "form_id": formdata.form_Id,
                    "form_date": formdata.form_Date,  
                    "form_status": formdata.status,
                }

                return Response({
                    "status": "success",
                    "message": "File created successfully",
                    "data": context
                }, status=status.HTTP_200_OK)
            


        elif formid == 'FAF05': 
            parsed_date_obj = datetime.strptime(parsed_date, "%Y-%m-%d").date()
            formdata = Forms_db.objects.filter(user_is=user, form_Id=formid, form_Date=parsed_date_obj).first()

            if formdata:
                response_data = {
                    "formId": formdata.id,
                    "form_ref_no": formdata.form_ref_no,
                    "form_id": formdata.form_Id,
                    "form_name": formdata.form_Name,
                    "form_date": formdata.form_Date,
                    "form_data":formdata.formData,
                    "form_status": formdata.status,
                }
                return Response({
                    "status": "success",
                    "message": "File details collected successfully",
                    "data": response_data
                }, status=status.HTTP_200_OK)
            else:
                f = Forms_db()
                f.user_is = user
                f.form_Id = formid
                f.form_Name = "Commanders Discretion Report"
                f.form_Date = parsed_date_obj
                f.Aircraft_Type = aircrafttype
                f.Aircraft_Reg = aircraftreg
                f.status = 'notcompleted'
                f.save()
                f.form_ref_no = "FA-CDR" + str(f.id).zfill(3)
                f.save()

                formdata = Forms_db.objects.get(id=f.id)

                context = {
                    "formId": formdata.id,
                    "form_ref_no": formdata.form_ref_no,
                    "form_id": formdata.form_Id,
                    "form_date": formdata.form_Date,  
                    "form_status": formdata.status,
                }

                return Response({
                    "status": "success",
                    "message": "File created successfully",
                    "data": context
                }, status=status.HTTP_200_OK)
                
        elif formid == 'FAF06': 
            parsed_date_obj = datetime.strptime(parsed_date, "%Y-%m-%d").date()
            formdata = Forms_db.objects.filter(user_is=user, form_Id=formid, form_Date=parsed_date_obj).first()

            if formdata:
                response_data = {
                    "formId": formdata.id,
                    "form_ref_no": formdata.form_ref_no,
                    "form_id": formdata.form_Id,
                    "form_name": formdata.form_Name,
                    "form_date": formdata.form_Date,
                    "form_data":formdata.formData,
                    "form_status": formdata.status,
                }
                return Response({
                    "status": "success",
                    "message": "File details collected successfully",
                    "data": response_data
                }, status=status.HTTP_200_OK)
            else:
                f = Forms_db()
                f.user_is = user
                f.form_Id = formid
                f.form_Name = "Rotary Wing Flight Plan Envelop"
                f.form_Date = parsed_date_obj
                f.Aircraft_Type = aircrafttype
                f.Aircraft_Reg = aircraftreg
                f.status = 'notcompleted'
                f.save()
                f.form_ref_no = "FA-RWFPE" + str(f.id).zfill(3)
                f.save()

                formdata = Forms_db.objects.get(id=f.id)

                context = {
                    "formId": formdata.id,
                    "form_ref_no": formdata.form_ref_no,
                    "form_id": formdata.form_Id,
                    "form_date": formdata.form_Date,  
                    "form_status": formdata.status,
                }

                return Response({
                    "status": "success",
                    "message": "File created successfully",
                    "data": context
                }, status=status.HTTP_200_OK)

        
 

    def post(self, request, *args, **kwargs): 
        formid = request.GET.get('formid')
        print(formid)
        formrefno = request.GET.get('formrefno')
        
        print(formrefno)
         
        try:
            body = json.loads(request.body.decode('utf-8'))

            print(body)
            data = body.get("data", {})

            if "tableValues" in data and isinstance(data["tableValues"], str):
                data["tableValues"] = json.loads(data["tableValues"])

            
            formis = Forms_db.objects.get(form_ref_no = formrefno)
            formis.formData = data


            if formid == 'FAF04':
                statusx = body.get("status", {})   
                formis.status = statusx
            elif formid == 'FAF02':
                statusx = body.get("status", {})
                formis.status = statusx
            elif formid == 'FAF03':
                statusx = body.get("status", {})
                formis.status = statusx
            elif formid == 'FAF06':
                statusx = body.get("status", {})
                formis.status = statusx
            else: 
                formis.status = 'completed'

 
            formis.save()
 
            response_data = { 
                "formId": formid,
                "formRefNo": formrefno
            }
            return Response({
                    "status": "success",
                    "message": "Form data saved successfully.",
                    "data": response_data
                }, status=status.HTTP_200_OK)
        
 
        except Exception as e:
            
            print(str(e))
            return Response(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )







import os
from django.conf import settings

def get_file_path(url):
    """Convert URL to absolute file path"""
    return os.path.join(settings.MEDIA_ROOT, url.replace('/media/', ''))



# FORM sign SECTION ======================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================================
class SignForm(APIView):
    permission_classes = [TokenBasedAuthentication]



    def get(self, request):   
        date = request.query_params.get('date')  
        user_id = request.query_params.get('userid')  

        aircrafttype = request.query_params.get('aircrafttype')  
        aircraftreg = request.query_params.get('aircraftreg')  

 
        # try:
        user = AppUser.objects.get(id=user_id)
        parsed_date = datetime.strptime(date, "%d-%m-%Y").strftime("%Y-%m-%d")
        aircrafttype = Group.objects.get(id=aircrafttype)
        aircraftreg = Group.objects.get(id=aircraftreg)
        parsed_date_obj = datetime.strptime(parsed_date, "%Y-%m-%d").date()
 

        
        try : 
            signFile = SignPDFFiles_db.objects.get(Aircraft_Type = aircrafttype.id, Aircraft_Reg = aircraftreg.id ,signfile_Date = parsed_date_obj)
            
            if signFile: 
                signed_file = SignedCaptFiles_db.objects.filter(
                    signFile_is = signFile,
                    signFile_is__Aircraft_Type=aircrafttype,
                    signFile_is__Aircraft_Reg=aircraftreg,
                    user_is=user
                ).first()

                is_signed = bool(signed_file)

                
                if is_signed:

                    print(signed_file.signedpdf_file)

                    print('ssss')
                    response_data = {  
                        "file" : "yes",
                        "isSigned": is_signed,
                        "file_id":signFile.signfile_Id,
                        "file_name":signFile.signfile_Name,
                        "file_url": request.build_absolute_uri(signed_file.signedpdf_file.url) if signed_file.signedpdf_file else None
                    }
                else:
                    response_data = {  
                        "file" : "yes",
                        "isSigned": is_signed,
                        "file_id":signFile.signfile_Id,
                        "file_name":signFile.signfile_Name,
                        "file_url": request.build_absolute_uri(signFile.signpdf_file.url) if signFile.signpdf_file else None
                    }

                return Response({
                    "status": "success",
                    "message": "One Sign Form",
                    "data": response_data
                }, status=status.HTTP_200_OK)
             
        except:
            response_data = {  
                "file" : "no"
            }

            return Response({
                "status": "success",
                "message": "No Sign Form",
                "data": response_data
            }, status=status.HTTP_200_OK)
            

        # formdata = Forms_db.objects.filter(user_is=user, form_Date=parsed_date_obj).first()

        # Check if the PDF file is signed
  



        response_data = {  
            "signFile" : "",
            "isSigned": is_signed,  # Include whether the file is signed
            "signedFileName": signed_file.signedpdf_file.name if signed_file else None
        }

        return Response({
            "status": "success",
            "message": "Form data retrieved successfully.",
            "data": response_data
        }, status=status.HTTP_200_OK)

        # except Exception as e:
        #     print(e)
        #     return Response({
        #         "status": "error",
        #         "message": str(e),
        #     }, status=status.HTTP_400_BAD_REQUEST)




        # except AppUser.DoesNotExist:
        #     return Response(
        #         {"status": "error", "message": "User not found"},
        #         status=status.HTTP_404_NOT_FOUND
        #     )
 

    def post(self, request, *args, **kwargs): 
        sign_Formid = request.GET.get('signFormId') 
        user_id = request.GET.get('userid')

        try:
            # Fetch user and PDF details
            user_is = AppUser.objects.get(id=user_id)
            signFile = SignPDFFiles_db.objects.get(signfile_Id=sign_Formid)

            # Get absolute file paths
            input_pdf = get_file_path(signFile.signpdf_file.url)
            image_path = os.path.join(settings.MEDIA_ROOT, str(user_is.user_sign))

            # Dynamic output path
            output_directory = os.path.join(settings.MEDIA_ROOT, 'signed')
            output_pdf_filename = f"signed_{user_id}{sign_Formid}.pdf"
            output_pdf = os.path.join(output_directory, output_pdf_filename)

            # Ensure the output directory exists
            if not os.path.exists(output_directory):
                os.makedirs(output_directory)

            # Generate name to be added to the PDF
            name_text = f"{user_is.firstname} {user_is.lastname}"

            # PDF Processing
            reader = PdfReader(input_pdf)
            writer = PdfWriter() 
            signature_image = ImageReader(image_path)

            for page in reader.pages: 
                page_width = float(page.mediabox.width)
                page_height = float(page.mediabox.height)
                
                # Create an overlay canvas
                overlay = BytesIO()
                c = canvas.Canvas(overlay, pagesize=(page_width, page_height))
                
                # Draw signature at bottom-right
                c.drawImage(signature_image, page_width - 350, 20, width=70, height=30, mask='auto') 
                
                # Draw user's name at bottom center
                c.setFont("Helvetica", 9)  
                name_width = c.stringWidth(name_text, "Helvetica")
                name_x_position = ((page_width - name_width)) / 2 - 100
                name_y_position = 35  
                c.drawString(name_x_position, name_y_position, name_text)

                # Finalize and save the overlay
                c.save()
                overlay.seek(0)

                # Merge overlay with original PDF page
                overlay_reader = PdfReader(overlay)
                page.merge_page(overlay_reader.pages[0])
        
                writer.add_page(page)
        
            # Write the signed PDF to the output directory
                        # Write the signed PDF to the output directory
            with open(output_pdf, "wb") as output_file:
                writer.write(output_file)

            # Manually construct the correct URL without /api/v1/
            base_url = f"{request.scheme}://{request.get_host()}"
            signed_pdf_url = f"{base_url}/media/signed/{output_pdf_filename}"

            print(output_pdf)

            # Save the signed PDF record
            sf = SignedCaptFiles_db()
            sf.user_is = user_is
            sf.signFile_is = signFile
            sf.signedpdf_file = f"signed/{output_pdf_filename}"
            sf.save()

            signFile.signature_count = int(signFile.signature_count or 0) + 1
            signFile.save()

            response_data = {  
                "isSigned": True,
                "signed_pdf_url": signed_pdf_url} 

            return Response({
                "status": "success",
                "message": "Form signed successfully.",
                "data":response_data
            }, status=status.HTTP_200_OK)

        except AppUser.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User not found."
            }, status=status.HTTP_404_NOT_FOUND)

        except SignPDFFiles_db.DoesNotExist:
            return Response({
                "status": "error",
                "message": "Sign form not found."
            }, status=status.HTTP_404_NOT_FOUND)

        except FileNotFoundError as e:
            return Response({
                "status": "error",
                "message": f"File not found: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        except Exception as e:
            return Response({
                "status": "error",
                "message": f"An error occurred: {str(e)}"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         

