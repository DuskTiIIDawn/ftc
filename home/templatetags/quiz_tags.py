from django import template
from django.db.models import Sum
from home.models import Question,Sitting,Quiz,UserOrder
import json

register = template.Library()


@register.simple_tag
def max_mark(quiz_id):
    return Question.objects.filter(quiz=quiz_id).aggregate(Sum('max_mark'))['max_mark__sum']


@register.simple_tag
def get_answer(user,quiz_id,question_id):
    quiz = Quiz.objects.get(pk=quiz_id)
    sitting = Sitting.objects.user_sitting(user, quiz)
    user_answers = json.loads(sitting.user_answers)
    q_ans = user_answers.get(str(question_id))
    if q_ans:
        ans = q_ans['guess']
        return ans
    else:
        return q_ans

@register.simple_tag
def get_time_left(user,quiz_id):
    quiz = Quiz.objects.get(pk=quiz_id)
    sitting = Sitting.objects.user_sitting(user, quiz)
    time_left = sitting.time_left
    return time_left

@register.simple_tag
def ckeck_if_sitting_exist(user,quiz_id):
    quiz = Quiz.objects.get(pk=quiz_id)
    if Sitting.objects.filter(user=user, quiz=quiz, complete=False) \
            .exists():
        mysitting = "True"
    else:
        mysitting = "False"
    return mysitting

@register.simple_tag
def is_unlocked(request,quiz):
    if quiz.secret_key == request.session.get(str(quiz.id),False):
        return True
    else:

        return False


@register.simple_tag
def check_if_secret_key(quiz):
    if quiz.secret_key != "":
        return True
    else:
        return False


@register.simple_tag
def check_if_hide_result(quiz_id):
    try:
        quiz = Quiz.objects.get(pk=int(quiz_id))
        if quiz.hide_results == True:
            return True
        else:
            return False
    except Quiz.DoesNotExist:
        return "NO"

@register.simple_tag
def get_percent(dividend,divisor):
    if divisor != 0:
        return float(round((dividend / divisor) * 100, 2))
    else:
        return 0


@register.simple_tag
def cart_list(user):
    if UserOrder.objects.filter(user=user) \
            .exists():
        userorder = UserOrder.objects.filter(user=user)[0]
        cart = json.loads(userorder.cart)
        l = list(int(k) for k,v in cart.items())

    else:
        l=[]
    return l

