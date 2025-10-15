from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
import os
import pickle
import numpy as np
import google.generativeai as genai
from django.conf import settings
from .ai_counselor import counselor
from .models import CareerSurvey 


# ====================================================
# 🔹 Career Prediction View
# ====================================================

# ... your existing imports and model loading code ...
# Add these imports at the top
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from io import BytesIO
import base64
from datetime import datetime

# Add this function to your views.py
@csrf_exempt
@require_POST
def download_career_report(request):
    """Generate and download a PDF career report"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        predictions = data.get('predictions', [])
        counseling_data = request.session.get('counseling_data', {})
        conversation_history = request.session.get('conversation_history', [])
        
        # Create PDF in memory
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter, 
                              topMargin=0.5*inch, bottomMargin=0.5*inch,
                              leftMargin=0.5*inch, rightMargin=0.5*inch)
        
        # Create styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#0c4a6e'),
            spaceAfter=30,
            alignment=1  # Center aligned
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#0369a1'),
            spaceAfter=12,
            spaceBefore=20
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#334155'),
            spaceAfter=12
        )
        
        # Build the story (content)
        story = []
        
        # Header
        story.append(Paragraph("NovaX Career Intelligence Report", title_style))
        story.append(Paragraph(f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                             ParagraphStyle('Date', parent=styles['Normal'], fontSize=9, alignment=1, textColor=colors.gray)))
        story.append(Spacer(1, 20))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", heading_style))
        summary_text = """
        This comprehensive career assessment analyzes your personality traits, aptitudes, and work preferences 
        to identify career paths where you're most likely to excel and find fulfillment. The recommendations 
        are based on psychological research and data-driven analysis of successful professionals.
        """
        story.append(Paragraph(summary_text, normal_style))
        story.append(Spacer(1, 15))
        
        # Top Career Recommendations
        story.append(Paragraph("Top Career Recommendations", heading_style))
        
        if predictions:
            # Create table for predictions
            prediction_data = [['Rank', 'Career Path', 'Match Score', 'Key Strengths']]
            
            strength_mapping = {
                'C_score': 'Organization & Detail-Oriented',
                'O_score': 'Openness to Innovation',
                'E_score': 'Social & Communication Skills', 
                'A_score': 'Team Collaboration',
                'N_score': 'Stress Resilience',
                'Numerical_Aptitude': 'Analytical Thinking',
                'Verbal_Aptitude': 'Communication Excellence',
                'Abstract_Reasoning': 'Problem-Solving',
                'Logical_Reasoning': 'Logical Analysis',
                'Spatial_Aptitude': 'Spatial Intelligence',
                'Enjoy_Teamwork': 'Collaborative Spirit',
                'Creative_Thinking': 'Creative Innovation',
                'Attention_to_Detail': 'Precision Focus'
            }
            
            for i, pred in enumerate(predictions[:3], 1):
                # Determine top 3 strengths for this career
                strengths = get_strengths_for_career(counseling_data)
                strength_text = ", ".join(strengths[:3])
                
                prediction_data.append([
                    str(i),
                    pred['career'],
                    f"{pred['probability']}%",
                    strength_text
                ])
            
            # Create and style the table
            table = Table(prediction_data, colWidths=[0.6*inch, 2.2*inch, 0.8*inch, 2.4*inch])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0c4a6e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#cbd5e1'))
            ]))
            
            story.append(table)
        else:
            story.append(Paragraph("No career predictions available.", normal_style))
        
        story.append(Spacer(1, 20))
        
        # Personal Profile Analysis
        story.append(Paragraph("Personal Profile Analysis", heading_style))
        
        # Personality Insights
        personality_data = [
            ['Trait', 'Score', 'Interpretation'],
            ['Organization (C)', counseling_data.get('C_score', 'N/A'), get_interpretation('C_score', counseling_data.get('C_score'))],
            ['Openness (O)', counseling_data.get('O_score', 'N/A'), get_interpretation('O_score', counseling_data.get('O_score'))],
            ['Extraversion (E)', counseling_data.get('E_score', 'N/A'), get_interpretation('E_score', counseling_data.get('E_score'))],
            ['Agreeableness (A)', counseling_data.get('A_score', 'N/A'), get_interpretation('A_score', counseling_data.get('A_score'))],
            ['Neuroticism (N)', counseling_data.get('N_score', 'N/A'), get_interpretation('N_score', counseling_data.get('N_score'))]
        ]
        
        personality_table = Table(personality_data, colWidths=[1.5*inch, 0.7*inch, 3.8*inch])
        personality_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0369a1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f1f5f9')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#e2e8f0'))
        ]))
        
        story.append(personality_table)
        story.append(Spacer(1, 15))
        
        # Aptitude Scores
        story.append(Paragraph("Aptitude Assessment", ParagraphStyle('SubHeading', parent=heading_style, fontSize=14)))
        
        aptitude_data = [
            ['Aptitude', 'Score', 'Level'],
            ['Numerical Reasoning', counseling_data.get('Numerical_Aptitude', 'N/A'), get_level(counseling_data.get('Numerical_Aptitude'))],
            ['Verbal Ability', counseling_data.get('Verbal_Aptitude', 'N/A'), get_level(counseling_data.get('Verbal_Aptitude'))],
            ['Abstract Thinking', counseling_data.get('Abstract_Reasoning', 'N/A'), get_level(counseling_data.get('Abstract_Reasoning'))],
            ['Logical Reasoning', counseling_data.get('Logical_Reasoning', 'N/A'), get_level(counseling_data.get('Logical_Reasoning'))],
            ['Spatial Awareness', counseling_data.get('Spatial_Aptitude', 'N/A'), get_level(counseling_data.get('Spatial_Aptitude'))]
        ]
        
        aptitude_table = Table(aptitude_data, colWidths=[1.8*inch, 0.7*inch, 1.5*inch])
        aptitude_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f0f9ff')),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bae6fd'))
        ]))
        
        story.append(aptitude_table)
        story.append(Spacer(1, 20))
        
        # Work Style Preferences
        story.append(Paragraph("Work Style Preferences", heading_style))
        
        preference_text = f"""
        Your assessment indicates a strong preference for {get_work_style_preference(counseling_data)}. 
        You thrive in environments that emphasize {get_environment_preference(counseling_data)}.
        """
        story.append(Paragraph(preference_text, normal_style))
        
        # Next Steps
        story.append(Paragraph("Recommended Next Steps", heading_style))
        next_steps = """
        1. Research the top recommended career paths in depth
        2. Connect with professionals in these fields for informational interviews
        3. Identify relevant skills to develop or enhance
        4. Consider internship or shadowing opportunities
        5. Discuss these findings with a career counselor or mentor
        """
        story.append(Paragraph(next_steps, normal_style))
        
        # Footer
        story.append(Spacer(1, 30))
        footer_text = """
        <i>This report was generated by NovaX Career Intelligence AI System. 
        The recommendations are based on statistical analysis and should be considered 
        alongside personal interests, values, and market conditions.</i>
        """
        story.append(Paragraph(footer_text, ParagraphStyle('Footer', parent=styles['Italic'], fontSize=8, textColor=colors.gray)))
        
        # Build PDF
        doc.build(story)
        
        # Get PDF value and create response
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"novax_career_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        print(f"Error generating PDF: {e}")
        return JsonResponse({'error': 'Failed to generate report'}, status=500)

# Helper functions for the PDF generation
def get_interpretation(trait, score):
    """Get interpretation for personality traits"""
    if score is None:
        return "Not assessed"
    
    score = float(score)
    interpretations = {
        'C_score': {
            'low': "Flexible and adaptable approach",
            'medium': "Balanced organization skills", 
            'high': "Highly structured and systematic"
        },
        'O_score': {
            'low': "Prefer routine and consistency",
            'medium': "Open to new experiences",
            'high': "Highly innovative and curious"
        },
        'E_score': {
            'low': "Reflective and reserved",
            'medium': "Socially balanced",
            'high': "Outgoing and energetic"
        },
        'A_score': {
            'low': "Independent and direct",
            'medium': "Cooperative and considerate",
            'high': "Highly empathetic and supportive"
        },
        'N_score': {
            'low': "Emotionally resilient",
            'medium': "Generally stable",
            'high': "Sensitive and emotionally aware"
        }
    }
    
    if score <= 4:
        level = 'low'
    elif score <= 7:
        level = 'medium'
    else:
        level = 'high'
        
    return interpretations.get(trait, {}).get(level, "Average")

def get_level(score):
    """Get proficiency level for aptitudes"""
    if score is None:
        return "Not assessed"
    
    score = float(score)
    if score <= 3:
        return "Basic"
    elif score <= 6:
        return "Intermediate"
    elif score <= 8:
        return "Advanced"
    else:
        return "Expert"

def get_strengths_for_career(counseling_data):
    """Identify top strengths based on assessment scores"""
    strength_scores = []
    for field, score in counseling_data.items():
        if score is not None:
            strength_scores.append((field, float(score)))
    
    # Sort by score descending and return top strengths
    strength_scores.sort(key=lambda x: x[1], reverse=True)
    return [field for field, score in strength_scores[:5]]

def get_work_style_preference(counseling_data):
    """Determine work style preference"""
    teamwork = counseling_data.get('Enjoy_Teamwork', 5)
    creativity = counseling_data.get('Creative_Thinking', 5)
    detail = counseling_data.get('Attention_to_Detail', 5)
    
    if teamwork >= 8:
        return "collaborative team environments"
    elif creativity >= 8:
        return "innovative and creative work"
    elif detail >= 8:
        return "detailed and precise tasks"
    else:
        return "balanced and varied work"

def get_environment_preference(counseling_data):
    """Determine preferred work environment"""
    extraversion = counseling_data.get('E_score', 5)
    openness = counseling_data.get('O_score', 5)
    
    if extraversion >= 7 and openness >= 7:
        return "dynamic, social, and innovative settings"
    elif extraversion >= 7:
        return "social and interactive environments"
    elif openness >= 7:
        return "creative and changing circumstances"
    else:
        return "stable and predictable settings"
    
    
@csrf_exempt
@require_POST
def start_counseling(request):
    """Start a new counseling session"""
    try:
        initial_data = counselor.get_initial_greeting()
        
        # Initialize session
        request.session['counseling_data'] = {}
        request.session['conversation_history'] = []
        request.session['current_field'] = initial_data['field']
        request.session['conversation_step'] = initial_data['conversation_step']
        
        # Log first message
        request.session['conversation_history'].append({
            'type': 'bot',
            'message': initial_data['message']
        })
        request.session['conversation_history'].append({
            'type': 'bot',
            'message': initial_data['next_question']
        })
        
        return JsonResponse({
            'success': True,
            'message': initial_data['message'],
            'next_question': initial_data['next_question'],
            'field': initial_data['field'],
            'conversation_step': initial_data['conversation_step']
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
@csrf_exempt
@require_POST
def process_counseling_answer(request):
    """Process user's answer during counseling session"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        user_answer = data.get('answer')
        current_field = request.session.get('current_field')
        counseling_data = request.session.get('counseling_data', {})
        conversation_step = request.session.get('conversation_step', 'personality')
        
        # Log user message
        conversation_history = request.session.get('conversation_history', [])
        
        # Only log if it's not a simple edit command we're handling
        if not (user_answer.lower() in ['edit', 'change', 'back'] and conversation_step != 'editing'):
            conversation_history.append({
                'type': 'user',
                'message': user_answer
            })
        
        # Get next question from counselor
        counselor_response = counselor.process_answer(
            user_answer, current_field, conversation_step, counseling_data
        )
        
        # Update session data
        request.session['counseling_data'] = counseling_data
        request.session['current_field'] = counselor_response.get('field')
        request.session['conversation_step'] = counselor_response.get('conversation_step')
        
        # Log bot responses
        if counselor_response.get('message'):
            conversation_history.append({
                'type': 'bot', 
                'message': counselor_response['message']
            })
        if counselor_response.get('next_question'):
            conversation_history.append({
                'type': 'bot',
                'message': counselor_response['next_question']
            })
        
        request.session['conversation_history'] = conversation_history
        request.session.modified = True
        
        response_data = {
            'success': True,
            'message': counselor_response.get('message', ''),
            'next_question': counselor_response.get('next_question'),
            'field': counselor_response.get('field'),
            'conversation_step': counselor_response.get('conversation_step'),
            'completed': counselor_response.get('completed', False),
            'show_edit_option': counselor_response.get('show_edit_option', True),
            'collected_data': counseling_data
        }
        
        # Add edit options if in edit mode
        if counselor_response.get('edit_options'):
            response_data['edit_options'] = counselor_response['edit_options']
        
        # If counseling is completed, make prediction
        if counselor_response.get('completed'):
            predictions = generate_career_predictions(counseling_data)
            response_data['predictions'] = predictions
            
            # Save the session data
            save_counseling_session(request, counseling_data, predictions)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

