from django.shortcuts import render
from imust.models import Student,Article,Comment, News
from django.views.decorators import csrf
from django.http import HttpResponse
from django.http import HttpResponseRedirect

from django.shortcuts import render
from django.contrib.auth import authenticate, login    

import time
from bs4 import BeautifulSoup
import requests
from lxml import html
import sys
import re


baseurl = "https://coes-stud.must.edu.mo"
intake  = "1809"
academic = "https://coes-stud.must.edu.mo/coes/AcademicRecordsForm.do"

# Create your views here.


def login(request):
    if request.POST:
        if verify(request.POST['sid'],request.POST['pw']) == 0:
            result = Student(sid = request.POST['sid'], password =  request.POST['pw'], name = 'DEFAULT_' + request.POST['sid'])
            result.save()
        else:
            return HttpResponseRedirect('http://127.0.0.1:8000/')
    return HttpResponseRedirect('http://127.0.0.1:8000/S_Home.html/?sid=' + request.POST['sid'])

def Login(request):
    return render(request, 'imust/Login.html')

def quit(request):
    result = Student.objects.get(sid=request.GET.get('sid')).delete()
    return HttpResponseRedirect('http://127.0.0.1:8000/')

def forumComment(request):
    s = request.GET.get('sid')
    aid = request.GET.get('aid')
    article = Article.objects.get(aid=aid)
    comment_list = Comment.objects.filter(aid=aid)
    return render(request, 'imust/S_Forum-comment.html', context={'article': article, 'comment_list':comment_list, 'sid':s})

def forumPublish(request):
    s = request.GET.get('sid')
    return render(request, 'imust/S_Forum-publish.html', context={'sid':s})

def submitAr(request):
    s = request.GET.get('sid')
    stu = Student.objects.get(sid=s)
    ctx={}
    if request.POST:
        result = Article(title = request.POST['Title'], content =  request.POST['Content'], author = stu.name)
        result.save()
        ar = Article.objects.latest('time')
    ctx['result'] = "Successful!"
    return render(request, 'imust/S_Forum-publish.html', context={'result':ctx, 'sid':s})

def submitCo(request):
    s = request.GET.get('sid')
    aid=request.GET.get('aid')
    ctx={}
    if request.POST:
        stu = Student.objects.get(sid=s)
        result = Comment(aid = aid, comment =  request.POST['Comment'], name=stu.name, sid=s)
        result.save()
    ctx['result'] = "Successful!"
    article = Article.objects.get(aid=aid)
    comment_list = Comment.objects.filter(aid=aid)
    return render(request, 'imust/S_Forum-comment.html', context={'article': article, 'comment_list':comment_list, 'result':ctx, 'sid':s})


def forumhome(request):
    s = request.GET.get('sid')
    article_list = Article.objects.all().order_by('-time')
    return render(request, 'imust/S_Forumhome.html', context={'article_list': article_list, 'sid':s})

def home(request):
    s = request.GET.get('sid')
    return render(request, 'imust/S_Home.html', context={'sid':s})

def news(request):
    s = request.GET.get('sid')
    result = News.objects.all().order_by('-time')
    return render(request,'imust/S_News.html', context = {'news':result, 'sid':s})

def refreshNew(request):
    a = News.objects.all().delete()
    s = request.GET.get('sid')
    a = getNews()
    result = News.objects.all().order_by('-time')
    return render(request,'imust/S_News.html', context = {'news':result, 'sid':s})

def Time(request):
    s = request.GET.get('sid')
    return render(request, 'imust/S_Time.html', context={'sid':s})

