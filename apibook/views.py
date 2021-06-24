from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authentication import BasicAuthentication, SessionAuthentication, TokenAuthentication
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated

from .models import Book
from .serializers import BookSerializer,BookModelSerializer,LoginSerializer
from django.http import JsonResponse

from rest_framework.views import APIView   # usage of modelforms and class based views

from rest_framework import mixins,generics   #usage of mixins

from django.contrib.auth import authenticate,login

from rest_framework.authtoken.models import Token

# Create your views here.
# book create,list,view ,update,delete
# serializers.py file creation

@csrf_exempt                                    #for not expecting a csrf token
def book_list(request):                        # function based views due to normal serializer
    if request.method == "GET":                # view
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        return JsonResponse(serializer.data, safe=False)
    elif request.method=="POST":               #create or insert
        data=JSONParser.parse(request)
        serializer=BookSerializer(data=data)
        if serializer.is_valid():               #if valid def create in serializer.py will work
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)

@csrf_exempt
def book_details(request, id):
    book=Book.objects.get(id=id)

    if request.method == "GET":
        serializer=BookSerializer(book)
        return JsonResponse(serializer.data)

    elif request.method=="PUT":                      #update
        data=JSONParser().parse(request)
        serializer=BookSerializer(book,data=data)     #update( book have id and can update)
        if serializer.is_valid():
            serializer.save()

            # book.book_name=serializer.validated_data.get("book_name")      either this or the above serializer.save()
            # book.author = serializer.validated_data.get("author")          both are same, only need anyone of them
            # book.price = serializer.validated_data.get("price")
            # book.pages = serializer.validated_data.get("pages")
            # book.save()

            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)

    elif request.method == "delete":                #delete
        book.delete()
        return JsonResponse({"msg":"Deleted"})



class BookListView(APIView):                  #class based view

    def get(self,request):
        books=Book.objects.all()
        serializer=BookModelSerializer(books,many=True)
        return JsonResponse(serializer.data,safe=False)  #safe=False mentions any way serialized

    def post(self,request):
        serializer=BookModelSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)

#authhntication-> session and token authentication

class BookDetailView(APIView):                     #class based view

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_object(self,id):
        return Book.objects.get(id=id)

    def get(self,request,id):
        book=self.get_object(id)
        serializer=BookModelSerializer(book)
        return JsonResponse(serializer.data,status=201)

    def put(self, request, id):
        book=self.get_object(id)
        serializer=BookModelSerializer(book,data=request.data)
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(serializer.data, status=201)
        else:
            return JsonResponse(serializer.errors, status=400)

    def delete(self,request,id):
        book=self.get_object(id)
        book.delete()
        return JsonResponse({"msg": "Deleted"})


#in web django for list we have lstview , for create - createview likewise here we have mixins

class BookMixinView(mixins.ListModelMixin,
                    mixins.CreateModelMixin,
                    generics.GenericAPIView):

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Book.objects.all()
    serializer_class = BookModelSerializer

    def get(self, request,*args, **kwargs):             #view
        return self.list(request,*args,**kwargs)

    def post(self, request,*args, **kwargs):            #create
        return self.create(request,*args,**kwargs)


class BookDetailMixinView(generics.GenericAPIView,
                          mixins.UpdateModelMixin,
                          mixins.DestroyModelMixin,
                          mixins.RetrieveModelMixin,):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    queryset = Book.objects.all()
    serializer_class = BookModelSerializer

    def get(self,request,*args, **kwargs):
        return self.retrieve(request,*args,**kwargs)

    def put(self,request,*args, **kwargs):
        return self.update(request,*args,**kwargs)

    def delete(self,request,*args, **kwargs):
        return self.destroy(request,*args,**kwargs)   #the destroy() update() retrieve() are predefined in mixins


#token authentication
class LoginApi(APIView):

    def post(self,request,*args, **kwargs):
        serializer=LoginSerializer(data=request.data)
        if serializer.is_valid():
            username=serializer.validated_data.get("username")
            password=serializer.validated_data.get("password")
            user=authentication(request,username=username,password=password)
            if user:
                login(request,user)
                token,created=Token.objects.get_or_create()   # generating token to user (initial no token hence create and createdflag=true ,while next login the token is get not created)
                return JsonResponse({"token":token.key})
            else:
                print("no user")
                return JsonResponse({"msg":"failed"})