def generate_career_predictions(counseling_data):
    """Generate career predictions from collected data"""
    if not ENSEMBLE_MODELS:
        return None
    
    try:
        features = [
            "O_score", "C_score", "E_score", "A_score", "N_score",
            "Numerical_Aptitude", "Verbal_Aptitude", "Abstract_Reasoning", 
            "Logical_Reasoning", "Spatial_Aptitude",
            "Enjoy_Teamwork", "Creative_Thinking", "Attention_to_Detail"
        ]
        
        # Ensure all features are present, use 5 as default for missing values
        input_data = [float(counseling_data.get(feat, 5)) for feat in features]
        
        # Scale and predict
        input_array = np.array(input_data).reshape(1, -1)
        scaled_input = SCALER.transform(input_array)
        
        # Ensemble prediction
        probas_list = [model.predict_proba(scaled_input) for model in ENSEMBLE_MODELS]
        avg_probas = np.mean(probas_list, axis=0)
        
        # Get top 3 predictions
        top3_indices = np.argsort(avg_probas[0])[::-1][:3]
        top3_careers = LABEL_ENCODER.inverse_transform(top3_indices)
        
        results = []
        for career, index in zip(top3_careers, top3_indices):
            probability = avg_probas[0][index]
            results.append({
                'career': career,
                'probability': round(probability * 100, 2)
            })
            
        return results
        
    except Exception as e:
        print(f"Prediction error: {e}")
        return None

