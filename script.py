

import os
import json
from django.core.wsgi import get_wsgi_application


os.environ['DJANGO_SETTINGS_MODULE'] = 'website.settings'
application = get_wsgi_application()



from home.models import Sitting, Quiz,Progress,SittingManager, UserOrder
from datetime import datetime



for sitting in Sitting.objects.all():
    quiz_time_in_sec = sitting.quiz.test_timing * 60
    time_elapsed = datetime.now() - sitting.start
    time_elapsed_in_sec = time_elapsed.total_seconds()
    if sitting.quiz.exam_paper == "True" and sitting.quiz.save_answers == False:
        if int(time_elapsed_in_sec - quiz_time_in_sec) > 10:
            progress, c = Progress.objects.get_or_create(user=sitting.user)
            progress.update_score(sitting.quiz, sitting)
            progress.update_all_quiz_records(sitting.quiz, sitting)
            sitting.mark_quiz_complete()
            sitting.delete()

    if sitting.quiz.exam_paper == "False":
        if (float(time_elapsed_in_sec - quiz_time_in_sec) / (60 * 60 * 24 * 7)) > 1:
            progress, c = Progress.objects.get_or_create(user=sitting.user)
            progress.update_score(sitting.quiz, sitting)
            progress.update_all_quiz_records(sitting.quiz, sitting)
            sitting.mark_quiz_complete()
            sitting.delete()




for order in UserOrder.objects.all():
    now = datetime.now()
    orderprocessing = json.loads(order.orderprocessing)
    l= list( k for k , v in orderprocessing.items() if float((datetime.now() - datetime.strptime(v[0]['time'], '%Y-%m-%d %H:%M:%S' )).total_seconds()/ (60* 60)) >= 12)
    if l:
        for key in l:
            orderprocessing.pop(str(key), None)

    order.orderprocessing = json.dumps(orderprocessing, indent=2)
    order.save()


for order in UserOrder.objects.all():
    now = datetime.now()
    orderpurchased = json.loads(order.orderpurchased)
    purchased_quizes = order.get_purchased_list
    for k , v in orderpurchased.items():
        cart= v[0]['order']
        days_elapsed = float((datetime.now() - datetime.strptime(v[0]['purchased_time'], '%Y-%m-%d %H:%M:%S')).total_seconds() / ( 60*60*24))
        if order:
            for key, value in cart.items():
                quiz = Quiz.objects.get(pk=int(key))
                if quiz:
                    if quiz.days < days_elapsed:
                        if int(key) in purchased_quizes:
                            purchased_quizes.remove(int(key))
    order.purchased_list = ','.join(map(str, purchased_quizes))
    order.save()

    
    
    
















  

