from django.db import models
from django.contrib.auth.models import User

class CourseData(models.Model):
    course_id = models.BigAutoField(primary_key='True')
    course_name = models.CharField(max_length=16,unique='True',null='True')
    description = models.CharField(max_length=500)

    class Meta:
        db_table='Courses'

class StudentData(models.Model):
    student_id = models.BigAutoField(primary_key='True',auto_created='True')
    stu_reg_id = models.CharField(max_length=50,unique='True',null='True')
    student_image = models.ImageField(null='True', upload_to='')

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user')

    class Meta:
        db_table='Student'
        
    def _str_(self):
        return self.user.username
    
class RegisteredData(models.Model):
    registered_id = models.BigAutoField(primary_key='True',auto_created='True')
    student_id = models.ForeignKey(StudentData, null=True, on_delete=models.CASCADE)
    course_id = models.ForeignKey(CourseData, null=True, on_delete=models.CASCADE)
    course_status = models.IntegerField(default=0)
    
    class Meta:
        db_table='Regisatered'


   