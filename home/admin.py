from django.contrib import admin
from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple
from home.models import (Notice, Quiz, Question, MCQuestion, TF_Question, Essay_Question, 
Category,Progress,Sitting,UserProfile,MediaFile,Photos,ImportantForms,FormResponses,UserOrder)

admin.site.register(Notice)
admin.site.register(Category)
admin.site.register(UserOrder)


@admin.register(MediaFile)
class MediaFile(admin.ModelAdmin):
    class Media:
        js = ('//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
              '/static/home/admin/progress_bar.js',)


@admin.register(Photos)
class PhotosAdmin(admin.ModelAdmin):
    search_fields = ('description',)
    list_display = ('myphoto', 'description')

@admin.register(ImportantForms)
class ImportantForms(admin.ModelAdmin):
    list_display = ('description', 'myform',)
    search_fields = ('description',)



@admin.register(FormResponses)
class FormResponses(admin.ModelAdmin):
    list_display = ('user', 'form', 'form_response')
    search_fields = ('user__username','form',)
    list_filter = ('user', 'form',)
    readonly_fields = ('user', 'form','form_response')
   


class QuestionAdminForm(forms.ModelForm):
    class Meta:
        model = Question
        exclude = []

    category = forms.CharField(
        required=False,
        label="Question Category",
        disabled=True,
    )

    def __init__(self, *args, **kwargs):
        super(QuestionAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            if hasattr(self.instance, 'mcquestion'):
                self.fields['category'].initial = "Multiple Choice Question"
            elif hasattr(self.instance, 'tf_question'):
                self.fields['category'].initial = "True False Question"
            elif hasattr(self.instance, 'essay_question'):
                self.fields['category'].initial = "Eassy Type Question"


class QuizAdminForm(forms.ModelForm):
    class Meta:
        model = Quiz
        exclude = []

    questions = forms.ModelMultipleChoiceField(
        queryset=Question.objects.all().select_subclasses(),
        required=False,
        label="Questions",
        widget=FilteredSelectMultiple(
            verbose_name="Questions",
            is_stacked=False))

    def __init__(self, *args, **kwargs):
        super(QuizAdminForm, self).__init__(*args, **kwargs)
        if self.instance.pk:
            self.initial['questions'] = \
                self.instance.question_set.all().select_subclasses()

    def save(self, commit=True):
        quiz = super(QuizAdminForm, self).save(commit=False)
        quiz.save()
        quiz.question_set.set(self.cleaned_data['questions'])
        self.save_m2m()
        return quiz




@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions
    form = QuizAdminForm
    list_display = ('title', 'posting_date', 'description')
    search_fields = ('title',)
    readonly_fields = ('posting_date',)

    class Media:
        js = ('//ajax.googleapis.com/ajax/libs/jquery/3.4.1/jquery.min.js',
              '/static/home/admin/assets_admin.js',)
    


@admin.register(Sitting)
class SittingAdmin(admin.ModelAdmin):
    list_display = ('user', 'quiz','complete','start','end')
    search_fields = ('user__username','quiz__title',)
    list_filter = ('quiz', 'user',)
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Progress)
class ProgressAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
    list_filter = ('user',)
    def has_add_permission(self, request, obj=None):
        return False

class UserProfileInline(admin.TabularInline):
    model = UserProfile
    extra = 1
    can_delete = False

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)
    list_filter = ('user',)
    readonly_fields = ['image_tag','image']

    def has_add_permission(self, request, obj=None):
        return False




@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    form = QuestionAdminForm
    list_display = ('q_category', 'max_mark', 'negative_marking', 'content')

    def q_category(self, obj):
        if obj.pk:
            if hasattr(obj, 'mcquestion'):
                return ("Multiple Choice Question")
            elif hasattr(obj, 'tf_question'):
                return ("True False Question")
            elif hasattr(obj, 'essay_question'):
                return ("Eassy Type Question")

    search_fields = ('content',)
    list_filter = ('quiz',)
    filter_vertical = ('quiz',)

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(MCQuestion)
class MCQuestionAdmin(admin.ModelAdmin):
    list_display = ('max_mark', 'negative_marking', 'content')
    search_fields = ('content', )
    fields = (
    'quiz',  'content', 'option1', 'option2', 'option3', 'option4', 'answer', 'max_mark', 'negative_marking',
    'explanation',)

    list_filter = ('quiz',)
    filter_vertical = ('quiz',)


@admin.register(TF_Question)
class TF_QuestionAdmin(admin.ModelAdmin):
    list_display = ( 'max_mark', 'negative_marking', 'content')
    search_fields = ('content', )
    fields = ('quiz',  'content', 'correct', 'max_mark', 'negative_marking', 'explanation',)
    list_filter = ('quiz', )
    filter_vertical = ('quiz',)


@admin.register(Essay_Question)
class Essay_QuestionAdmin(admin.ModelAdmin):
    list_display = ( 'max_mark', 'negative_marking', 'content')
    search_fields = ('content', )
    fields = ('quiz', 'content', 'max_mark', 'explanation',)
    list_filter = ('quiz',)
    filter_vertical = ('quiz',)