def save_counseling_session(request, counseling_data, predictions):
    """Save counseling session to database"""
    try:
        from .models import CareerSurvey  # Your existing model
        
        CareerSurvey.objects.create(
            category='AI_Counseling',
            responses={
                'counseling_data': counseling_data,
                'predictions': predictions,
                'conversation_history': request.session.get('conversation_history', [])
            }
        )
    except Exception as e:
        print(f"Error saving counseling session: {e}")

@csrf_exempt
@require_POST
def get_conversation_history(request):
    """Get the current conversation history"""
    try:
        history = request.session.get('conversation_history', [])
        return JsonResponse({'history': history})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Add a new view for the counseling interface
def career_counseling(request):
    return render(request, 'career_counseling.html')

# =====================================================
# Get the directory of the current views.py file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Define the path to the directory containing the model files
MODEL_DIR = os.path.join(BASE_DIR, 'ml_models') # Assuming you created an ml_models folder
print(MODEL_DIR)
# Check if model files exist and load them globally for efficiency
# This loads the models only once when Django starts
try:
    with open(os.path.join(MODEL_DIR, "ensemble_models_optuna.pkl"), "rb") as f:
        ENSEMBLE_MODELS = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "label_encoder.pkl"), "rb") as f:
        LABEL_ENCODER = pickle.load(f)
    with open(os.path.join(MODEL_DIR, "scaler.pkl"), "rb") as f:
        SCALER = pickle.load(f)
    print("✅ Career Prediction Models loaded successfully!")
