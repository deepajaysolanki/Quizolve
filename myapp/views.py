from django.shortcuts import render, redirect
from django.contrib import messages
from .models import AppUsers
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from . import ai_services # importing module
from django.contrib.auth.decorators import login_required
from .forms import UserProfileForm
import re, json
from django.utils import timezone   
from .models import ExamQuizAttempt, UserQuizAttempt, AnsweredQuestion
from django.contrib import messages
from django.views.decorators.http import require_POST
from datetime import timedelta
from django.conf import settings

def home_page(request):
    return render(request, 'pages/index.html')
def about_page(request):
    return render(request, 'pages/about.html')
def quiz_page(request):
    return render(request, 'pages/quiz.html')
def contact_page(request):
    return render(request, 'pages/contact.html')

def registration_form(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        dob = request.POST.get('date_of_birth') 
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        profile_photo = request.FILES.get('profile_photo')  

        field_errors = {}

        if not first_name:
            field_errors['first_name'] = "First Name is required."
        if not last_name:
            field_errors['last_name'] = "Last Name is required."
        if not dob:
            field_errors['date_of_birth'] = "Date of birth is required."
        if not email:
            field_errors['email'] = "Email is required."
        if not password:
            field_errors['password'] = "Password is required."
        if not confirm_password:
            field_errors['confirm_password'] = "Confirm password is required."

        # first name validation
        if first_name and not re.match(r'^[a-zA-Z]{1,25}$', first_name):
            field_errors['first_name'] = "Enter a valid First name."

        # last name validation
        if last_name and not re.match(r'^[a-zA-Z]{1,25}$', last_name):
            field_errors['last_name'] = "Enter a valid Last name."

         # Password validation
        if password and not re.match(r'^(?=.*\d)(?=.*[\W_]).{8,}$', password):
            field_errors['password'] = "Password must be at least 8 characters and include a special character."
        
        # Password confirmation check
        if password and confirm_password and password != confirm_password:
            field_errors['confirm_password'] = "Passwords confirmation do not match."

        # Email validation
        if email and not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            field_errors['email'] = "Invalid email format."

        # Field validation
        if not all([first_name, last_name, dob, email, password, confirm_password]):
            messages.error(request, "All fields are required.")
            return redirect('registration')
        
        # Check if email already exists in the database
        if email and AppUsers.objects.filter(email=email).exists():
            field_errors['email'] = "Email already exists."

        # Hash the password before creating the user object
        if password:
            hashed_password = make_password(password)            

        if field_errors:
            request.session['field_errors'] = field_errors  # store for template
            request.session['old_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'date_of_birth': dob,
                'password': hashed_password,
                'confirm_password': confirm_password
            }
            return redirect('registration')
         
        try:
            user = AppUsers(
                first_name=first_name,
                last_name=last_name,
                date_of_birth=dob,
                email=email,
                password=hashed_password,
            )

            if profile_photo:
                user.profile_photo = profile_photo

            user.save()

            messages.success(request, "User registered successfully!")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Something went wrong: {str(e)}")
            return redirect('registration')
       
      # GET request
    old_data = request.session.pop('old_data', {})
    field_errors = request.session.pop('field_errors', {})
   
    return render(request, 'user/register.html', {
        'old_data': old_data,
        'field_errors': field_errors
    })

def login_form(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '').strip()
            
        # Save entered data for reloading
        request.session['old_data'] = {'email': email}

        field_errors = {}
        if not email:
            field_errors['email'] = "Email is required."
        if not password:
            field_errors['password'] = "Password is required."

        if not field_errors:
            user = AppUsers.objects.filter(email=email, password=password).first()
            if user:
                # messages.success(request, "Login successful!")
                request.session.pop('old_data', None)
                request.session.pop('field_errors', None)
                login(request, user)  

                return redirect('home-page') 
            else:
                field_errors['password'] = "Invalid email or password."

        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home-page')
        

        request.session['field_errors'] = field_errors
        return redirect('login')  # URL name in urls.py

    else:
        # On GET or refresh, clean up session data
        old_data = request.session.pop('old_data', {})
        field_errors = request.session.pop('field_errors', {})

    return render(request, 'user/login.html', {
        'old_data': old_data,
        'field_errors': field_errors
    })

def logout_view(request):
    logout(request)
    return redirect('home-page')  

def profile_view(request):
    if request.user.is_authenticated:
        # If logged in, get the user object
        current_user = request.user

        # Add the user's data into variables
        first_name = current_user.first_name
        last_name = current_user.last_name
        email = current_user.email
        date_of_birth = current_user.date_of_birth
        profile_photo = current_user.profile_photo.url

        # Create a context dictionary with your variables
        context = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'date_of_birth': date_of_birth,
            'profile_photo': profile_photo  
        }
        
        # Render the profile page with the context data
        return render(request, 'pages/user-profile.html', context)
    else:
        return redirect('login')
    
