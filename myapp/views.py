from django.shortcuts import render, redirect
from django.contrib import messages
from .models import AppUsers, PaymentRequest, ContactMessage, AnsweredQuestion, UserQuizAttempt
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from . import ai_services 
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import UserProfileForm
import re, json, random
from django.utils import timezone
from django.utils.dateparse import parse_datetime   
from django.utils.safestring import mark_safe
from .models import UserQuizAttempt, AnsweredQuestion, AppUsers
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.contrib import messages
from django.views.decorators.http import require_POST
from datetime import timedelta, datetime, date
from django.conf import settings
from django.core.cache import cache
from .utils import generate_otp, send_otp_email
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

def home_page(request):
    return render(request, 'pages/index.html')
def about_page(request):
    return render(request, 'pages/about.html')
def quiz_page(request):
    return render(request, 'pages/quiz.html')
def contact_page(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            # 1. Get data from the form (using the 'name' attributes from your HTML)
            name_input = request.POST.get('name') 
            email_input = request.POST.get('email')
            message_input = request.POST.get('message')
            
            # 2. Save to Database
            if name_input and email_input and message_input:
                ContactMessage.objects.create(
                    full_name=name_input,
                    email=email_input,
                    message=message_input
                )
                # 3. Trigger Success Toast
                messages.success(request, "Message sent successfully! We will contact you soon.")
                return redirect('contact-page')
            else:
                messages.error(request, "Please fill in all fields.")
    else:
        messages.error(request, "You must be logged in to send a message.")

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
        return redirect('login') 

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
        return render(request, 'user/user-profile.html', context)
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
        now = timezone.now()
        twenty_four_hours_ago = now - timedelta(hours=24)
        quiz_type = None
        topic = None
        difficulty = None
        DAILY_LIMIT = 3 # Default for free users

        # Check if user is premium AND subscription hasn't expired
        if request.user.is_premium:
            if request.user.subscription_expiry and request.user.subscription_expiry >= date.today():
                 DAILY_LIMIT = 12
            else:
                # Subscription expired, revert to free
                DAILY_LIMIT = 3

        # Starting a new quiz from a form
        if request.method == 'POST':
            print(f"--- POST data received: {request.POST} ---")
            quiz_type = request.POST.get('quiz_type')
            topic = request.POST.get('topic')
            difficulty = request.POST.get('difficulty', 'medium')
        
        # Clicking "Play Again" from the results page
        elif request.method == 'GET':
            print("--- GET request received (Play Again) ---")
            # Get the previous quiz settings from the session
            topic = request.session.get('topic')
            difficulty = request.session.get('difficulty')
            
            # Determine the quiz_type from the saved session data
            if difficulty == 'exam':
               return redirect('start-exam-quiz', exam_name=topic)
            
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
            if attempt_count >= DAILY_LIMIT:
                if not request.user.is_premium:
                    msg = f"You've hit your limit of {DAILY_LIMIT} free quizzes today for the '{topic}'. <a href='/checkout/' style='color: inherit; font-weight: bold; text-decoration: underline;'>Upgrade to Premium</a> to unlock more quizzes!"
                    messages.error(request, mark_safe(msg))
                else:
                    messages.error(request, f"You have reached your daily limit of {DAILY_LIMIT} quizzes for the '{topic}' category.")
                return redirect('quiz-page')
            
        elif quiz_type == 'custom':
            # Global limit check for all custom topic quizzes
            attempt_count = UserQuizAttempt.objects.filter(
                user=request.user, 
                quiz_type='custom',
                created_at__gte=twenty_four_hours_ago
            ).count()
            if attempt_count >= DAILY_LIMIT:
                if not request.user.is_premium:
                    msg = f"You've hit your limit of {DAILY_LIMIT} free quizzes today for the '{topic}'. <a href='/checkout/' style='color: inherit; font-weight: bold; text-decoration: underline;'>Upgrade to Premium</a> to unlock more quizzes!"
                    messages.error(request, mark_safe(msg))
                else:
                    messages.error(request, f"You have reached your daily limit of {DAILY_LIMIT} quizzes for the '{topic}' category.")
                return redirect('quiz-page')
            
        # If allowed, create a new attempt record
            # UserQuizAttempt.objects.create(user=request.user, quiz_type=quiz_type, quiz_identifier=topic)
        
        attempt = UserQuizAttempt.objects.create(
            user = request.user,
            quiz_type = quiz_type,
            quiz_identifier = topic,
            total_questions = 0
        )
        # UserQuizAttempt.objects.create(user=request.user)

        # setup the session variables
        request.session['current_attempt_id'] = attempt.id
        request.session['topic'] = topic
        request.session['difficulty'] = difficulty
        request.session['total_questions'] = 50
        request.session['correct_answers'] = 0
        request.session['total_played'] = 0
        request.session['question_batch'] = [] 
        request.session['quiz_review_data'] = [] 
        request.session['asked_questions'] = []
        request.session['quiz_start_time'] = str(datetime.now())
        request.session.save()

        return redirect('play-quiz')
    else:
        return redirect('login')

def play_quiz_view(request):
    if request.user.is_authenticated:
        # Get the current quiz attempt ID from the session
        attempt_id = request.session.get('current_attempt_id')
        total_played = AnsweredQuestion.objects.filter(attempt__id=attempt_id).count()
        total_questions = request.session.get('total_questions', 10)

        if attempt_id:
            try:
                # Count how many questions have already been answered for this attempt
                total_played = AnsweredQuestion.objects.filter(attempt__id=attempt_id).count()
            except AnsweredQuestion.DoesNotExist:
                total_played = 0

        if total_played >= total_questions:
            # Quiz is over, go to results
            return redirect('result-page')
        
        difficulty = request.session.get('difficulty', 'medium')
        topic = request.session.get('topic', 'General Quiz')
        saved_question = request.session.get('current_question_data')
        current_question = None

        # Case A: REFRESH DETECTED
        # If we have a saved question AND its index matches where we are (total_played),
        # just reload it. Do not generate a new one.
        if saved_question and saved_question.get('index') == total_played:
            print(f"--- Reloading Question #{total_played + 1} from Session (Refresh) ---")
            current_question = saved_question['data']
        
        # Case B: NEW QUESTION NEEDED
        else:
            print(f"--- Generating New Question #{total_played + 1} ---")
            
            # ==================================================
            # PUT YOUR AI / QUESTION GENERATION LOGIC HERE
            # ==================================================
            # For now, I am putting a placeholder. Replace this with your actual AI call.
            current_question = {
                'text': f"Question {total_played + 1}: What is the capital of France?",
                'options': ['Paris', 'London', 'Berlin', 'Madrid'],
                'correct': 'Paris'
            }
            # ==================================================

            # Save this specific question to the session so it survives a refresh
            request.session['current_question_data'] = {
                'index': total_played,
                'data': current_question
            }
            request.session.modified = True

        # Set time limit based on quiz type
        if difficulty == 'exam':
            time_limit = 59  # Set to 59 for all exam quizzes
        else:
            if difficulty == 'easy':
                time_limit = 30
            elif difficulty == 'hard':
                time_limit = 15
            else: # medium
                time_limit = 20
        
        # # Get the number of questions the user has already played in this quiz
        # total_played = request.session.get('total_played', 0)
        # print("Total played from play_quiz view:", total_played)

        context = {
            'question': current_question,  
            'question_number': total_played + 1,
            'total_questions': total_questions,
            'time_limit': time_limit,
            'quizTopic': topic,
            'current_attempt_id': attempt_id,
            'total_played': total_played,
        }
        
        return render(request, 'AI_features/play_quiz.html', context)
    else:
        return redirect('login')

# Final Results View
def results_view(request):
    """Displays the final results from the session."""

    attempt_id = request.session.get('current_attempt_id')  
    attempt = None

    if attempt_id:
        try:
            attempt = UserQuizAttempt.objects.get(id=attempt_id, user=request.user)
        except UserQuizAttempt.DoesNotExist:
            attempt = None
        
    # User has never played a quiz or session expired.
    if not attempt:
        # Fallback to the latest attempt
        attempt = UserQuizAttempt.objects.filter(user=request.user).order_by('-created_at').first()
        
    if not attempt:
        return redirect('home-page')
    
    # Get Saved Answers & Score
    review_data = attempt.answers.all().order_by('id')
    correct_answers = attempt.score  
    
    # Get the Real Count 
    real_question_count = review_data.count()

    #  If DB has a score but 0 questions, force the count to match the score.
    if real_question_count < correct_answers:
        real_question_count = correct_answers

    # calculate incorrect 
    incorrect_answers = real_question_count - correct_answers

    #  Update the Database with the REAL count
    if attempt.total_questions != real_question_count:
        attempt.total_questions = real_question_count
        attempt.save()

    # Calculate Percentage & Skipped Logic
    # We use the session variable for the "Denominator" (Max Questions).
    session_total = request.session.get('total_questions', 0)
    
    # If it's an exam, strictly enforce 50.
    quiz_max_questions = 50 if attempt.quiz_type == 'exam' else session_total

    # Calculate Percentage
    denominator = real_question_count if real_question_count > 0 else 1
    percentage = round((correct_answers / denominator) * 100)
    # percentage = 0
    # if quiz_max_questions > 0:
    #     percentage = round((correct_answers / quiz_max_questions) * 100)

    # Calculate skipped
    skipped_questions = quiz_max_questions - real_question_count
    if skipped_questions < 0: skipped_questions = 0

    # Calculate Time Taken
    start_time_str = request.session.get('quiz_start_time')
    time_taken_display = "00:00"

    if start_time_str:
        try:
            start_time = parse_datetime(start_time_str)
            end_time = datetime.now()
            duration = end_time - start_time
            total_seconds = int(duration.total_seconds())  
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            time_taken_display = f"{minutes:02d}m {seconds:02d}s"
        except:
            time_taken_display = "N/A"
            
    # Check if ended early flag exists
    ended_early = request.session.pop('ended_early', False)

    # Clean up Session
    request.session.pop('current_attempt_id', None)
    # request.session.pop('topic', None)
    # request.session.pop('difficulty', None)
    request.session.pop('total_questions', None)
    request.session.pop('asked_questions', None)
    request.session.pop('quiz_start_time', None)

    context = {
        'total_played': real_question_count,  # Used for "Attempted" count
        'display_total': quiz_max_questions,  # Used for "Out of X" (e.g. 50)
        'correct': correct_answers,
        'incorrect': incorrect_answers,
        'skipped': skipped_questions,
        'ended_early': ended_early,
        'quiz_type': attempt.quiz_type,
        'percentage': percentage,
        'review_data': review_data,
        'score': correct_answers,
        'quiz_topic': attempt.quiz_identifier or request.session.get('topic', 'General Knowledge'),      
        'time_taken': time_taken_display,
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
        
        # --- Choose the correct AI function ---
        new_batch = []
        # if settings.DEBUG:
        #     # If we are in development, use the fast, free mock data
        #     new_batch = ai_services.get_mock_questions(topic, difficulty)
        # else:
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
    if request.user.is_authenticated:
        now = timezone.now()
        twenty_four_hours_ago = now - timedelta(days=1)
        DAILY_LIMIT = 3

        # Check if user is premium AND subscription hasn't expired
        if request.user.is_premium:
            if request.user.subscription_expiry and request.user.subscription_expiry >= date.today():
                DAILY_LIMIT = 12  # ✅ Premium Limit
            else:
                DAILY_LIMIT = 3

        # Per-exam limit check
        attempt_count = UserQuizAttempt.objects.filter(
            user=request.user, 
            quiz_type='exam', 
            quiz_identifier=exam_name,
            created_at__gte=twenty_four_hours_ago
        ).count()

        # CHANGE THIS LINE from >= 1 to >= 3
        if attempt_count >= DAILY_LIMIT:
            if not request.user.is_premium:
                msg = f"You've hit your limit of {DAILY_LIMIT} free quizzes today for the '{exam_name}'. <a href='/checkout/' style='color: inherit; font-weight: bold; text-decoration: underline;'>Upgrade to Premium</a> to unlock more quizzes!"
                messages.error(request, mark_safe(msg))
            else:
                messages.error(request, f"You have reached your daily limit of {DAILY_LIMIT} quizzes for the '{exam_name}' category.")
            return redirect('exam-selection')
        
        # If allowed, create a new attempt record
        attemp = UserQuizAttempt.objects.create(user=request.user, quiz_type='exam', quiz_identifier=exam_name, total_questions=50)

        # Set up the session rules for the exam quiz
        request.session['current_attempt_id'] = attemp.id
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
    else:
        return redirect('login')    

@login_required
@require_POST
def set_ended_early_view(request):
    request.session['ended_early'] = True
    request.session.save()
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
    
# OTP Email Functionalities
# --- 1. CUSTOM LOGIN WITH OTP ---
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Check credentials but DO NOT login yet
        user = authenticate(request, email=email, password=password)
        
        if user is not None:
            if not user.is_active:
                messages.error(request, "This account is inactive.")
                return redirect('login')

            # Generate and Send OTP
            otp = generate_otp()
            send_otp_email(user.email, otp)
            
            # Save the user ID and OTP in the cache for 5 minutes (300 seconds)
            # We use the key 'otp_login_{user_id}' to make it unique
            cache.set(f'otp_login_{user.id}', otp, 300)
            
            # Save user ID in session temporarily to know who we are verifying
            request.session['auth_user_id'] = user.id
            
            messages.success(request, f"OTP sent to {user.email}")
            return redirect('verify-login-otp')
        else:
            messages.error(request, "Invalid email or password.")
            
    return render(request, 'user/login.html')

def verify_login_otp_view(request):
    user_id = request.session.get('auth_user_id')
    if not user_id:
        return redirect('login')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        cached_otp = cache.get(f'otp_login_{user_id}')
        
        if cached_otp and str(entered_otp) == str(cached_otp):
            # OTP Matches! Now we actually log the user in.
            user = AppUsers.objects.get(id=user_id)
            auth_login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            # Cleanup
            del request.session['auth_user_id']
            cache.delete(f'otp_login_{user_id}')
            
            return redirect('home-page')
        else:
            messages.error(request, "Invalid or expired OTP.")

    return render(request, 'user/ForgetPassword/verify_otp.html', {'action': 'Login'})


# --- 2. FORGOT PASSWORD WITH OTP ---
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        try:
            user = AppUsers.objects.get(email=email)
            
            # Generate and Send OTP
            otp = generate_otp()
            send_otp_email(user.email, otp)
            
            # Store in cache
            cache.set(f'otp_reset_{user.id}', otp, 300)
            request.session['reset_user_id'] = user.id
            
            messages.success(request, "OTP sent to your email.")
            return redirect('verify-reset-otp')
            
        except AppUsers.DoesNotExist:
            # For security, don't reveal if the email doesn't exist
            messages.error(request, "If an account exists with this email, an OTP has been sent.")
            
    return render(request, 'user/forgot_password.html')

def verify_reset_otp_view(request):
    user_id = request.session.get('reset_user_id')
    if not user_id:
        return redirect('forgot-password')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        cached_otp = cache.get(f'otp_reset_{user_id}')
        
        if cached_otp and str(entered_otp) == str(cached_otp):
            # OTP Verified. Allow them to reset password.
            # We set a flag in session to verify they passed this step
            request.session['reset_verified'] = True
            return redirect('reset-new-password')
        else:
            messages.error(request, "Invalid or expired OTP.")
            
    return render(request, 'user/ForgetPassword/verify_otp.html', {'action': 'Reset Password'})

def reset_new_password_view(request):
    user_id = request.session.get('reset_user_id')
    is_verified = request.session.get('reset_verified')
    
    if not user_id or not is_verified:
        return redirect('login')

    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password == confirm_password:
            user = AppUsers.objects.get(id=user_id)
            user.set_password(password)
            user.save()
            
            # Cleanup
            del request.session['reset_user_id']
            del request.session['reset_verified']
            cache.delete(f'otp_reset_{user_id}')
            
            messages.success(request, "Password reset successfully! Please login.")
            return redirect('login')
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, 'user/reset_new_password.html')

# ------ Subscription Plans View ------
# 1. The Pricing Page (Purple Cards)
def subscription_plans(request):
    return render(request, 'pages/checkout.html')


# 2. The Checkout Page (Simulated Payment Gateway)
@login_required
def checkout_view(request):
    # If already premium, show status page instead of payment page
    if request.user.is_premium and request.user.subscription_expiry:
        if request.user.subscription_expiry >= date.today():
            return render(request, 'pages/subscription-status.html')
        
    my_upi_id = "your-upi-id@okicici"
    
    if request.method == 'POST':
        # Get data from the form
        plan_type = request.POST.get('plan_type') # Now coming from the form
        user_upi = request.POST.get('upi_id')
        txn_id = request.POST.get('transaction_id')
        name = request.POST.get('name')

        # Determine amount based on plan (Security check)
        if plan_type == 'yearly':
            amount = "1299"
        else:
            plan_type = 'monthly' # Fallback
            amount = "149"
            
        
        # Save request to DB
        PaymentRequest.objects.create(
            user=request.user,
            plan_type=plan_type,
            amount=amount,
            transaction_id=txn_id
        )
        
        messages.success(request, "Payment submitted! We will verify and upgrade your account shortly.")
        return redirect('quiz-page')

    context = {
        'my_upi_id': my_upi_id
    }
    return render(request, 'pages/checkout.html', context)

# Forgot password view with OTP verification
def forgot_password_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Check if user exists
        try:
            user = AppUsers.objects.get(email=email)
        except AppUsers.DoesNotExist:
            # As requested: Explicitly tell them user is not found
            messages.error(request, "User with this email not found.")
            return redirect('forgot-password')

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Save OTP and Email in Session (Temporary)
        request.session['reset_email'] = email
        request.session['reset_otp'] = otp
        
        # Send Email
        subject = "Reset Your Password"
        message = f"Hi {user.first_name},\n\nYour OTP for password reset is: {otp}\n\nValid for this session only."
        from_email = settings.DEFAULT_FROM_EMAIL
        
        try:
            send_mail(subject, message, from_email, [email], fail_silently=False)
            messages.success(request, f"OTP sent successfully to {email}")
            return redirect('verify-reset-otp')
        except Exception as e:
            messages.error(request, "Error sending email. Please try again later.")
            
    return render(request, 'user/ForgetPassword/forgot_password.html')


# --- 2. VERIFY OTP PAGE ---
def verify_reset_otp_view(request):
    # Security: If no email in session, they skipped step 1
    if 'reset_email' not in request.session:
        messages.error(request, "Session expired. Please start again.")
        return redirect('forgot-password')

    if request.method == 'POST':
        entered_otp = request.POST.get('otp')
        stored_otp = request.session.get('reset_otp')
        
        if entered_otp == stored_otp:
            # Mark verified so they can access the next page
            request.session['reset_verified'] = True
            messages.success(request, "OTP Verified! Please set your new password.")
            return redirect('reset-new-password')
        else:
            messages.error(request, "Invalid OTP. Please try again.")

    return render(request, 'user/ForgetPassword/verify_otp.html')


# --- 3. SET NEW PASSWORD PAGE ---
def reset_new_password_view(request):
    # Security: Ensure they verified OTP before accessing this page
    if not request.session.get('reset_verified'):
        return redirect('user/ForgetPassword/forgot-password')
    
    email = request.session.get('reset_email')
    
    if request.method == 'POST':
        new_pass = request.POST.get('new_password')
        confirm_pass = request.POST.get('confirm_password')
        
        if new_pass == confirm_pass:
            try:
                user = AppUsers.objects.get(email=email)
                user.set_password(new_pass)
                user.save()
                
                # Cleanup: Remove session data
                del request.session['reset_email']
                del request.session['reset_otp']
                del request.session['reset_verified']
                
                messages.success(request, "Password reset successful! You can now login.")
                return redirect('login')
                
            except AppUsers.DoesNotExist:
                messages.error(request, "An error occurred. User not found.")
        else:
            messages.error(request, "Passwords do not match.")

    return render(request, 'user/ForgetPassword/reset_new_password.html')

# Only allow superusers (admins) to see this page
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard_view(request):
    # --- 1. QUICK STATS CARDS ---
    total_users = AppUsers.objects.count()
    total_quizzes_taken = UserQuizAttempt.objects.count()
    total_premium = AppUsers.objects.filter(is_premium=True).count()
    
    # --- 2. CHART DATA: Quiz Attempts Last 30 Days (Line Chart) ---
    last_30_days = timezone.now() - timedelta(days=30)
    
    # Group by date and count
    attempts_data = UserQuizAttempt.objects.filter(created_at__gte=last_30_days)\
        .annotate(date=TruncDate('created_at'))\
        .values('date')\
        .annotate(count=Count('id'))\
        .order_by('date')
        
    # --- FIX: SAFE LOOP TO PREVENT CRASH ---
    quiz_dates = []
    quiz_counts = []
    
    for item in attempts_data:
        # Only add data if the date is valid (not None)
        if item['date']:
            quiz_dates.append(item['date'].strftime("%Y-%m-%d"))
            quiz_counts.append(item['count'])

    # --- 3. CHART DATA: Premium vs Free (Doughnut Chart) ---
    free_users = total_users - total_premium
    
    # --- 4. CHART DATA: Top 5 Popular Topics (Bar Chart) ---
    popular_topics = UserQuizAttempt.objects.values('quiz_identifier')\
        .annotate(total=Count('id'))\
        .order_by('-total')[:5]
        
    # List comprehensions are safe here because strings/integers don't have .strftime()
    topic_labels = [item['quiz_identifier'] for item in popular_topics]
    topic_counts = [item['total'] for item in popular_topics]

    # --- 5. CONTEXT ---
    context = {
        'total_users': total_users,
        'total_premium': total_premium,
        'total_quizzes_taken': total_quizzes_taken,
        
        # Pass lists directly (HTML template handles JSON conversion)
        'quiz_dates': quiz_dates,
        'quiz_counts': quiz_counts,
        'topic_labels': topic_labels,
        'topic_counts': topic_counts,
        'premium_count': total_premium,
        'free_count': free_users,
    }
    
    return render(request, 'pages/admin_dashboard.html', context)