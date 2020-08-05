
from io import BytesIO

import xlwt
from django.contrib.admin.utils import quote
from django.http import JsonResponse, HttpRequest, HttpResponse
from django.shortcuts import render,redirect
from polls.models import Subject,Teacher,User
from polls.utils import gen_md5_digest,gen_random_code
from polls.gen_captcha import Captcha

# Create your views here.

def show_subjects(request):
    subjects = Subject.objects.all().order_by('no')
    return render(request,'subjects.html',{'subjects':subjects})

def show_teachers(request):
    try:
        sno = int(request.GET.get('sno'))
        if sno:
            subject = Subject.objects.only('name').get(no=sno)
            teachers = Teacher.objects.filter(subject=subject).order_by('no')
        return render(request,'teachers.html',{
            'subject':subject,
            'teachers':teachers
        })
    except(ValueError,Subject.DoesNotExist):
        return redirect('/')

def praise_or_criticize(request:HttpRequest)->HttpResponse:

    if request.session.get('userid'):
        try:
            tno = int(request.GET.get('tno'))
            teacher = Teacher.objects.get(no=tno)
            if request.path.startswith("/praise"):
                teacher.good_count += 1
                count = teacher.good_count
            else:
                teacher.bad_count += 1
                count = teacher.bad_count
            teacher.save()
            data = {'code':20000,'mesg':'操作成功','count':count}
        except(ValueError,Teacher.DoseNotExist):
            data = {'code':20001,'mesg':'操作失败'}
    else:
        data = {'code':20002,'mesg':'请先登录'}
    return JsonResponse(data)


def get_captcha(request:HttpRequest) -> HttpResponse:
    """验证码"""
    captcha_text = gen_random_code()
    request.session['captcha'] = captcha_text
    image_data = Captcha.instance().generate(captcha_text)
    return HttpResponse(image_data, content_type='image/png')


def login(request:HttpRequest) -> HttpResponse:
    hint=""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get("password")
        if username and password:
            password = gen_md5_digest(password)
            user = User.objects.filter(username=username,password=password).first()
            if user:
                request.session["userid"] = user.no
                request.session["username"] = user.username
                return redirect('/')
            else:
                hint="用户名或者密码错误"
        else:
            hint = "请输入有效的用户名和密码"
    return render(request,'login.html',{'hint':hint})

def register(request):
    hint=""
    if request.method == "POST":
        reg_username = request.POST.get("reg_username")
        reg_password = request.POST.get("reg_password")
        reg_password_again = request.POST.get("reg_password_again")
        if reg_password != reg_password_again:
            hint = "两次输入的用户名密码不正确,请重新输入"
        elif reg_password and reg_username:

            if reg_username == User.objects.filter(username=reg_username).first().username:
                hint = "用户名已经被注册"
                return render(request, "register.html", {"hint": hint})

            user = User(username=reg_username,password = gen_md5_digest(reg_password))
            user.save()
            return redirect('/login/')
        else:
            hint="输入有误，请重新输入"

    return render(request,"register.html",{"hint":hint})


def logout(request):

    """注销"""
    request.session.flush()
    return redirect('/')

def export_teachers_excel(request):
    # 创建工作簿
    wb = xlwt.Workbook()
    # 添加工作表
    sheet = wb.add_sheet('老师信息表')
    # 查询所有老师的信息
    queryset = Teacher.objects.all().select_related('subject')
    # 向Excel表单中写入表头
    colnames = ('姓名', '介绍', '好评数', '差评数', '学科')
    for index, name in enumerate(colnames):
        sheet.write(0, index, name)
    # 向单元格中写入老师的数据
    props = ('name', 'intro', 'good_count', 'bad_count', 'subject')
    for row, teacher in enumerate(queryset):
        for col, prop in enumerate(props):
            value = getattr(teacher, prop, '')
            if isinstance(value, Subject):
                value = value.name
            sheet.write(row + 1, col, value)
    # 保存Excel
    buffer = BytesIO()
    wb.save(buffer)
    # 将二进制数据写入响应的消息体中并设置MIME类型
    resp = HttpResponse(buffer.getvalue(), content_type='application/vnd.ms-excel')
    # 中文文件名需要处理成百分号编码
    filename = quote('老师.xls')
    # 通过响应头告知浏览器下载该文件以及对应的文件名
    resp['content-disposition'] = f'attachment; filename*=utf-8''{filename}'
    return resp

# def export_pdf(request: HttpRequest) -> HttpResponse:
#     buffer = BytesIO()
#     import reportlab
#     pdf = canvas.Canvas(buffer)
#     pdf.setFont("Helvetica", 80)
#     pdf.setFillColorRGB(0.2, 0.5, 0.3)
#     pdf.drawString(100, 550, 'hello, world!')
#     pdf.showPage()
#     pdf.save()
#     resp = HttpResponse(buffer.getvalue(), content_type='application/pdf')
#     resp['content-disposition'] = 'inline; filename="demo.pdf"'
#     return resp

def get_teachers_data(request):
    queryset = Teacher.objects.all().only('name','good_count','bad_count')
    names = [teacher.name for teacher in queryset]
    good_counts = [teacher.good_count for teacher in queryset]
    bad_counts = [teacher.bad_count for teacher in queryset]
    return JsonResponse({'names': names, 'good': good_counts, 'bad': bad_counts})

def echarts(request):
    return render(request,'echarts.html')