except Exception as e:
    # IMPORTANT: Handle the case where models aren't found or fail to load
    print(f"❌ Error loading ML models: {e}. Check if the files are in {MODEL_DIR}")
    ENSEMBLE_MODELS = None
    LABEL_ENCODER = None
    SCALER = None


@csrf_exempt
@require_POST
def predict_career(request):
    if not ENSEMBLE_MODELS:
        return JsonResponse({'error': 'Prediction models are not loaded.'}, status=503)

    try:
        data = json.loads(request.body.decode('utf-8'))
        
        # Define the expected feature keys based on your training script
        features = [
            "O_score", "C_score", "E_score", "A_score", "N_score",
            "Numerical_Aptitude", "Verbal_Aptitude", "Abstract_Reasoning",
            "Logical_Reasoning", "Spatial_Aptitude",
            "Enjoy_Teamwork", "Creative_Thinking", "Attention_to_Detail"
        ]
        
        # Extract features in the correct order
        input_data = [float(data.get(feat, 0)) for feat in features]
        
        # 1. Convert to numpy array and reshape for the scaler
        input_array = np.array(input_data).reshape(1, -1)
        
        # 2. Scale the input data
        scaled_input = SCALER.transform(input_array)
        
        # 3. Ensemble Prediction (Soft Voting)
        probas_list = [model.predict_proba(scaled_input) for model in ENSEMBLE_MODELS]
        avg_probas = np.mean(probas_list, axis=0)
        
        # 4. Get Top 3 Predictions
        # np.argsort returns indices that would sort the array
        top3_indices = np.argsort(avg_probas[0])[::-1][:3]
        top3_careers = LABEL_ENCODER.inverse_transform(top3_indices)
        
        # 5. Format results with probabilities
        results = []
        for career, index in zip(top3_careers, top3_indices):
            probability = avg_probas[0][index]
            results.append({
                'career': career,
                'probability': round(probability * 100, 2) # Percentage
            })
            
        return JsonResponse({'predictions': results}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON in request body.'}, status=400)
    except KeyError as e:
        return JsonResponse({'error': f'Missing expected data field: {e}'}, status=400)
    except Exception as e:
        return JsonResponse({'error': f'An unexpected error occurred: {str(e)}'}, status=400)

# ====================================================
# 🔹 Existing Views (Unchanged)
# ====================================================

@csrf_exempt
@require_POST
def save_survey(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        category = data.get('category')
        responses = data.get('responses')

        CareerSurvey.objects.create(category=category, responses=responses)
        return JsonResponse({'message': 'Survey saved successfully!'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Create your views here.
def home(request):
    return render(request, 'k_home.html')

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def quiz_hub(request):
    return render(request, 'quiz_hub.html')

def aptitude_test_Q(request):
    return render(request, 'aptitude_test.html')

def educational_test_Q(request):
    return render(request, 'educational_test.html')

def educational_major_selection(request):
    return render(request, 'educational_major_selection.html')

def educational_test_CSE_Q(request):
    return render(request, 'educational_test_CSE.html')

def educational_test_CSE_result(request):
    return render(request, 'educational_test_CSE_result.html')

def combined_test_Q(request):
    return render(request, 'combined_test.html')

def aptitude_test_R(request):
    return render(request, 'aptitude_result.html')

def architecture_path(request):
    return render(request, 'architecture_path.html')

def institution_detail(request):
    return render(request, 'institution_detail.html')

# def private_colleges(request):
#     return render(request, 'private_colleges.html')

# def public_universities(request):
#     return render(request, 'public_universities.html')

from django.shortcuts import render, get_object_or_404
from .models import PublicUniversity, PrivateCollege

def public_universities(request):
    universities = PublicUniversity.objects.all()
    return render(request, 'public_universities.html', {'universities': universities})

def public_university_detail(request, pk):
    university = get_object_or_404(PublicUniversity, pk=pk)
    return render(request, 'public_universities_details.html', {'university': university})

def private_colleges(request):
    colleges = PrivateCollege.objects.all()
    return render(request, 'private_colleges.html', {'colleges': colleges})

def private_college_detail(request, pk):
    college = get_object_or_404(PrivateCollege, pk=pk)
    return render(request, 'private_colleges_details.html', {'college': college})