def profile_edit_view(request):
    if request.user.is_authenticated:
        # The form is instantiated with the current user's data
        form = UserProfileForm(instance=request.user)

        if request.method == 'POST':
            # If the form is submitted, populate it with the POST data and files
            form = UserProfileForm(request.POST, request.FILES, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile has been updated successfully!')
                return redirect('user-profile') # Redirect back to the profile page

        context = {
            'form': form
        }
        return render(request, 'user/profile_edit.html', context)
    else:
        return redirect('login')
    
def start_quiz_view(request):
    if request.user.is_authenticated:
        print(f"--- POST data received in start_quiz_view: {request.POST} ---")
        now = timezone.now()
        twenty_four_hours_ago = now - timedelta(hours=24)
        quiz_type = None
        topic = None
        difficulty = None

        # Case 1: Starting a new quiz from a form
        if request.method == 'POST':
            print(f"--- POST data received: {request.POST} ---")
            quiz_type = request.POST.get('quiz_type')
            topic = request.POST.get('topic')
            difficulty = request.POST.get('difficulty', 'medium')
        
        # Case 2: Clicking "Play Again" from the results page
        elif request.method == 'GET':
            print("--- GET request received (Play Again) ---")
            # Get the previous quiz settings from the session
            topic = request.session.get('topic')
            difficulty = request.session.get('difficulty')
            
            # Determine the quiz_type from the saved session data
            if difficulty == 'exam':
               return redirect('exam-selection')
            
            if topic in ['General Knowledge', 'Science', 'History', 'Geography', 'Math', 'Literature']:
                quiz_type = 'category'
            else:   
                quiz_type = 'custom'
        # If there is no topic, we can't start a quiz
        if not topic:
            return redirect('quiz-page')
        
        if quiz_type == 'category':
            # Per-category limit check
            attempt_count = UserQuizAttempt.objects.filter(
                user=request.user, 
                quiz_type='category', 
                quiz_identifier=topic,
                created_at__gte=twenty_four_hours_ago
            ).count()
            if attempt_count >= 3:
                messages.error(request, f"You have reached your daily limit of 3 quizzes for the '{topic}' category.")
                return redirect('quiz-page')
            
        elif quiz_type == 'custom':
            # Global limit check for all custom topic quizzes
            attempt_count = UserQuizAttempt.objects.filter(
                user=request.user, 
                quiz_type='custom',
                created_at__gte=twenty_four_hours_ago
            ).count()
            if attempt_count >= 3:
                messages.error(request, "You have reached your daily limit of 3 custom topic quizzes.")
                return redirect('quiz-page')
            
        # If allowed, create a new attempt record
            # UserQuizAttempt.objects.create(user=request.user, quiz_type=quiz_type, quiz_identifier=topic)
        
        attempt = UserQuizAttempt.objects.create(
            user=request.user,
            quiz_type=request.POST.get('quiz_type'),
            quiz_identifier=request.POST.get('topic'),
            total_questions=50
        )
        # UserQuizAttempt.objects.create(user=request.user)

        # setup the session variables
        request.session['current_attempt_id'] = attempt.id
        request.session['topic'] = topic
        request.session['difficulty'] = difficulty
        request.session['total_questions'] = 50
        request.session['correct_answers'] = 0
        request.session['total_played'] = 0
        request.session['question_batch'] = [] # Important: Clear any leftover questions
        request.session['quiz_review_data'] = [] 
        request.session['asked_questions'] = []
        
        request.session.save()
        return redirect('play-quiz')
    else:
        return redirect('login')

def play_quiz_view(request):
    if request.user.is_authenticated:
        difficulty = request.session.get('difficulty', 'medium')
        topic = request.session.get('topic', 'General Quiz')
        total_questions = request.session.get('total_questions', 0)

        # --- THIS IS THE FIX ---
        # Set time limit based on quiz type
        if difficulty == 'exam':
            time_limit = 59  # Set to 59 for all exam quizzes
        else:
            # You can keep varied times for regular quizzes
            if difficulty == 'easy':
                time_limit = 30
            elif difficulty == 'hard':
                time_limit = 15
            else: # medium
                time_limit = 20
        # --- END OF FIX ---
        
        # Get the number of questions the user has already played in this quiz
        total_played = request.session.get('total_played', 0)
        
        context = {
            'time_limit': time_limit,
            'quizTopic': topic,
            'total_questions': total_questions,
            'current_attempt_id': request.session.get('current_attempt_id'),
            'total_played': total_played,
        }
        
        return render(request, 'AI_features/play_quiz.html', context)
    else:
        return redirect('login')
    
def results_view(request):
    """Displays the final results from the session."""

    attempt = None
    attempt_id = request.session.get('current_attempt_id')  

    if attempt_id:
        try:
            attempt = UserQuizAttempt.objects.get(id=attempt_id, user=request.user)
        except UserQuizAttempt.DoesNotExist:
            attempt = None
        
    # User refreshed the page or is visiting directly.
    if not attempt:
        # find their most recent quiz attempt from the database.
        attempt = UserQuizAttempt.objects.filter(user=request.user).order_by('-created_at').first()

    # User has never played a quiz. Redirect them.
    if not attempt:
        return redirect('home-page')
    
    # # Get the type of quiz that was just played from the session
    # quiz_type = request.session.get('difficulty', 'regular')
        
    # Get all the saved answers for that quiz
    review_data = attempt.answers.all().order_by('id')
        
    # Get all stats directly from the database record
    total_played = review_data.count()
    correct_answers = attempt.score
    display_total = attempt.total_questions
    quiz_type = attempt.quiz_type
        
    #  Check if the quiz was ended early (this flag is still useful)
    ended_early = request.session.pop('ended_early', False)

    # Calculate percentage
    percentage = 0
    if display_total > 0:
        percentage = round((correct_answers / display_total) * 100)

    # Clean up the session so the next quiz is fresh
    request.session.pop('current_attempt_id', None)
    request.session.pop('topic', None)
    request.session.pop('difficulty', None)
    request.session.pop('total_questions', None)
    request.session.pop('asked_questions', None)

    context = {
        'total_played': total_played,
        'correct': correct_answers,
        'incorrect': total_played - correct_answers,
        'display_total': display_total,
        'ended_early': ended_early,
        'quiz_type': quiz_type,
        'percentage': percentage,
        'review_data': review_data,
    }
    return render(request, 'AI_features/result.html', context)    

# --- API Views (Called by JavaScript) ---

# myapp/views.py

def get_next_question_api(request):
    # This block runs only when the current batch of questions is empty
    if not request.session.get('question_batch'):
        topic = request.session.get('topic')
        difficulty = request.session.get('difficulty')
        asked_questions = request.session.get('asked_questions', [])
        
        if not topic:
            return JsonResponse({'error': 'Quiz not started or session expired.'}, status=400)
        
        # --- NEW LOGIC: Choose the correct AI function ---
        new_batch = []
        if settings.DEBUG:
            # If we are in development, use the fast, free mock data
            new_batch = ai_services.get_mock_questions(topic, difficulty)
        else:
            if difficulty == 'exam':
                EXAM_FULL_NAMES = {
                    'UPSC': 'UPSC Civil Services Examination',
                    'JEE': 'JEE (Joint Entrance Examination) for engineering',
                    'NEET': 'NEET (National Eligibility cum Entrance Test) for medical students',
                    'CAT': 'CAT (Common Admission Test) for MBA admissions in India',
                    'SSC CGL': 'SSC CGL (Combined Graduate Level) Examination',
                    'GATE': 'GATE (Graduate Aptitude Test in Engineering)',
                }
                full_exam_name_for_ai = EXAM_FULL_NAMES.get(topic, topic)
                # For exams, use the specialized function to get a batch
                new_batch = ai_services.generate_exam_question_batch(full_exam_name_for_ai, exclude_questions=asked_questions)
            else:
                # For regular quizzes, use the general function
                new_batch = ai_services.generate_question_batch(topic, difficulty, exclude_questions=asked_questions)
            # --- END OF NEW LOGIC ---

        if not new_batch:
            return JsonResponse({'error': 'Failed to generate new questions from the AI.'}, status=500)

        # Update memory and save the new batch to the session
        new_question_texts = [q['question'] for q in new_batch]
        asked_questions.extend(new_question_texts)
        request.session['asked_questions'] = asked_questions
        request.session['question_batch'] = new_batch

    # This part runs every time to serve one question from the batch
    question_batch = request.session.get('question_batch', [])
    
    if not question_batch:
         return JsonResponse({'error': 'Ran out of questions.'}, status=500)

    next_question = question_batch.pop(0)
    request.session['question_batch'] = question_batch
    
    return JsonResponse(next_question)

def check_answer_api(request):
    """API endpoint to check if the user's answer was correct and update score."""
    if request.method == 'POST':
        data = json.loads(request.body)
        is_correct = data.get('is_correct')

        # Update session stats
        request.session['total_played'] = request.session.get('total_played', 0) + 1
        if is_correct:
            request.session['correct_answers'] = request.session.get('correct_answers', 0) + 1
            
        return JsonResponse({'status': 'success', 'stats': {
            'total_played': request.session['total_played'],
            'correct_answers': request.session['correct_answers']
        }})
    return JsonResponse({'error': 'Invalid request'}, status=400)

# views for Exam Quiz Feature
def exam_selection_view(request):
    return render(request, 'AI_features/exam_selection.html')

def start_exam_quiz_view(request, exam_name):
    now = timezone.now()
    twenty_four_hours_ago = now - timedelta(days=1)

     # Per-exam limit check
    attempt_count = UserQuizAttempt.objects.filter(
        user=request.user, 
        quiz_type='exam', 
        quiz_identifier=exam_name,
        created_at__gte=twenty_four_hours_ago
    ).count()

    # CHANGE THIS LINE from >= 1 to >= 3
    if attempt_count >= 3:
        messages.error(request, f"You have reached your daily limit of 3 quizzes for the {exam_name} exam.")
        return redirect('exam-selection')
    
    # If allowed, create a new attempt record
    attemp = UserQuizAttempt.objects.create(user=request.user, quiz_type='exam', quiz_identifier=exam_name)

    # Set up the session rules for the exam quiz
    request.session['question_batch'] = [] # Start with an empty batch
    request.session['topic'] = exam_name
    request.session['difficulty'] = 'exam' # Set the difficulty to 'exam'
    request.session['total_questions'] = 50 
    request.session['correct_answers'] = 0
    request.session['total_played'] = 0
    request.session['asked_questions'] = []
    request.session['quiz_review_data'] = []

    request.session.save()
    return redirect('play-exam-quiz')

@require_POST
def end_exam_quiz_early_api(request):
    # Create an attempt record to lock the user out for the day
    ExamQuizAttempt.objects.create(
        user=request.user,
        exam_name=request.session.get('topic'),
        date_played=timezone.now().date()
    )
    # ADD THIS LINE: Set a flag in the session
    request.session['ended_early'] = True
    
    return JsonResponse({'status': 'success'})

# API to record individual question answers in the database
@require_POST
def record_answer_api(request):
    try:
        data = json.loads(request.body)
        attempt_id = request.session.get('current_attempt_id')
        
        if not attempt_id:
            return JsonResponse({'status': 'error', 'message': 'No attempt ID in session.'}, status=400)
        
        attempt = UserQuizAttempt.objects.get(id=attempt_id)
        is_correct = (data.get('user_answer') == data.get('correct_answer'))

        # Save the question and answer to the database
        AnsweredQuestion.objects.create(
            attempt=attempt,
            question_text=data.get('question'),
            user_answer=data.get('user_answer'),
            correct_answer=data.get('correct_answer'),
            is_correct=is_correct
        )

        # Update the score on the main attempt object
        if is_correct:
            attempt.score = attempt.score + 1
            attempt.save()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    
def quiz_history_view(request):
    if request.user.is_authenticated:
       # Get all attempts for the current user
        attempts = UserQuizAttempt.objects.filter(user=request.user).order_by('-created_at')

        # Create a new list to hold the attempts with their percentages
        attempts_with_percentage = []
        for attempt in attempts:
                percentage = 0
                if attempt.total_questions > 0:
                    percentage = round((attempt.score / attempt.total_questions) * 100)
                
                # Add the calculated percentage to the attempt object (or a new dict)
                attempts_with_percentage.append({
                    'attempt': attempt,
                    'percentage': percentage
                })

        context = {
                'attempts_with_percentage': attempts_with_percentage
            }
        return render(request, 'user/quiz_history.html', context)    
    else:
        return redirect('login')

@require_POST
def record_attempt_on_leave_api(request):
    if request.user.is_authenticated:
        # Only record an attempt if it's an exam quiz in progress
        if request.session.get('difficulty') == 'exam':
            # Use get_or_create to avoid duplicate entries
            UserQuizAttempt.objects.get_or_create(
                user=request.user,
                quiz_type='exam',
                quiz_identifier=request.session.get('topic'),
                created_at__date=timezone.now().date()
            )
        return JsonResponse({'status': 'ok'})
    else:
        return redirect('login')