from django.shortcuts import render,HttpResponse,redirect
from shoemart.models import Product,Cart,Orders
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
import random,razorpay
from django.core.mail import send_mail

# Create your views here.
'''
function based view
def function_name(req):    
    function body
    return HttpResponse(data)
'''

#function views for ecomm

def index(request):
    uid=request.user.id
    print('User Id:',uid)
    print(request.user.is_authenticated)
    print(request.user.username)
    p=Product.objects.filter(is_active=True)
    #print(p)
    context={}
    context['product']=p
    return render(request,'index.html',context)

def details(request,id):
    p=Product.objects.filter(id=id)
    # print(p)
    context={}
    context['product']=p
    return render(request,'details.html',context)

def cart(request,rid):
    context={}
    if request.user.is_authenticated:
        p=Product.objects.filter(id=rid)
        u=User.objects.filter(id=request.user.id)
        # print(p)
        q1=Q(pid=p[0])
        q2=Q(uid=u[0])
        res=Cart.objects.filter(q1 & q2)
        # print(res)
        if res:
            context['error']='Product already exist in Cart.'
            context['product']=p
            return render(request,'details.html',context)
        else:
            # print(u)
            c=Cart.objects.create(uid=u[0],pid=p[0])
            c.save()
            context['product']=p
            context['succ']='Product Added Successfully in Cart.'            
            return render(request,'details.html',context)
    else:
        return redirect ("/login")
        
def order(request):
    context={}
    if request.user.is_authenticated:
        c=Cart.objects.filter(uid=request.user.id) #fetch filter data from database
        oid=random.randrange(1000,9999)
        # print(oid)
        i=len(c) #for count of total obj
        s=0 #make var for multiply
        for x in c:
            o=Orders.objects.create(order_id=oid,uid=x.uid,pid=x.pid,qty=x.qty)
            o.save()            
            s=s+(x.qty*x.pid.price) #multiply product quantity x product price for total price
            x.delete()
        context['total']=s #keypair for total value
        context['cdata']=c #fetch data from database. 2nd way to fecth=(Orders.objects.filter(uid=request.user.id))
        context['items']=i
        return render(request,'order.html',context)
    else:
        return redirect('/login')

def about(request):
    return render(request,'about.html')

def contact(request):
    return render(request,'contact.html')

def userlogin(request):
    context={}
    if request.method=='GET':
        return render(request,'login.html')
    else:
        vname=request.POST['lname']
        vpass=request.POST['lpass']
        # print(vname)
        # print(vpass)
        u=authenticate(username=vname,password=vpass)
        if u is not None:
            login(request,u)
            return redirect('/index')
        else:
            context['errormsg']='Invalid Username or Password!!!'
            return render(request,'login.html',context)         
        
def payment(request):
    client = razorpay.Client(auth=("rzp_test_FZZBoGqEBQidFC", "IL9OWMM1TmK49pTkpkETbcwo"))
    # print(client)
    q1=Q(order_status=False)
    q2=Q(uid=request.user.id)
    o=Orders.objects.filter(q1 & q2) #fetch filter data from database
    oid=str(o[0].order_id)
    s=0
    for x in o:
        s=s+(x.qty*x.pid.price)
    # print("id :",oid)
    # print("total :",s)
    s=s*100 #rs to paisa
    data = { "amount":s, "currency": "INR", "receipt": oid } #insert data with variable
    payment = client.order.create(data=data) #insert data to razorpay dashboard
    # print(payment)
    context={}
    context['pay']=payment
    context['data']=o
    context['amount']=s/100
    return render(request,'payment.html',context)

def sendmail(request):
    context={}
    o=Orders.objects.filter(uid=request.user.id)
    pid=request.GET['p1']
    oid=request.GET['p2']
    sign=request.GET['p3']
    myid=o[0].order_id
    # print(pid)
    # print(oid)
    # print(sign)
    msg="Your Order had been Placed Successfully. Your Order Tracking Id: "+oid
    rec_email=request.user.email
    send_mail(
    "Subject here",
    msg,
    "ppanaskar9@gmail.com",
    [rec_email],
    fail_silently=False,
    )
    o=Orders.objects.filter(order_id=myid)
    o.update(order_status=True)
    context['oid']=oid
    context['pid']=pid
    return render(request,'placed.html',context)


def register(request):
    context={}
    if request.method=='GET':
        return render(request,'register.html')
    else:
        vname=request.POST['uname']
        vpass=request.POST['upass']
        vcpass=request.POST['ucpass']
        # validation
        if vname=='' or vpass=='' or vcpass=='':
            context['errormsg']='Field Cannot be Empty'
            return render(request,'register.html',context)
        elif vpass!=vcpass:
            context['errormsg']="Password didn't match"
            return render(request,'register.html',context)
        else:
            try:
                u=User.objects.create(username=vname)
                u.set_password(vpass)
                u.save()
                context['succ']="User Created Successfully"
                return render(request,'register.html',context)
            except Exception:
                context['errormsg']='Username not available' 
                return render(request,'register.html',context)
       


def catfilter(request,cv):
    q1=Q(cat=cv)
    q2=Q(is_active=1)
    #p=Product.objects.filter(cat=cv)
    p=Product.objects.filter(q1 & q2)
    context={}
    context['product']=p
    return render(request,'index.html',context)

def pricerange(request):

    min=request.GET['min']
    max=request.GET['max']
    # print(min)
    # print(max)
    # return HttpResponse('values')
    q1=Q(price__gte=min)
    q2=Q(price__lte=max)
    q3=Q(is_active=1)
    p=Product.objects.filter(q1 & q2 & q3)
    context={}
    context['product']=p
    return render(request,'index.html',context)

def sort(request,sv):
    if sv == '1':
        para='-price'
    else:
        para='price'
    p=Product.objects.order_by(para).filter(is_active=1)
    context={}
    context['product']=p
    return render(request,'index.html',context)

def user_logout(request):
    logout(request)
    return redirect('/index')

def viewcart(request):
    context={}
    if request.user.is_authenticated:
        c=Cart.objects.filter(uid=request.user.id) #fetch filter data from database
        i=len(c) #for count of total obj
        s=0 #make var for multiply
        for x in c:
            s=s+(x.qty*x.pid.price) #multiply product quantity x product price for total price
        context['total']=s #keypair for total value
        context['cdata']=c #fetch data from database
        context['items']=i
        return render(request,'cart.html',context)
    else:
        return redirect('/login')

def remove(request,cid):
    c=Cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')

def cartqty(request,sig,pid):
    q1=Q(uid=request.user.id)
    q2=Q(pid=pid)
    c=Cart.objects.filter(q1 & q2)
    # print(c)
    qty=c[0].qty
    if sig == '0':
        if qty>1:
            qty=qty-1
            c.update(qty=qty)
    else:
        qty=qty+1
        c.update(qty=qty)
    # print(qty)
    return redirect('/viewcart')

def search(request):
    context={}
    find=request.GET['find']
    if find!='':
        p=Product.objects.filter(name__icontains=find)
        context['product']=p
        context['value']=find
        return render(request,'index.html',context)
    else:
        return redirect('/index')



#appcode- tueo eiae hwxn amzf