from django.shortcuts import render
from .forms import StyleQuizForm

def style_quiz(request):
    result = None

    if request.method == 'POST':
        form = StyleQuizForm(request.POST)
        if form.is_valid():
            answers = form.cleaned_data

          
            score = {
                'streetwear': 0,
                'formal': 0,
                'minimalist': 0,
                'sporty': 0
            }

            if answers['q1'] == 'a':
                score['streetwear'] += 1
            elif answers['q1'] == 'b':
                score['formal'] += 1
            elif answers['q1'] == 'c':
                score['minimalist'] += 1
            elif answers['q1'] == 'd':
                score['sporty'] += 1

            if answers['q2'] == 'a':
                score['streetwear'] += 1
            elif answers['q2'] == 'b':
                score['formal'] += 1
            elif answers['q2'] == 'c':
                score['minimalist'] += 1
            elif answers['q2'] == 'd':
                score['sporty'] += 1

           
            result = max(score, key=score.get)

    else:
        form = StyleQuizForm()

    return render(request, 'stylequiz/quiz.html', {'form': form, 'result': result})
