from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.
def slide_builder(request):
    return render(request, 'slide_builder.html')

@csrf_exempt
def generate_slides(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only Post Request Method Allowed'}, status=405)
    
    try:
        body = json.loads(request.body.decode('utf-8'))

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    
    topic = (body.get('topic') or "").strip()
    if not topic:
        topic = "Random Topic "

    titles = [
        f"Introduction to {topic}",
        f"Core ideas of {topic}",
        f"How {topic} works",
        f"Use cases of {topic}",
        f"Future of {topic}",]
        
    slides = []
    for idx, title in enumerate(titles):
        slides.append({
            'id': idx,
            'title': title,
            'image': "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&w=800&q=80",
        })


    return JsonResponse({'slides': slides})