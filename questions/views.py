from django.shortcuts import render, redirect, get_object_or_404
from django.utils.timezone import now
from .models import Question
from .forms import form_for_question, form_for_answer
from store.models import Customer  

def askQ(request):
    if request.method == "POST":
        form = form_for_question(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.user = request.user
            question.save()  
            print(f"Question created with ID: {question.id}")  
            return redirect('questions:list')  
        else:
            print("Form is not valid")
    else:
        form = form_for_question()

    return render(request, 'ask_q.html', {'form': form})



def listQ(request):
    questions = Question.objects.all()
    return render(request, 'list.html', {'questions': questions})  



def answerQ(request, question_id):
    question = get_object_or_404(Question, id=question_id)

    
    if not request.user.is_staff:
        return redirect('questions:list')  
    
    if request.method == "POST":
        form = form_for_answer(request.POST, instance=question)
        if form.is_valid():
            question.answered = now()  
            form.save()
            return redirect('questions:list')

    else:
        form = form_for_answer(instance=question)

    return render(request, 'answer_q.html', {'form': form, 'question': question})




def unanswered_questions(request):

    if not request.user.is_staff:
        return redirect('questions:list') 

    unanswered = Question.objects.filter(answer__isnull=True)
    count = unanswered.count()
    return render(request, 'unanswered_admin.html', {
        'unanswered_questions': unanswered,
        'count': count,
    })