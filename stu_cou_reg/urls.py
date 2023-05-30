from django.urls import path
from . import views


urlpatterns = [
    path('course-reg/<int:id>', views.course_reg_page, name='course_reg_page'),
    path('student-profile', views.stu_profile_page, name='stu_profile_page'),
    path('admin-port/', views.admin_portal_page, name='admin_portal_page'),
    # path('ap-std/', views.admin_portal_std_page, name='admin_portal_std_page'),
    # path('ap-course/', views.admin_portal_course_page, name='admin_portal_course_page'),

    path('mail-verification/', views.admin_portal_approval_page, name='email_verify'),
    path('email_verify/',views.VerifyEmail.as_view(),name="email_verify"),
    path('email_for_pass/',views.Forgot_Pass_Email.as_view(),name="email_for_pass"),
    path('forgot-pass-to-mail/', views.forgot_pass_to_mail, name='forgot_pass_to_mail'),
    path('set-new-pass/', views.change_forgot_pass, name='change_forgot_pass'),

    path('signup/', views.student_signup_form, name='student_signup_form'),
    path('login/', views.student_login_form, name='student_login_form'),
    path('stu-course/', views.course_reg_form, name='course_reg_form'),
    path('admin-login/', views.admin_login_form, name='admin_login_form'),
    path('student-logout/', views.student_logout, name='student_logout'),
    path('student-delete/<int:id>', views.delete_student, name='delete_student'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('ap-std/', views.student_view, name='student_view'),
    path('ap-course-add/', views.course_add, name='course_add'),
    path('ap-course-view/', views.course_view, name='course_view'),
    path('ap-course-edit/<int:pk>', views.course_edit_click, name='course_edit_click'),
    path('ap-course-edit-port/', views.course_edit, name='course_edit'),
    path('student-profile-edit-click/', views.edit_student_profile_click, name='edit_student_profile_click'),
    path('student-profile-edit/', views.edit_student_profile, name='edit_student_profile'),
    path('student-change-password/', views.stu_change_pass, name='stu_change_pass'),
    path('ap-stu-reg-approve/<int:id>/<int:course_id>', views.std_reg_status_approval, name='std_reg_status_approval'),
    path('ap-stu-reg-reject/<int:id>/<int:course_id>', views.std_reg_status_reject, name='std_reg_status_reject'),
]