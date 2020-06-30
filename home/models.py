import os
from datetime import datetime
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, validate_comma_separated_integer_list, MinLengthValidator
from django.db import models
from django.conf import settings
from django.utils.timezone import now
from model_utils.managers import InheritanceManager
from django.db.models import Sum
import json
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.core.exceptions import ValidationError
from django.utils.html import mark_safe



class UserProfile(models.Model):
    def file_size(value):
        ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
        valid_extensions = ['.jpg', '.png', '.jpeg']
        if not ext.lower() in valid_extensions:
            raise ValidationError('Unsupported file extension.')

        limit = 150 * 1024
        if value.size > limit:
            raise ValidationError('File too large. Size should not exceed 150 kb.')

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    description = models.CharField(max_length=100, default='')
    address = models.CharField(max_length=100, default='')
    education = models.CharField(max_length=100)
    phone = models.CharField(default='', max_length=20)
    image = models.FileField(verbose_name="Profile Picture", upload_to='profile_image', blank=True,
                             validators=[file_size])

    def image_tag(self):
        return mark_safe('<img src="/media/%s" width="150" height="150" />' % (self.image))

    image_tag.short_description = 'Image'

    def save(self, *args, **kwargs):
        try:
            old = UserProfile.objects.get(id=self.id)
            if old.image != self.image:
                old.image.delete(save=False)
        except:
            pass
        super(UserProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

def create_profile(sender, **kwargs):
    user = kwargs["instance"]
    if kwargs["created"]:
        user_profile = UserProfile(user=user)
        user_profile.save()


post_save.connect(create_profile, sender=User)


class Notice(models.Model):
    about = models.CharField(max_length=100)
    notice = models.TextField()
    release_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.about

    class Meta:
        verbose_name = " Notices"
        verbose_name_plural = "Notices"


class ImportantForms(models.Model):
    description = models.CharField(verbose_name="Form description", max_length=200)
    myform = models.FileField(verbose_name="Upload the form", upload_to='important_forms')

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = "Important Form to upload"
        verbose_name_plural = "Important Forms to upload"


@receiver(models.signals.post_delete, sender=ImportantForms)
def auto_delete_form_on_delete(sender, instance, **kwargs):
    if instance.myform:
        if os.path.isfile(instance.myform.path):
            os.remove(instance.myform.path)


@receiver(models.signals.pre_save, sender=ImportantForms)
def auto_delete_form_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_file = ImportantForms.objects.get(pk=instance.pk).myform
    except ImportantForms.DoesNotExist:
        return False

    new_file = instance.myform
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class FormResponsesManager(models.Manager):
    def safe_save(self, user, form):
        try:
            this = self.filter(user=user, form=form)[0]
            this.delete()
        except:
            pass
        return False


class FormResponses(models.Model):
    def file_size(value):
        ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
        valid_extensions = ['.pdf']
        if not ext.lower() in valid_extensions:
            raise ValidationError('Unsupported file extension.Only pdfs are supported!')

        limit = 250 * 1024
        if value.size > limit:
            raise ValidationError('File too large. Size should not exceed 250 kb.')

    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    form = models.ForeignKey(ImportantForms, blank=True, null=True,
                             verbose_name="Form Description",
                             on_delete=models.CASCADE)
    form_response = models.FileField(verbose_name="Form submitted by user", upload_to='submitted_forms_by_users',
                                     validators=[file_size])

    objects = FormResponsesManager()

    class Meta:
        verbose_name = "Form submitted By User"
        verbose_name_plural = "Forms Submitted By Users"
        ordering = ['form']

        def __str__(self):
            return self.user.username


@receiver(models.signals.post_delete, sender=FormResponses)
def auto_delete_form_response_on_delete(sender, instance, **kwargs):
    if instance.form_response:
        if os.path.isfile(instance.form_response.path):
            os.remove(instance.form_response.path)


class MediaFile(models.Model):
    description = models.CharField(max_length=200, default='')
    myfile = models.FileField(verbose_name="File To Upload", upload_to='important_files')

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = "Important File"
        verbose_name_plural = "Important  Files to upload"


@receiver(models.signals.post_delete, sender=MediaFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    if instance.myfile:
        if os.path.isfile(instance.myfile.path):
            os.remove(instance.myfile.path)


@receiver(models.signals.pre_save, sender=MediaFile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_file = MediaFile.objects.get(pk=instance.pk).myfile
    except MediaFile.DoesNotExist:
        return False

    new_file = instance.myfile
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class Photos(models.Model):
    def validate_file_extension(value):
        ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
        valid_extensions = ['.jpg', '.png', '.jpeg']
        if not ext.lower() in valid_extensions:
            raise ValidationError('Unsupported file extension.')

    description = models.CharField(max_length=40, default='', blank=True)
    myphoto = models.FileField(verbose_name="Add photos to show in memories section", upload_to='my_photos',
                               blank=False,
                               validators=[validate_file_extension])

    class Meta:
        verbose_name = "Photo"
        verbose_name_plural = "Photos"


@receiver(models.signals.post_delete, sender=Photos)
def auto_delete_photos_on_delete(sender, instance, **kwargs):
    if instance.myphoto:
        if os.path.isfile(instance.myphoto.path):
            os.remove(instance.myphoto.path)


@receiver(models.signals.pre_save, sender=Photos)
def auto_delete_photos_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return False
    try:
        old_file = Photos.objects.get(pk=instance.pk).myphoto
    except Photos.DoesNotExist:
        return False

    new_file = instance.myphoto
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class Category(models.Model):
    category = models.CharField(
        verbose_name="Category Name",
        max_length=50, blank=False,
        unique=True)
    description = models.CharField(
        verbose_name="Category description",
        max_length=250, blank=False)

    class Meta:
        verbose_name = "Quiz Category"
        verbose_name_plural = "Quiz Categories"

    def __str__(self):
        return self.category


class Question(models.Model):
    quiz = models.ManyToManyField('Quiz',
                                  verbose_name="Quiz",
                                  blank=True)

    content = models.TextField(max_length=1000,
                               blank=False,
                               help_text="Enter the question text that "
                                         "you want displayed",
                               verbose_name='Question')

    explanation = models.CharField(max_length=2000,
                                   blank=True,
                                   help_text="Explanation to be shown "
                                             "after the question has "
                                             "been answered.",
                                   verbose_name='Explanation')
    max_mark = models.PositiveIntegerField(blank=False,
                                           null=True,
                                           validators=[MaxValueValidator(100)],
                                           verbose_name="Max Mark",
                                           help_text="Max mark of this question.")
    negative_marking = models.PositiveIntegerField(blank=True,
                                                   null=True,
                                                   default=0,
                                                   verbose_name="Negative marking",

                                                   help_text="No of marks reduced for attempting wrong answer.Leave blank for no negative marks")

    objects = InheritanceManager()

    def __str__(self):
        return self.content

    class Meta:
        verbose_name = "All Question"
        verbose_name_plural = "All Questions"
       


class MCQuestion(Question):
    option1 = models.CharField(max_length=1000,
                               blank=False,
                               verbose_name='option1')
    option2 = models.CharField(max_length=1000,
                               blank=False,
                               verbose_name='option2')
    option3 = models.CharField(max_length=1000,
                               blank=False,
                               verbose_name='option3')
    option4 = models.CharField(max_length=1000,
                               blank=False,
                               verbose_name='option4')
    choose = (('A', 'option1'), ('B', 'option2'), ('C', 'option3'), ('D', 'option4'))
    answer = models.CharField(max_length=1, choices=choose, blank=False)

    def check_if_correct(self, guess):
        if self.answer == guess:
            return True
        else:
            return False

    def get_answers(self):
        if self.answer == 'A':
            return {'content': self.option1}
        if self.answer == 'B':
            return {'content': self.option2}
        if self.answer == 'C':
            return {'content': self.option3}
        if self.answer == 'D':
            return {'content': self.option4}

    class Meta:
        verbose_name = " Multiple_Choice_Question"
        verbose_name_plural = "Multiple_Choice_Questions"


class TF_Question(Question):
    correct = models.BooleanField(blank=False,
                                  default=False,
                                  help_text="Tick this if the question "
                                            "is true. Leave it blank for"
                                            " false.",
                                  verbose_name="Correct")

    def check_if_correct(self, guess):
        if guess == "True":
            guess_bool = True
        elif guess == "False":
            guess_bool = False
        else:
            return False

        if guess_bool == self.correct:
            return True
        else:
            return False

    def get_answers(self):
        return [{'correct': self.check_if_correct("True"),
                 'content': 'True'},
                {'correct': self.check_if_correct("False"),
                 'content': 'False'}]

    class Meta:
        verbose_name = "True/False Question"
        verbose_name_plural = "True/False Questions"



class Essay_Question(Question):
    def check_if_correct(self, guess):
        return False

    class Meta:
        verbose_name = "Essay style question"
        verbose_name_plural = "Essay style questions"



class Quiz(models.Model):
    posting_date = models.DateTimeField(auto_now=True)
    title = models.CharField(
        verbose_name="Quiz Title",
        help_text=" name of quiz you want to host",
        max_length=250,
        unique=True, null=True)
    category = models.ForeignKey(Category,
                                verbose_name="Quiz Category",
                                blank=False,
                                on_delete=models.CASCADE)
    description = models.CharField(max_length=1000,
                                   verbose_name="Description",
                                   blank=True, help_text="a description of the quiz")
    choose1 = (('True', 'Paid'), ('False', 'Free'))
    is_paid = models.CharField(max_length=5, choices=choose1, blank=False, verbose_name="Quiz Charge",
                                  help_text = "Select if the quiz will be paid or free", )
    price = models.PositiveIntegerField( default = 0, blank=False, verbose_name="Quiz Price",
                               help_text="Amount (in Rs )to be paid to unlock this quiz", )
    days=models.PositiveIntegerField( default = 0, blank=False, verbose_name="Days",
                               help_text="No of days to unlock the quiz after paying", )

    passing_percentage = models.SmallIntegerField(
        blank=True, default=0,
        verbose_name="Pass percentage",
        help_text="Percentage required to pass exam.",
        validators=[MaxValueValidator(100)])
    test_timing = models.PositiveIntegerField(
        blank=True, default=60,
        verbose_name="Time Alloted(in min.)",
        help_text=" Time Limit Of Exam( in minutes)"
    )
    choose2 = (('True', 'Exam Paper'), ('False', 'Practice Paper'))
    exam_paper = models.CharField(max_length=5, choices=choose2, blank=False, verbose_name=" Paper Type",
                                  help_text="If Exam Paper, the result of each  attempt by a user will be stored. Necessary for marking.", )

    secret_key = models.CharField(max_length=50, help_text="If set only the allowed users can access the exam",
                                  blank=True, validators=[MinLengthValidator(8)], default="")

    save_answers = models.BooleanField(
        blank=False, default=False,
        help_text="If yes, All the answers of user will be saved",
        verbose_name="SAVE ANSWERS OF USER")

    single_attempt = models.BooleanField(
        blank=False, default=False,
        help_text="If yes, only one attempt by"
                  " a user will be permitted.",
        verbose_name="Single Attempt")
    hide_results = models.BooleanField(
        blank=False, default=False,
        help_text="If yes, User can't see his result unless you come back and mark this true",
        verbose_name="Hide Results")
    hide_quiz = models.BooleanField(
        blank=False, default=False,
        help_text="If yes, User can't see his Quiz in the quiz list",
        verbose_name="HIDE QUIZ")
    user_marks = models.TextField(default='{}', verbose_name="Marks of Users",  help_text="Marks of users will be recorded here. Necessary for making ranks.")


    class Meta:
        verbose_name = "Online Test"
        verbose_name_plural = "Online Tests"

    def add_or_update_user_score(self,user,marks):
        current = json.loads(self.user_marks)
        current[str(user.username)] = marks
        self.user_marks=json.dumps(current,indent=2)
        self.save()

    def get_user_rank(self,user):
        data = json.loads(self.user_marks)
        if data:
            s_data = sorted(data.items(), key=lambda item: item[1],reverse=True)
            rank, count, previous = 0, 0, None
            for key, val in s_data:
                count += 1
                if val != previous:
                    rank += count
                    previous = val
                    count = 0
                if key == str(user.username):
                    return rank







    def __str__(self):
        return self.title




class SittingManager(models.Manager):
    def new_sitting(self, user, quiz):
        question_set = quiz.question_set.all() \
            .select_subclasses()
        question_set = [item.id for item in question_set]
        questions = ",".join(map(str, question_set))
        new_sitting = self.create(user=user,
                                  quiz=quiz,
                                  question_order=questions,
                                  unanswered_list=questions,
                                  correct_questions="",
                                  incorrect_questions="",
                                  current_score=0,
                                  complete=False,
                                  user_answers='{}',
                                  time_left=quiz.test_timing
                                  )
        return new_sitting

    def user_sitting(self, user, quiz):
        if quiz.single_attempt is True:
            if Progress.objects.filter(user=user) \
                    .exists():
                user_progress = Progress.objects.get(user=user)
                user_quizes = json.loads(user_progress.score)
                quiz_check = user_quizes.get(str(quiz.id), None)
                if quiz_check:
                    return False

        try:
            sitting = self.get(user=user, quiz=quiz, complete=False)
        except Sitting.DoesNotExist:
            sitting = self.new_sitting(user, quiz)
        except Sitting.MultipleObjectsReturned:
            sitting = self.filter(user=user, quiz=quiz, complete=False)[0]
        return sitting


class Sitting(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, verbose_name="Quiz", on_delete=models.CASCADE)
    question_order = models.CharField(
        max_length=1024,
        verbose_name="Question Order",
        validators=[validate_comma_separated_integer_list])

    unanswered_list = models.CharField(
        max_length=1024,
        verbose_name="Unanswerd List",
        validators=[validate_comma_separated_integer_list])
    correct_questions = models.CharField(
        max_length=1024,
        blank=True,
        verbose_name="Correct questions",
        validators=[validate_comma_separated_integer_list])
    incorrect_questions = models.CharField(
        max_length=1024,
        blank=True,
        verbose_name="Incorrect questions and Answered Essay questions",
        validators=[validate_comma_separated_integer_list])
    current_score = models.IntegerField(verbose_name="Current Score")

    complete = models.BooleanField(default=False, blank=False,
                                   verbose_name="Complete")

    user_answers = models.TextField(blank=True, default='{}',
                                    verbose_name="User Answers")
    start = models.DateTimeField(auto_now_add=True,
                                 verbose_name="started on")
    time_left = models.DecimalField(
        blank=True, max_digits=5, decimal_places=2,
        verbose_name="Time Remaining (in min.)",
        help_text=" remaining time availaible to student (in minutes)"
    )

    end = models.DateTimeField(null=True, blank=True, verbose_name="completed on")
    objects = SittingManager()

    def add_to_score(self, points):
        self.current_score += int(points)
        self.save()

    def update_time_left(self, time_left_in_min):
        self.time_left = time_left_in_min
        self.save()

    @property
    def get_current_score(self):
        return self.current_score

    def mark_quiz_complete(self):
        self.complete = True
        self.end = now()
        self.save()

    @property
    def get_unanswered_list(self):
        return [int(q) for q in self.unanswered_list.split(',') if q]

    def remove_unanswered_list(self, question):
        current = self.get_unanswered_list
        if question.id in current:
            current.remove(question.id)
        self.unanswered_list = ','.join(map(str, current))
        self.save()

    def add_unanswered_list(self, question):
        current = self.get_unanswered_list
        if question.id not in current:
            if len(self.unanswered_list) > 0:
                self.unanswered_list += ','
            self.unanswered_list += str(question.id)
            self.save()

    @property
    def get_incorrect_questions(self):
        return [int(q) for q in self.incorrect_questions.split(',') if q]

    def remove_incorrect_question(self, question):
        current = self.get_incorrect_questions
        if question.id in current:
            current.remove(question.id)
        self.incorrect_questions = ','.join(map(str, current))
        self.save()

    def add_incorrect_question(self, question):
        current = self.get_incorrect_questions
        if question.id not in current:
            if len(self.incorrect_questions) > 0:
                self.incorrect_questions += ','
            self.incorrect_questions += str(question.id)
            self.save()

    def add_correct_question(self, question):
        current = self.get_correct_questions
        if question.id not in current:
            if len(self.correct_questions) > 0:
                self.correct_questions += ','
            self.correct_questions += str(question.id)
            self.save()

    @property
    def get_correct_questions(self):
        return [int(q) for q in self.correct_questions.split(',') if q]

    def remove_correct_question(self, question):
        current = self.get_correct_questions
        if question.id in current:
            current.remove(question.id)
        self.correct_questions = ','.join(map(str, current))
        self.save()

    @property
    def get_percent_correct(self):
        dividend = float(self.current_score)
        divisor = Question.objects.filter(quiz=self.quiz.id).aggregate(Sum('max_mark'))['max_mark__sum']
        if divisor < 1:
            return 0  # prevent divide by zero error

        if dividend > divisor:
            return 100

        correct = float(round((dividend / divisor) * 100, 2))

        if correct >= 1:
            return correct
        else:
            return 0

    @property
    def check_if_passed(self):
        return self.get_percent_correct >= self.quiz.passing_percentage

    @property
    def result_message(self):
        if self.check_if_passed:
            return "PASS"
        else:
            return "FAIL"

    def add_update_or_remove_user_answer(self, question, guess):
        current = json.loads(self.user_answers)
        if guess == "_NO_ANSWER_":
            current.pop(str(question.id), None)
        else:
            current[str(question.id)] = {'question': question.content, 'guess': guess}
        self.user_answers = json.dumps(current, indent=2)
        self.save()

    class Meta:
        verbose_name = "User's Answers of exam"
        verbose_name_plural = "User's Answers of exams"


class Progress(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.CASCADE)
    all_quiz_records = models.TextField(default='{}', verbose_name="All Quiz Appeared Till Date", )
    score = models.TextField(default='{}', verbose_name="Current Quiz Scores", )

    def update_score(self, quiz,sitting):
        """
        Pass in quiz object, amount to increase score
        and max possible.
        Does not return anything.
        """
        quiz_test = Quiz.objects.filter(pk=quiz.id) \
            .exists()

        if any([item is False for item in [quiz_test
                                           ]]):
            return "error quiz does not exist or invalid score"

        percentage_scored = sitting.get_percent_correct
        total_score = sitting.current_score
        quiz.add_or_update_user_score(sitting.user,total_score)
        result = sitting.result_message
        max_mark = Question.objects.filter(quiz=quiz).aggregate(Sum('max_mark'))['max_mark__sum']
        quiz_passing_percentage = quiz.passing_percentage
        marks_deducted = 0
        positive_marks = 0
        question_correct = 0
        for q in sitting.correct_questions.split(','):
            if q:
                question_correct += 1
                correct_question = Question.objects.get(pk=q)
                positive_marks += correct_question.max_mark

        question_incorrect = 0
        incorrect_answered_mark = 0
        for q in sitting.incorrect_questions.split(','):
            if q:
                question_incorrect += 1
                incorrect_question = Question.objects.get(pk=q)
                incorrect_answered_mark += incorrect_question.max_mark
                marks_deducted += incorrect_question.negative_marking

        question_left = 0
        marks_left = 0
        for q in sitting.unanswered_list.split(','):
            if q:
                question_left += 1
                left_question = Question.objects.get(pk=q)
                marks_left += left_question.max_mark

        current = json.loads(self.score)
        now = datetime.now()
        if quiz.exam_paper == "True":
            quiz_category ="Exam Paper"
        else:
            quiz_category = "Practice Paper"

        current[str(quiz.id)] = {'quiz_title': quiz.title,
                            'quiz_category': quiz_category,
                            'completed_on': now.strftime('%d-%m-%Y %H:%M'),
                            'no_of_question_correct': question_correct,
                            'no_of_question_incorrect': question_incorrect,
                            'no_of_question_left': question_left,
                            'correct_answered_marks': positive_marks,
                            'incorrect_answered_mark': incorrect_answered_mark,
                            'marks_left': marks_left,

                            'negative_marks': marks_deducted,
                            'net_score': total_score,
                            'max_mark_of_quiz': max_mark,
                            'percentage_scored': percentage_scored,
                            'quiz_passing_percentage': quiz_passing_percentage,
                            'result': result}
        self.score = json.dumps(current, indent=2)


        new = json.loads(self.all_quiz_records)
        if not new.get('all_records'):
            new['all_records'] = {'no_of_exams_appeared': 0,
                                  'no_of_exams_passed': 0,
                                  'no_of_practice_paper_appeared': 0,
                                  'no_of_practice_paper_passed': 0
                                  }
        self.all_quiz_records = json.dumps(new, indent=2)
        self.save()

    def update_all_quiz_records(self,quiz,sitting):
        new = json.loads(self.all_quiz_records)
        if quiz.exam_paper == "True":
            new['all_records']['no_of_exams_appeared'] += 1
            if sitting.check_if_passed:
                new['all_records']['no_of_exams_passed'] += 1

        else:
            new['all_records']['no_of_practice_paper_appeared'] += 1
            if sitting.check_if_passed:
                new['all_records']['no_of_practice_paper_passed'] += 1

        self.all_quiz_records = json.dumps(new, indent=2)
        self.save()


    class Meta:
        verbose_name = "User's Quiz  Progress Record "
        verbose_name_plural = "User's Quiz Progress Records"



class UserOrder(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name="User", on_delete=models.CASCADE)
    cart = models.TextField(default='{}', verbose_name="Orders in User Cart", )
    current_cart_value = models.PositiveIntegerField(
        blank=True, default= 0,
        verbose_name="Current_cart_value",
        help_text=" Total Cart amount in Rs"
    )
    purchased_list = models.CharField(
        max_length=2024,
        blank=True,
        verbose_name="Purchased Quiz Ids",
        validators=[validate_comma_separated_integer_list])
    orderprocessing = models.TextField(default='{}', verbose_name="Order in Progress",help_text="Live order being processed by Paytm" )
    orderpurchased = models.TextField(default='{}', verbose_name="Order History", )

    @property
    def get_purchased_list(self):
        return [int(q) for q in self.purchased_list.split(',') if q]

    @property
    def empty_cart(self):
        self.cart = '{}'
        self.current_cart_value = 0
        self.save()




    def add_to_cart(self, quiz):
        current = json.loads(self.cart)
        object = current.get(str(quiz.id))
        if object:
            pass
        else:
            current[str(quiz.id)] = {'quiz_title': quiz.title,
                                     'price': quiz.price,
                                     'for_days':quiz.days,
                                     }
            self.current_cart_value += int(quiz.price)

        self.cart = json.dumps(current, indent=2)
        self.save()
    def remove_from_cart(self,quiz):
        current = json.loads(self.cart)
        object = current.get(str(quiz.id))
        if object:
            current.pop(str(quiz.id),None)
            self.current_cart_value -= int(quiz.price)
        else:
            pass
        self.cart = json.dumps(current, indent=2)
        self.save()



    def add_to_processing(self, order_id):
        now = datetime.now()
        current = json.loads(self.orderprocessing)
        cart = json.loads(self.cart)
        current[str(order_id)] = {'time': now.strftime('%Y-%m-%d %H:%M:%S'),
                                  'amount': self.current_cart_value,
                                  'cart': cart},
        self.orderprocessing = json.dumps(current, indent=2)
        self.save()

    def delete_processing_order(self,order_id):
        current = json.loads(self.orderprocessing)
        current.pop(str(order_id),None)
        self.orderprocessing = json.dumps(current, indent=2)
        self.save()

    def add_to_purchased(self,order_id,amount):
        now = datetime.now()
        current = json.loads(self.orderpurchased)
        orderprocessing = json.loads(self.orderprocessing)
        ordersuccessful = orderprocessing[str(order_id)][0]['cart']
        purchased_quizes = self.get_purchased_list
        if ordersuccessful:
            for key, value in ordersuccessful.items():
                if int(key) not in purchased_quizes:
                    if len(self.purchased_list) > 0:
                        self.purchased_list += ','
                    self.purchased_list += str(key)


        current[str(order_id)]= {'purchased_time': now.strftime('%Y-%m-%d %H:%M:%S'),
                                 'amount_paid': str(amount),
                                 'order':ordersuccessful,
                                }
        self.orderpurchased = json.dumps(current, indent=2)
        orderprocessing.pop(str(order_id),None)
        self.orderprocessing = json.dumps( orderprocessing, indent=2)
        self.remove_from_cart
        self.save()


    class Meta:
        verbose_name = "User Order"
        verbose_name_plural = "Users Order"