def getNews():
	list_Content = []

	for page in range(1,5):
		print("------------------------------------------next page: ", page)
		urlend = '?limit=10&start='
		target = 'https://www.must.edu.mo/cn/news'
		if page != 1:
			start = page * 10
			target = target + urlend + str(start)
		req = requests.get(url = target, verify=False)
		html = req.text
		bf = BeautifulSoup(html, features="html.parser")
		must = 'https://www.must.edu.mo'

		for row in range(0,9):
			time = bf.select('#t3-content > section > div.items-row.cols-1.row-'+str(row)+' > article > div.article-content > aside')
			title = bf.select('#t3-content > section > div.items-row.cols-1.row-'+ str(row) + ' > article > div.article-content > h4 > a')
			link = bf.select('#t3-content > section > div.items-row.cols-1.row-'+ str(row) + ' > article > div.article-content > h4 > a')
			#print(time[0].text) 
			#print(title[0].text)
			for href in link:
				t = href.get('href')
				news = must + t;
				#print(news)
				req = requests.get(url = news, verify = False)
				sub = BeautifulSoup(req.text, features="html.parser")
				body = sub.find('section', class_= 'article-content clearfix')
				result = News(title=title[0].text,time=time[0].text,content=body.text)
				result.save()
				#print(body.text)
				
	return 0

def verify(uname,pwd):
    # pre-processing
    cook = ""
    try:
        url = baseurl+"/coes/login.do"
        resp = requests.get(url,timeout=5)
        cook = resp.cookies
        tree = html.fromstring(resp.text)
        token = tree.xpath('//form[@name="LoginForm"]/div/input/@value')
        post_data = {'org.apache.struts.taglib.html.TOKEN': token, 'userid': uname, 'password': pwd,
                         'submit': '%E7%99%BB%E5%85%A5'}
        
        time.sleep(3)
        resp = requests.post(url, data=post_data, cookies=cook)
        print (cook)

        if resp.text.find("Inbox") != -1:
            print ('>>>Login successed!')
            logout(cook)
            return 0
        else:
            print ('>>>Login failed!')
            logout(cook)
            return 1
    except Exception as e:
        logout(cook)
        raise e
    except KeyboardInterrupt:
        logout(cook)
        sys.exit(n) 

def timeTableMain(uname, pwd):
    # pre-processing
    cook = ""
    try:
        url = baseurl+"/coes/login.do"
        resp = requests.get(url,timeout=5)
        cook = resp.cookies
        tree = html.fromstring(resp.text)
        token = tree.xpath('//form[@name="LoginForm"]/div/input/@value')
        post_data = {'org.apache.struts.taglib.html.TOKEN': token, 'userid': uname, 'password': pwd,
                     'submit': '%E7%99%BB%E5%85%A5'}
        
        # real login
        time.sleep(3)
        resp = requests.post(url, data=post_data, cookies=cook)
        print (cook)

        if resp.text.find("Inbox") != -1:
            print ('>>>Login successed!')
        else:
            print ('>>>Login failed!')
            logout(cook)
            return None
            raise Exception("Failed to login")

        academic_form(academic, cook)

        return cook
    except Exception as e:
        logout(cook)
        raise e
    except KeyboardInterrupt:
        logout(cook)
        sys.exit(n) 

def logout(cook):
    print ('>>>logout with Cook:' + str(cook))
    url = baseurl+"/coes/logout.do"
    requests.get(url, cookies=cook)
    print ('>>>Logout done!')


def academic_form(url,cookie):
    res = requests.get(url, cookies=cookie)
    tree = html.fromstring(res.text)
    token = tree.xpath('//form[@name="AcademicRecordsForm"]/div/input/@value')
    form_data = {'org.apache.struts.taglib.html.TOKEN': token, 'formAction': 'Timetable', 'intake': '1809',
                 'x': '25','y':'6' }

    time.sleep(3)
    res_timetable = requests.post(url, data=form_data, cookies=cookie)
    bf = BeautifulSoup(res_timetable.text, features="html.parser")
    script = bf.find_all('td', class_='data')
    script = str(script)
    print(script)

    #select script content
    scr = re.compile(r'<!--[\s\S]*-->')
    scr_content = scr.findall(script)
    print(scr_content)

    tb = re.compile(r'\'[^,+) ]*\'')
    tbs = tb.findall(scr_content[0])
    print(tbs)

    for data in tbs:
        return 
    return 0





