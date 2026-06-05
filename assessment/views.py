from django.shortcuts import render, redirect
from .questions import (LEVEL1_QUESTIONS, LEVEL2_DEPRESSION,
                        LEVEL2_NORMAL, LEVEL2_HAPPY)

# ── Scoring Engine ─────────────────────────────────────────
def get_level1_path(score, max_score=40):
    pct = (score / max_score) * 100
    if pct >= 55:   return 'depression'
    elif pct <= 30: return 'happy'
    else:           return 'normal'

def get_final_result(path, l1_score, l2_score):
    if path == 'depression':
        total = (l1_score * 0.4) + (l2_score * 0.6)
        pct   = round((total / 40) * 100)
        if pct >= 75:
            return {'category': 'Severe Depression',    'pct': pct,
                    'desc': 'You are experiencing significant depression symptoms that require immediate professional attention.',
                    'color': '#ef4444', 'bg': '#2d0a0a', 'border': '#dc2626', 'icon': '🔴'}
        elif pct >= 50:
            return {'category': 'Moderate Depression',  'pct': pct,
                    'desc': 'You are showing moderate signs of depression. Professional support is strongly recommended.',
                    'color': '#f97316', 'bg': '#1c0a00', 'border': '#ea580c', 'icon': '🟠'}
        else:
            return {'category': 'Mild Depression',      'pct': pct,
                    'desc': 'You are experiencing mild depressive symptoms. Early intervention can help greatly.',
                    'color': '#facc15', 'bg': '#1a1200', 'border': '#ca8a04', 'icon': '🟡'}

    elif path == 'happy':
        total = l2_score
        pct   = round((total / 40) * 100)
        if pct >= 75:
            return {'category': 'Flourishing & Very Happy', 'pct': pct,
                    'desc': 'You are thriving! Your mental wellbeing is excellent. Keep nurturing this positivity.',
                    'color': '#22c55e', 'bg': '#052e16', 'border': '#16a34a', 'icon': '🟢'}
        else:
            return {'category': 'Positively Happy',     'pct': pct,
                    'desc': 'You have a good foundation of happiness. Small improvements can elevate your wellbeing further.',
                    'color': '#4ade80', 'bg': '#052e16', 'border': '#22c55e', 'icon': '✅'}

    else:  # normal
        total = (l1_score * 0.5) + (l2_score * 0.5)
        pct   = round((total / 40) * 100)
        if pct >= 45:
            return {'category': 'Normal — Mild Stress',  'pct': pct,
                    'desc': 'You are generally stable but experiencing some stress. Healthy habits will help you maintain balance.',
                    'color': '#38bdf8', 'bg': '#0c1a2e', 'border': '#0284c7', 'icon': '🔵'}
        else:
            return {'category': 'Normal — Well Balanced', 'pct': pct,
                    'desc': 'You are in a stable and balanced mental state. Continue your healthy lifestyle.',
                    'color': '#818cf8', 'bg': '#1e1b4b', 'border': '#6366f1', 'icon': '💜'}

# ── Advice Engine ──────────────────────────────────────────
ADVICE = {
    'Severe Depression': {
        'urgent': True,
        'tips': [
            "Please contact a mental health professional immediately — this is a medical situation.",
            "Pakistan Umang Helpline: 0317-4288665 (free, confidential, 24/7).",
            "Reach out to one trusted person today — you do not have to face this alone.",
            "Avoid making major life decisions while in this state.",
            "Simple grounding: place both feet on the floor, breathe slowly — 4 counts in, 4 out.",
        ]
    },
    'Moderate Depression': {
        'urgent': False,
        'tips': [
            "Schedule an appointment with a therapist or counselor this week.",
            "Try a 10-minute walk outside daily — sunlight significantly impacts mood.",
            "Establish a consistent sleep schedule — same time every night.",
            "Limit social media to 30 minutes per day.",
            "Write 3 things you are grateful for each morning — small but powerful.",
        ]
    },
    'Mild Depression': {
        'urgent': False,
        'tips': [
            "Consider speaking to a counselor — early support prevents worsening.",
            "Exercise 3 times a week — even a 20-minute walk counts.",
            "Reconnect with one friend or family member this week.",
            "Reduce caffeine and alcohol — both worsen mood significantly.",
            "Try a creative outlet: journaling, drawing, or music.",
        ]
    },
    'Normal — Mild Stress': {
        'urgent': False,
        'tips': [
            "Practice mindfulness meditation — even 5 minutes daily reduces cortisol.",
            "Prioritize your tasks — use a simple to-do list to reduce overwhelm.",
            "Schedule one enjoyable activity per week just for yourself.",
            "Improve sleep hygiene — no screens 30 minutes before bed.",
            "Talk to someone you trust about what is stressing you.",
        ]
    },
    'Normal — Well Balanced': {
        'urgent': False,
        'tips': [
            "Maintain your healthy routines — consistency is key to wellbeing.",
            "Consider adding strength training or yoga to your week.",
            "Nurture your relationships — schedule quality time with loved ones.",
            "Set a meaningful goal for the next 3 months.",
            "Practice regular digital detox — one offline day per week.",
        ]
    },
    'Positively Happy': {
        'urgent': False,
        'tips': [
            "Keep a gratitude journal — write 3 things daily to sustain positivity.",
            "Plan a nature trip — mountains, forests or beaches amplify happiness.",
            "Share your positivity — volunteer or mentor someone.",
            "Set bigger personal goals — you have the energy to achieve more.",
            "Explore a new skill or hobby to deepen your sense of purpose.",
        ]
    },
    'Flourishing & Very Happy': {
        'urgent': False,
        'tips': [
            "You are thriving — protect this by maintaining your boundaries.",
            "Consider mentoring others — sharing wellbeing multiplies it.",
            "Plan experiences over things — travel, events, meaningful moments.",
            "Deepen spiritual or philosophical practice for lasting fulfillment.",
            "Document your happiness habits — teach others what works for you.",
        ]
    },
}

# ── Views ──────────────────────────────────────────────────
def home(request):
    request.session.flush()
    return render(request, 'assessment/home.html')

def level1(request):
    if request.method == 'POST':
        score = sum(int(request.POST.get(q['id'], 0))
                    for q in LEVEL1_QUESTIONS)
        path  = get_level1_path(score)
        request.session['l1_score'] = score
        request.session['path']     = path
        return redirect('level2')

    return render(request, 'assessment/level1.html',
                  {'questions': LEVEL1_QUESTIONS, 'total': len(LEVEL1_QUESTIONS)})

def level2(request):
    path = request.session.get('path', 'normal')
    qmap = {'depression': LEVEL2_DEPRESSION,
            'normal':     LEVEL2_NORMAL,
            'happy':      LEVEL2_HAPPY}
    questions = qmap[path]

    if request.method == 'POST':
        score = sum(int(request.POST.get(q['id'], 0))
                    for q in questions)
        l1    = request.session.get('l1_score', 0)
        result = get_final_result(path, l1, score)
        advice = ADVICE.get(result['category'], {})
        request.session['result'] = result
        request.session['advice'] = advice
        return redirect('result')

    label = {'depression': 'Mental Health Deep Dive',
             'normal':     'Wellbeing Assessment',
             'happy':      'Happiness & Fulfillment'}[path]

    return render(request, 'assessment/level2.html',
                  {'questions': questions, 'total': len(questions),
                   'path': path, 'label': label})

def result(request):
    result = request.session.get('result')
    advice = request.session.get('advice')
    if not result:
        return redirect('home')
    return render(request, 'assessment/result.html',
                  {'result': result, 'advice': advice})