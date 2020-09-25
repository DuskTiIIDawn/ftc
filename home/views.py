from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, Http404,HttpResponse
from django.core.mail import send_mail
from home.forms import ContactForm, CreateUserForm, UserForm, SubmittedForm, ExamKeyForm
from home.models import (Notice, Quiz, Question, MCQuestion, TF_Question, Essay_Question, Category,
                         Sitting, SittingManager, Progress, UserProfile, MediaFile, Photos, FormResponses,
                         ImportantForms,UserOrder)

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import cache_control
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory
from django.core.exceptions import PermissionDenied
from datetime import datetime
from PayTm import Checksum
MERCHANT_KEY = '**********'
mid="***********"
import json
import requests


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def home(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            your_name = form.cleaned_data['your_name']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['email_id']
            cc_myself = form.cleaned_data['cc_myself']
            str_message = message + "\n" + "by" + "-" + your_name + "\n" + sender
            recipients = ['classesfuturetrack@gmail.com']

            if cc_myself:
                recipients.append(sender)

            send_mail(subject, str_message, sender, recipients, fail_silently=False, )
            return HttpResponseRedirect('#contact')
    else:
        form = ContactForm()
        return render(request, 'home/home.html', {'form': form})


def index(request):
    return render(request, 'home/index.html')


def memories(request):
    photos = Photos.objects.all()
    return render(request, 'home/memories.html', {'photos': photos})


def notice(request):
    notices = Notice.objects.all()
    return render(request, 'home/notice.html', {'notices': notices})


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def registration(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        form = CreateUserForm()
        if request.method == 'POST':
            form = CreateUserForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request, 'Account was created for ' + user)
                return redirect('login')
        context = {'form': form}
        return render(request, 'home/registration.html', context)


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def loginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    else:
        if request.method == 'POST':
            identity = request.POST.get('login_email_or_username')
            password = request.POST.get('password')
            user = authenticate(request, username=identity, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.info(request, 'Email OR password is incorrect')

        context = {}
        return render(request, 'home/login.html', context)


def logoutPage(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def importantpdf(request):
    important_files = MediaFile.objects.all()
    args = {'important_files': important_files}
    return render(request, 'home/Important_files.html', args)


@login_required(login_url='login')
def importantforms(request):
    important_forms = ImportantForms.objects.all()
    submitted_form = SubmittedForm()
    if request.method == "POST":
        form_id = request.POST.get('description')
        submitted_form = SubmittedForm(request.POST, request.FILES)
        if submitted_form.is_valid():
            requested_form = ImportantForms.objects.get(pk=form_id)
            FormResponses.objects.safe_save(request.user, requested_form)
            model_instance = submitted_form.save()
            model_instance.user = request.user
            model_instance.form = requested_form
            model_instance.save()
            messages.success(request, 'Form was submitted succesfully!')
            return redirect('importantforms')
        else:
            form_id = int(form_id)
            context = {'form': submitted_form, 'important_forms': important_forms, 'form_id': form_id}
            return render(request, 'home/important_forms.html', context)

    context = {'form': submitted_form, 'important_forms': important_forms}
    return render(request, 'home/important_forms.html', context)



@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def quiz(request):
    return render(request, 'home/quiz.html', {})




@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def paidpapers(request):
    category = request.GET.get('category', None)
    if category:
        try:
            requested_category = Category.objects.get(category=category)
            try:
                userorder = UserOrder.objects.get(user=request.user)
                purchased_list = userorder.get_purchased_list
            except UserOrder.DoesNotExist:
                purchased_list = []
            quizes = Quiz.objects.filter(hide_quiz=False, is_paid="True",category=requested_category).exclude(id__in=purchased_list)
            return render(request, 'home/paidpapers.html', {'quizes': quizes,'category':category})
        except Category.DoesNotExist:
            pass
    categories = Category.objects.all()
    title = "PAID PAPERS"
    link = "paidpapers"
    return render(request, 'home/category.html', {'categories': categories, 'title': title, 'link': link})


@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def freepapers(request):
    category = request.GET.get('category', None)
    if category:
        try:
            requested_category = Category.objects.get(category=category)
            quizes = Quiz.objects.filter(hide_quiz= False, is_paid="False",category= requested_category)
            return render(request, 'home/freepapers.html', {'quizes': quizes})
        except Category.DoesNotExist:
            pass
    categories = Category.objects.all()
    title="FREE PAPERS"
    link="freepapers"
    return render(request, 'home/category.html', {'categories': categories,'title':title,'link':link})


@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def mypapers(request):
    try:
        userorder = UserOrder.objects.get(user=request.user)
        purchased_list = userorder.get_purchased_list
    except UserOrder.DoesNotExist:
        purchased_list = []
    quizes = Quiz.objects.filter(hide_quiz = False, is_paid="True",pk__in = purchased_list)
    return render(request, 'home/mypapers.html', {'quizes': quizes})


@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def examkey(request, quiz_id):
    form = ExamKeyForm()
    isunlocked = None
    if request.method == "POST":
        if form.is_valid:
            key = request.POST.get('key')
            quiz = Quiz.objects.filter(pk=quiz_id,hide_quiz=False)[0]
            if quiz.secret_key == key:
                isunlocked = True
                request.session[str(quiz_id)] = quiz.secret_key
                return redirect('/quiz/' + quiz_id)
            else:
                isunlocked = False
    return render(request, "home/examkey.html", {'form': form, 'quiz_id': quiz_id, 'isunlocked': isunlocked})


@login_required(login_url='login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@csrf_exempt
def detail(request, quiz_id):
    try:
        quiz = Quiz.objects.get(pk=quiz_id, hide_quiz=False)
    except Quiz.DoesNotExist:
        raise Http404("Quiz is not accessible")
    if quiz.is_paid == "True":
        try:
            userorder = UserOrder.objects.get(user=request.user)
            purchased_list = userorder.get_purchased_list
        except UserOrder.DoesNotExist:
            purchased_list = None
        if quiz.id not in purchased_list or purchased_list == None:
            return redirect('paidpapers')


    if quiz.secret_key != "":
        if request.session.get(str(quiz_id), False) == False or request.session.get(str(quiz_id),False) != quiz.secret_key:
            return redirect('/quiz/examkey/' + quiz_id)
    questions = quiz.question_set.all().select_subclasses()
    mcquestions = quiz.question_set.all().exclude(mcquestion__isnull=True).select_subclasses()
    tfquestions = quiz.question_set.all().exclude(tf_question__isnull=True).select_subclasses()
    essayquestions = quiz.question_set.all().exclude(essay_question__isnull=True).select_subclasses()

    if request.method == 'POST':
        sitting = Sitting.objects.user_sitting(request.user, quiz)
        progress, c = Progress.objects.get_or_create(user=request.user)
        progress.update_score(quiz,sitting)
        progress.update_all_quiz_records(quiz,sitting)
        sitting.mark_quiz_complete()
        try:
            del request.session[str(quiz_id)]
        except KeyError:
            pass

        if quiz.save_answers == False:
            sitting.delete()

        return redirect('/quiz/result/' + quiz_id)

    context = {'quiz': quiz, 'questions': questions, 'mcquestions': mcquestions, 'tfquestions': tfquestions,
               'essayquestions': essayquestions}
    return render(request, 'home/detail.html', context)


@login_required(login_url='login')
@csrf_exempt
def question(request, quiz_id):
    if request.is_ajax():
        try:
            quiz = Quiz.objects.get(pk=quiz_id, hide_quiz=False)
        except Quiz.DoesNotExist:
            raise Http404("Quiz is not accessible")

        if quiz.is_paid == "True":
            try:
                userorder = UserOrder.objects.get(user=request.user)
                purchased_list = userorder.get_purchased_list
            except UserOrder.DoesNotExist:
                purchased_list = None
            if quiz.id not in purchased_list or purchased_list == None:
                raise PermissionDenied

        if quiz.secret_key != "":
            if request.session.get(str(quiz_id), False) == False or request.session.get(str(quiz_id),
                                                                                        False) != quiz.secret_key:
                raise PermissionDenied


        sitting = Sitting.objects.user_sitting(request.user, quiz)

        if sitting is False:
            return render(request, 'home/single_attempt.html')

        questions = quiz.question_set.all().select_subclasses().order_by('essay_question')
        paginator = Paginator(questions, 1)
        time = datetime.now() - sitting.start
        if quiz.exam_paper == "True":
            if quiz.test_timing * 60 - time.total_seconds() > 0:
                sitting.update_time_left(float((quiz.test_timing * 60 - time.total_seconds()) / 60))
            else:
                sitting.update_time_left(0)

        page = request.GET.get('page')
        try:
            page_obj = paginator.get_page(page)
        except PageNotAnInteger:
            page_obj = paginator.page(1)
        except EmptyPage:
            page_obj = paginator.page(paginator.num_pages)

        qd ={ int(i+1): paginator.get_page(i+1)[0].id for i in range(paginator.num_pages)}
        return render(request, 'home/question.html', {'quiz': quiz, 'page_obj': page_obj,'qd':qd})
    else:
        raise PermissionDenied


@login_required(login_url='login')
@csrf_exempt
def result(request, quiz_id):
    try:
        quiz = Quiz.objects.get(pk=quiz_id, hide_quiz=False)
    except Quiz.DoesNotExist:
        raise Http404("Quiz is not accessible")

    if request.method == 'POST':
        question_id = request.POST.get('question_id')
        guess = request.POST.get('guess')
        question = quiz.question_set.filter(pk=question_id).select_subclasses()[0]
        sitting = Sitting.objects.user_sitting(request.user, quiz)
        sitting.add_update_or_remove_user_answer(question, guess)
        if guess == "_NO_ANSWER_":
            sitting.remove_incorrect_question(question)
            sitting.remove_correct_question(question)
            sitting.add_unanswered_list(question)

        else:
            is_correct = question.check_if_correct(guess)
            if is_correct:
                sitting.add_correct_question(question)
                sitting.remove_incorrect_question(question)
                sitting.remove_unanswered_list(question)
            else:
                sitting.add_incorrect_question(question)
                sitting.remove_correct_question(question)
                sitting.remove_unanswered_list(question)

        sitting.current_score = 0
        for q in sitting.correct_questions.split(','):
            if q:
                correct_question = Question.objects.get(pk=q)
                sitting.add_to_score(correct_question.max_mark)

        for q in sitting.incorrect_questions.split(','):
            if q:
                incorrect_question = Question.objects.get(pk=q)
                sitting.add_to_score(-(incorrect_question.negative_marking))

    return render(request, 'home/result.html', {'quiz': quiz})




@login_required(login_url='login')
@csrf_exempt
def timer(request, quiz_id):
    if request.method == 'POST':
        try:
            quiz = Quiz.objects.get(pk=quiz_id,hide_quiz=False)
        except Quiz.DoesNotExist:
            raise Http404("Quiz is not accessible")
        sitting = Sitting.objects.user_sitting(request.user, quiz)
        time_left_in_min = request.POST.get('time_left_in_min')
        sitting.update_time_left(time_left_in_min)
        print(time_left_in_min)
        return render(request, 'home/result.html')
    else:
        raise PermissionDenied


@login_required(login_url='login')
def progress(request):
    try:
        progress = Progress.objects.get(user=request.user)
        progresses = json.loads(progress.score)
    except Progress.DoesNotExist:
        progresses = None

    context = {'progress': progresses}
    return render(request, 'home/progress.html', context)

@login_required(login_url='login')
def rank(request,quiz_id):
    if request.is_ajax():
        try:
            quiz = Quiz.objects.get(pk=quiz_id)
        except Quiz.DoesNotExist:
            raise Http404("Quiz does not exist ")
        data = json.loads(quiz.user_marks)
        if data:
            rank = quiz.get_user_rank(request.user)
            total_appeared=len(data)
            context = {'rank':rank, 'total_appeared': total_appeared}
        else:
            context = {'rank': 0, 'total_appeared': 0}
        return render(request, 'home/rank.html', context)
    else:
        raise PermissionDenied



@login_required(login_url='login')
def progressdetail(request, quiz_id):
    try:
        progress = Progress.objects.get(user=request.user)
    except Progress.DoesNotExist:
        raise Http404("Progress Does Not Exist")
    progresses = json.loads(progress.score)
    p_detail = progresses.get(str(quiz_id))

    context = {'quiz_result': p_detail,'quiz_id':quiz_id}
    return render(request, 'home/progress_detail.html', context)


@login_required(login_url='login')
def view_profile(request):
    user = request.user
    user_form = UserForm(instance=user)

    ProfileInlineFormset = inlineformset_factory(User, UserProfile, can_delete=False,
                                                 fields=('description', 'address', 'education', 'phone', 'image'))
    formset = ProfileInlineFormset(instance=user)

    if request.user.is_authenticated and request.user.id == user.id:
        if request.method == "POST":
            user_form = UserForm(request.POST, request.FILES, instance=user)
            formset = ProfileInlineFormset(request.POST, request.FILES, instance=user)

            if user_form.is_valid():
                created_user = user_form.save(commit=False)
                formset = ProfileInlineFormset(request.POST, request.FILES, instance=created_user)

                if formset.is_valid():
                    created_user.save()
                    formset.save()
                    return redirect('view_profile')

        try:
            progress = Progress.objects.get(user=request.user)
            achievements = json.loads(progress.all_quiz_records)
            achievements = achievements.get('all_records')
        except Progress.DoesNotExist:
            achievements = None

        return render(request, "home/profile.html", {
            'user': user,
            "noodle_form": user_form,
            "formset": formset,
            'achievements':achievements,
        })

    else:
        raise PermissionDenied


@login_required(login_url='login')
@csrf_exempt
def UpdateCart(request):
    if request.method == "POST" or request.is_ajax():
        userorder, c = UserOrder.objects.get_or_create(user=request.user)
        if request.method == "POST":
            action = request.POST.get('action')
            if action == "ADD" or action == "REMOVE":
                quiz_id = request.POST.get('quiz_id')
                try:
                    quiz = Quiz.objects.get(pk=quiz_id)
                except Quiz.DoesNotExist:
                    raise Http404("Quiz does not exist ")
                if action == "ADD":
                    userorder.add_to_cart(quiz)
                elif action == "REMOVE":
                    userorder.remove_from_cart(quiz)
            elif action == "EMPTY":
                userorder.empty_cart
        cart = json.loads(userorder.cart)
        total_price = userorder.current_cart_value
        total_items = len(cart.keys())
        return render(request, 'home/cart.html',{'cart':cart,'total_price':total_price,'total_items':total_items })
    else:
        raise PermissionDenied


@login_required(login_url='login')
def CheckOut(request):
    if request.method == "POST":
        order_id= Checksum.generateRandomString(6)
        try:
            userorder = UserOrder.objects.get(user=request.user)
            amount = userorder.current_cart_value
            userorder.add_to_processing(order_id)
            user_id = request.user.username
            paytmParams = dict()
            paytmParams["body"] = {
                "requestType": "Payment",
                "mid": mid,
                "websiteName": "WEBSTAGING",
                "orderId": order_id,
                "callbackUrl": "http://192.168.43.203:8000/handlerrequest/",
                "extendedInfo": {
                    "mercUnqRef": user_id,
                },
                "txnAmount": {
                    "value": str(amount),
                    "currency": "INR",
                },
                "userInfo": {
                    "custId": user_id,
                },
            }
            checksum = Checksum.generateSignature(json.dumps(paytmParams["body"]), MERCHANT_KEY)
            paytmParams["head"] = {
                "signature": checksum
            }
            post_data = json.dumps(paytmParams)
            url = "https://securegw-stage.paytm.in/theia/api/v1/initiateTransaction?mid="+mid+"&orderId="+order_id
            response = requests.post(url, data=post_data, headers={"Content-type": "application/json"}).json()
            print(json.dumps(response))
            signature= response["head"]["signature"]
            txn_token = response["body"]['txnToken']
            result_status = response["body"]['resultInfo']['resultStatus']
            verify = Checksum.verifySignature(json.dumps(response['body']), MERCHANT_KEY,signature)
            print(checksum)
            print(verify)

            if True:
                if result_status == "S":
                    return render(request, 'home/paytm.html',{'mid': mid ,'order_id':order_id,'txn_token': txn_token,'amount':amount})

        except UserOrder.DoesNotExist:
            pass
    else:
        raise PermissionDenied


@csrf_exempt
def handlerequest(request):
    # paytm will send you post request here
    if request.method =="POST":
        response_dict = dict()
        response_dict = dict(request.POST.items())
        paytmChecksum = response_dict['CHECKSUMHASH']
        response_dict.pop('CHECKSUMHASH', None)


        verify = Checksum.verifySignature(response_dict, MERCHANT_KEY, paytmChecksum)
        if verify:
            order_status = None

            if response_dict['RESPCODE'] == '01':
                order_id = response_dict['ORDERID']
                user = User.objects.get(username=response_dict['MERC_UNQ_REF'])
                userorder = UserOrder.objects.get(user=user)
                order_status ="SUCCESS"
                userorder.add_to_purchased(order_id,response_dict['TXNAMOUNT'])
                current = json.loads(userorder.orderpurchased)
                order_details = current[str(order_id)]
                return render(request, 'home/paytmstatus.html',{'order_status':order_status,"order_details":order_details})
            else:
                order_status = "FAILED"
                return render(request, 'home/paytmstatus.html',{'order_status':order_status,'message': response_dict['RESPMSG']})

    else:
        raise PermissionDenied


@login_required
def response(request, order_id):
    order_id = response_dict['ORDERID']
    user = User.objects.get(username=response_dict['MERC_UNQ_REF'])
    userorder = UserOrder.objects.get(user=user)
    return redirect(request, 'home/paytmstatus.html', {'order_status': order_status, "order_details": order_details})






