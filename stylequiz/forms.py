from django import forms

class StyleQuizForm(forms.Form):
    QUESTION_CHOICES = {
        'q1': [
            ('a', 'Hoodie and sneakers'),
            ('b', 'Blazer and loafers'),
            ('c', 'Neutral t-shirt and slim jeans'),
            ('d', 'Activewear'),
        ],
        'q2': [
            ('a', 'Bold and bright'),
            ('b', 'Monochrome'),
            ('c', 'Earth tones'),
            ('d', 'Neon or pastels'),
        ],
        'q3': [
            ('a', 'Basketball court or the streets'),
            ('b', 'Business meetings or fine dining'),
            ('c', 'Modern art gallery or coffee shop'),
            ('d', 'Gym or yoga studio'),
        ],
        'q4': [
            ('a', 'Layered street jackets and cargo pants'),
            ('b', 'Suits, coats, or polished looks'),
            ('c', 'Muted tones and structured basics'),
            ('d', 'Track pants, trainers, and sporty fits'),
        ],
        'q5': [
            ('a', 'Kanye West, Travis Scott'),
            ('b', 'David Beckham, Meghan Markle'),
            ('c', 'Zara models, Pinterest boards'),
            ('d', 'Serena Williams, sports influencers'),
        ]
    }

    q1 = forms.ChoiceField(label="1. What would you wear on a casual day out?", choices=QUESTION_CHOICES['q1'], widget=forms.RadioSelect)
    q2 = forms.ChoiceField(label="2. Pick your favourite colour palette", choices=QUESTION_CHOICES['q2'], widget=forms.RadioSelect)
    q3 = forms.ChoiceField(label="3. What’s your ideal environment?", choices=QUESTION_CHOICES['q3'], widget=forms.RadioSelect)
    q4 = forms.ChoiceField(label="4. Pick a go-to outfit vibe:", choices=QUESTION_CHOICES['q4'], widget=forms.RadioSelect)
    q5 = forms.ChoiceField(label="5. Whose style do you admire most?", choices=QUESTION_CHOICES['q5'], widget=forms.RadioSelect)
