from http import client

from django.shortcuts import render
import json
import base64
import io
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from google import genai
from google.genai import types

client = genai.Client()

# Create your views here.
def slide_builder(request):
    return render(request, 'slide_builder.html')

#to generate slide titles
def _generate_slide_titles(topic: str) -> list[str]:
    prompt = f"""
    You generate slide titles for presentations.

    Return exactly five slide titles for a beginner friendly talk about "{topic}".

    MUST return ONLY valid JSON in this exact structure:

    {{
    "slides": [
    {{"title": "..."}},
    {{"title": "..."}},
    {{"title": "..."}},
    {{"title": "..."}},
    {{"title": "..."}}
    ]
    }}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            content=[{"text": prompt}],
            config=types.GenerateContentConfig(response_mime_type="application/json"),
        )

        raw = ""
        for part in response.parts:
            if part.text:
                raw += part.text.strip()
        
        print("Raw title generation response:", raw)

        data = json.loads(raw)
        titles = [s["title"] for s in data.get("slides", []) if "title" in s]

        if len(titles) == 5:
            return titles
    
    except Exception as e:
        print("Error generating slide titles:", e)


    return [
        f"Introduction to {topic}",
        f"Core ideas of {topic}",
        f"How {topic} works",
        f"Use cases of {topic}",
        f"Future of {topic}",
    ]


def _generate_slide_image(title: str, topic: str) -> str | None:
    prompt = (
        f" Create a mordern presentation slide style illustration for a talk about {topic}."
        f" The focus of this slide is: {title}."
        "Minimal, clean, soft colours on a light background, no dense body text."
    )

    print("Generating image with prompt:", prompt)

    try:
        response = client.models.generate_content(
            model="gemini-3-pro-image-preview",
            contents=prompt,
            config=types.GenerateContentConfig(
                image_config=types.ImageConfig(
                    aspect_ratio="16:9",
                )
            ),
        )

        print("AI image generation response:", response)

        for part in response.parts:
            if part.inline_data:
                image_bytes = part.inline_data.data
                encoded = base64.b64encode(image_bytes).decode('ascii')
                mime_type = part.inline_data.mime_type or "image/jpeg"
                data_url = f"data:{mime_type};base64,{encoded}"
                print("Generated image data URL:", data_url[:100] + "...")  # Print the beginning of the data URL for verification
                return data_url
    except Exception as e:
            print("Error generating slide image:", e)

    return None

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

    print(f"Topic from client: {topic}")

    titles = _generate_slide_titles(topic)
    print(f"AI Generated slide titles: {titles}")


        
    slides = []
    for idx, title in enumerate(titles):
        image_url = _generate_slide_image(title, topic)
        if image_url is None:
            image_url = ("https://images.unsplash.com/photo-1635070041078-e363dbe005cb?auto=format&fit=crop&w=800&q=80")
        
        slides.append({
            'id': idx,
            'title': title,
            'image': image_url,
        })



    return JsonResponse({'slides': slides})