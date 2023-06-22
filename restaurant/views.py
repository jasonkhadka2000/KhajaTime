from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib import auth
from django.contrib import messages
from .forms import EditProfileForm
import json
from django.contrib.auth.forms import PasswordChangeForm
from .models import FoodItem,Category,Orders,Review,SpecialItem
from . import logistic as p


cart_price=dict()
cart_name=dict()
cart_quantity=dict()
count=0
esewatotal=0

# Create your views here.
def updatecount():
    global cart_dict
    global count
    count=count+1
    
def index(request):
    return render(request,'restaurant/index.html',{"title":"Home page"})

def about(request):
    return render(request,'restaurant/about.html',{"title":"About us"})

def contact(request):
        return render(request,'restaurant/contact.html',{"title":"Contact"})

def faq(request):
    return render(request,'restaurant/faq.html',{"title":"FAQ"})


def recommended(request):
    if request.user.is_authenticated:
        return render(request, 'restaurant/foryou.html')
    else:
        return redirect('index')

def loginandregister(request):
    return render(request,'restaurant/login.html',{"title":"Login and Register"})

def handlesignup(request):
    if request.method=="POST":
        username=request.POST.get('username','default')
        name=request.POST.get('name','default')
        password=request.POST.get('password','default')
        cpassword=request.POST.get('repassword','default')
        email=request.POST.get('email','default')

        print(name)

        if password==cpassword:
            new_user=User.objects.create_user(username,email,password,first_name=name)
            user=authenticate(username=username,password=password)
            if user is not None:
                login(request,user)
                return redirect('foryou')
        
        else:
            messages.error(request,"wrong passwords combination")
            return HttpResponse("error 404")

def handlelogin(request):
    if request.method=="POST":
        username=request.POST.get('username','default')
        password=request.POST.get('password','default')
        user=authenticate(username=username,password=password)
        if user is not None:
            login(request,user)
            return redirect('foryou')
        else:
            messages.error(request,"invalid credentials")
            return redirect('loginandregister')

def handlelogout(request):
    logout(request)
    return redirect('index')

def updateprofileform(request):
    fm=EditProfileForm(instance=request.user)
    return render(request,"restaurant/updateprofileform.html",{"form":fm,"title":"Update my profile"})

def updateprofile(request):
    if request.method=="POST":
        fm=EditProfileForm(request.POST, instance=request.user)
        if fm.is_valid():
            messages.success(request,"Data updated")
            fm.save()
            return redirect('updateprofileform')
        else:
            messages.success(request,"invalid credentials")
            return redirect('updateprofileform')
    else:
        return redirect('updateprofileform')

def updatepasswordform(request):
    if request.user.is_authenticated:
        fm=PasswordChangeForm(user=request.user)
        return render(request,"restaurant/updatepasswordform.html",{"form":fm,"title":"Update password"})
    else:
        messages.success(request,"Need to login again after password change")
        return redirect('handlelogout')

def updatepassword(request):
    print('here')
    if request.method=="POST":
        fm=PasswordChangeForm(request.user,request.POST)
        print(fm)
        if fm.is_valid():
            print("valid")           
            fm.save()
            logout(request)
            return redirect('updatepasswordform')
            
        else:
            print('invalid')
            messages.success(request,"invalid credentials")
            return redirect('updatepasswordform')
    else:
        messages.success("could not updatepassword")
        return redirect('updatepasswordform')

def fullmenu(request):
    foods=FoodItem.objects.all()
    categorys=Category.objects.all()
    for x  in foods:
        print(x.name)
    return render(request, 'restaurant/fullmenu.html',{"foods":foods,"categories":categorys,"title":"Fullmenu"})

def foryou(request):
    sps = SpecialItem.objects.all()
    foods = FoodItem.objects.all().order_by('-totalOrders')[:4]
    randoms = FoodItem.objects.all().order_by('?')[:4]
    return render(request, 'restaurant/foryou.html', {"sps": sps, "foods": foods, "randoms": randoms,"title":"Home"})


def viewfood(request,id1):
    food=FoodItem.objects.filter(id=id1)
    placeholder=1
    for obj in food:
        idproduct=obj.id
        c=obj.category
    rfood=FoodItem.objects.filter(category=c)
    if idproduct in cart_quantity.keys():
        placeholder=cart_quantity[idproduct]
    return render(request,'restaurant/viewfood.html',{"foods":food,"productsquantity":cart_quantity,"placeholder":placeholder,"rfoods":rfood,"title":"viewfood"})

def viewSpecialfood(request,id1):
    food=SpecialItem.objects.filter(id=id1)
    placeholder=1
    for obj in food:
        idproduct=obj.id
    if idproduct in cart_quantity.keys():
        placeholder=cart_quantity[idproduct]
    return render(request,'restaurant/viewfood.html',{"foods":food,"productsquantity":cart_quantity,"placeholder":placeholder,"title":"viewfood"})
 
   
def cart(request):
    # return HttpResponse(cart_pid)
    return render(request,"restaurant/cart.html",{"productsquantity":cart_quantity,"productsname":cart_name,"title":"MyCart"})

def updatecart(request,id2):
    global cart_price
    global cart_name
    global cart_quantity
    global count
    updatecount()
    quantity=request.POST.get('quantity','1')
    cart_quantity[id2]=quantity
    p=FoodItem.objects.filter(id=id2)
    for obj in p:
        price=obj.price
        name=obj.name
        cart_name[id2]=name
        cart_price[id2]=price
    messages.success(request,"Item added to cart")
    return redirect('/viewfood/'+str(id2))

def removefromcart(request,id3):
    global cart_name,cart_quantity
    del cart_name[id3]
    del cart_quantity[id3]

    return redirect('cart')

def checkout(request):
    global cart_price
    global cart_name
    global cart_puantity
    global esewatotal
    total=0
    esewatotal=0
    quantities=[]
    rates=[]
    total1=[]
    a=""
    
    for key,values in cart_quantity.items():
        quantities.append(values)
    for key,values in cart_price.items():
        rates.append(values)
    for num1, num2 in zip(quantities, rates):
        total1.append(int(num1) * int(num2)) 
        # total =total + (int(num1) * int(num2))

    
    total=sum(total1)
    esewatotal=total
    
    # return HttpResponse("checking out mrjk")
    return render(request,"restaurant/orderform.html",{"productsquantity":cart_quantity,"productsname":cart_name,"productsprice":cart_price,"total":total,"title":"Checkout"})

#using model

def reviews(request):
    uname=request.user.username
    postivecount=0
    negativecount=0
    allreviews=Review.objects.all()
    total=len(allreviews)
    for r in allreviews:
        if r.sentiment=="postive":
            postivecount=postivecount+1
        if r.sentiment=="negative":
            negativecount==negativecount+1
            
    if request.method=="POST":
        username=request.user
        review=request.POST.get('review','default')
        messages.success(request,"review added")
        newreview=Review(username=username,review=review,sentiment=p.prediction(review))
        newreview.save()
        return redirect('reviews')
    allreviews=Review.objects.all()
    return render(request, 'restaurant/reviews.html',{"reviews":allreviews,"uname":uname,"title":"Reviews","postive":round((postivecount/total)*100,2),"negative":round((negativecount/total)*100,2)})

def removereview(request,id=-1):
    Review.objects.filter(id=id).delete()
    messages.success(request, "Review has been deleted")
    return redirect('reviews')

def confirmorder(request):
    global cart_name
    global cart_price
    global cart_quantity
    finalnames=[]
    finalquantities=[]
    finalorder=dict()
    for key,value in cart_name.items():
        finalnames.append(value)
    for key,value in cart_quantity.items():
        finalquantities.append(value)
    for i in range(0,len(finalnames)):
        finalorder[finalnames[i]]=finalquantities[i]
    print(finalorder)
    if request.method=="POST":
        result = json.dumps(finalorder)
        # order_firstname=request.user.first_name
        # order_lastname="khadka"
        order_username=request.user.username
        order_id=request.user.id
        order_contact1=request.POST.get('contact1',"")
        order_contact2=request.POST.get('contact2',"")
        order_email=request.user.email
        order_location=request.POST.get('location',"")
        order_allorders=result
        if order_contact1!="" and order_location!="":
            new_order=Orders(order_username=order_username,order_id=order_id,order_contact1=order_contact1,order_contact2=order_contact2,order_email=order_email,order_location=order_location,order_allorders=order_allorders)
            new_order.save()
            cart_price={}
            cart_name={}
            cart_quantity={}
            messages.success(request,"Your order has been received")
            return redirect('foryou')
        else:
            return HttpResponse("fill out the form")

def cancelorder(request,id):
    order=Orders.objects.get(id=id)
    order.delete()
    messages.success(request,"order cancelled")
    return redirect('ordertracker')

def ordertracker(request):
    id=request.user.id
    orders=Orders.objects.filter(order_id=id)
    orders_dict_with_key_int={}
    for order in orders:
        print(order.order_allorders)
        allorders_dict=json.loads(order.order_allorders)  
        for key,value in allorders_dict.items():
            orders_dict_with_key_int[key]=value     
        order.order_allorders=orders_dict_with_key_int
        orders_dict_with_key_int={}
        

    return render(request,"restaurant/ordertracker.html",{"orders":orders,"title":"MyOrders"})

def esewaRequest(request, order_id):
    global esewatotal
    ord_id = int(order_id)
    order = Orders.objects.get(pk=order_id)
    return render(request,'restaurant/esewaRequest.html', {"order":order,"total":esewatotal})

def confirmEpay(request):
    global cart_name
    global cart_price
    global cart_quantity
    finalnames=[]
    finalquantities=[]
    finalorder=dict()
    for key,value in cart_name.items():
        finalnames.append(value)
    for key,value in cart_quantity.items():
        finalquantities.append(value)
    for i in range(0,len(finalnames)):
        finalorder[finalnames[i]]=finalquantities[i]
    print(finalorder)
    if request.method=="POST":
        result = json.dumps(finalorder)
        order_firstname=request.user.first_name
        order_lastname=request.user.last_name
        order_username=request.user.username
        order_id=request.user.id
        order_contact1=request.POST.get('contact1',"")
        order_contact2=request.POST.get('contact2',"")
        order_email=request.user.email
        order_location=request.POST.get('location',"")
        order_allorders=result
        if order_contact1!="" and order_location!="":
            new_order=Orders(order_firstname=order_firstname,order_lastname=order_lastname,order_username=order_username,order_id=order_id,order_contact1=order_contact1,order_contact2=order_contact2,order_email=order_email,order_location=order_location,order_allorders=order_allorders)
            new_order.save()
            cart_price={}
            cart_name={}
            cart_quantity={}
        else:
            return HttpResponse("fill out the form")
        id1 = new_order.id
        return redirect('/esewaRequest/'+str(id1))

        

