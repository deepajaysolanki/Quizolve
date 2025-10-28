document.addEventListener('DOMContentLoaded', function () {
    // --- Get all HTML elements ---
    const quizData = document.getElementById('quiz-data');
    const questionText = document.getElementById('question-text');
    const optionsContainer = document.getElementById('options-container');
    const nextBtn = document.getElementById('next-question-btn');
    const endQuizBtn = document.getElementById('end-quiz-btn');
    const currentQuestionNumSpan = document.getElementById('current-question-num');
    const totalQuestionsSpan = document.getElementById('total-questions');
    const timerDisplay = document.getElementById('timer');
    const progressBar = document.getElementById('time-progress-bar');
    
    // --- Get data from Django ---
    const GET_QUESTION_URL = quizData.dataset.getQuestionUrl;
    const RECORD_ANSWER_URL = quizData.dataset.checkAnswerUrl; // This is your 'record-answer-api'
    const END_EXAM_EARLY_URL = quizData.dataset.endExamEarlyUrl;
    const RESULTS_PAGE_URL = quizData.dataset.resultsPageUrl;
    const CSRF_TOKEN = quizData.dataset.csrfToken;
    const initialTimeLimit = parseInt(quizData.dataset.timeLimit, 10);
    const totalQuestions = parseInt(quizData.dataset.totalQuestions, 10);
    
    // --- State variables ---
    let correctAnswer = '';
    let currentQuestionText = ''; // Variable to hold the actual question text
    let timerInterval;
    let timeLeft = initialTimeLimit;
    let questionNumber = 0;
    let quizIsOver = false;

    // --- Initialize Display ---
    totalQuestionsSpan.textContent = totalQuestions > 0 ? totalQuestions : '?';
    currentQuestionNumSpan.textContent = 0;

    // --- Main Functions ---
    async function getNextQuestion() {
        if (totalQuestions > 0 && questionNumber >= totalQuestions) {
            quizIsOver = true;
            alert("You have completed the quiz!");
            window.location.href = RESULTS_PAGE_URL;
            return;
        }
        questionText.textContent = questionNumber === 0 ? 'Starting your quiz...' : 'Loading next question...';
        optionsContainer.innerHTML = '';
        nextBtn.disabled = true;
        clearInterval(timerInterval);
        
        const response = await fetch(GET_QUESTION_URL);
        const data = await response.json();
        
        if (data.error) {
            questionText.textContent = data.error;
            return;
        }
        
        questionNumber++;
        currentQuestionNumSpan.textContent = questionNumber;

        // Correctly save and display the new question
        currentQuestionText = data.question; 
        questionText.textContent = currentQuestionText;
        correctAnswer = data.answer;
        
        data.options.forEach(optionText => {
            const optionButton = document.createElement('button');
            optionButton.className = 'option';
            optionButton.textContent = optionText;
            optionButton.addEventListener('click', handleOptionClick);
            optionsContainer.appendChild(optionButton);
        });
        startTimer();
    }

    // This function is called when an option is clicked
    function handleOptionClick(event) {
        clearInterval(timerInterval);
        const selectedOption = event.target;
        const userAnswer = selectedOption.textContent;

        document.querySelectorAll('.option').forEach(opt => {
            opt.disabled = true;
            if (opt.textContent === userAnswer) {
                opt.classList.add('selected'); // Highlight the selected answer
            }
        });

        // Record the answer and move to the next question
        recordAnswer(currentQuestionText, userAnswer, correctAnswer).then(() => {
            setTimeout(() => {
                getNextQuestion();
            }, 1000);
        });
    }

    // This function is called when the timer runs out
    async function handleTimeUp() {
        clearInterval(timerInterval);
        document.querySelectorAll('.option').forEach(opt => {
            opt.disabled = true;
        });

        // Record "Time's Up" as the answer
        await recordAnswer(currentQuestionText, "Time's Up", correctAnswer);
        getNextQuestion();
    }
    
    function startTimer() {
        timeLeft = initialTimeLimit;
        updateTimerDisplay();
        updateProgressBar();
        timerInterval = setInterval(() => {
            timeLeft--;
            updateTimerDisplay();
            updateProgressBar();
            if (timeLeft <= 0) handleTimeUp();
        }, 1000);
    }
    
    function updateTimerDisplay() { timerDisplay.textContent = timeLeft; }
    
    function updateProgressBar() {
        const progressPercent = (timeLeft / initialTimeLimit) * 100;
        progressBar.style.width = `${progressPercent}%`;
        if (progressPercent > 50) progressBar.style.backgroundColor = '#22c55e';
        else if (progressPercent > 20) progressBar.style.backgroundColor = '#f59e0b';
        else progressBar.style.backgroundColor = '#ef4444';
    }

    // This function sends the answer data to the backend
    async function recordAnswer(question, user_answer, correct_answer) {
        await fetch(RECORD_ANSWER_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': CSRF_TOKEN },
            body: JSON.stringify({
                'question': question,
                'user_answer': user_answer,
                'correct_answer': correct_answer
            })
        });
    }

    // --- Event Listeners ---
    nextBtn.addEventListener('click', getNextQuestion);
    
    endQuizBtn.addEventListener('click', (event) => {
        // This makes your <a> tag work like a button with a confirmation
        event.preventDefault();
        clearInterval(timerInterval);
        quizIsOver = true;
        const isExam = totalQuestions > 0;
        
        if (isExam) {
            const confirmMsg = "Are you sure you want to end the exam? This will count as your attempt for the day.";
            if (confirm(confirmMsg)) {
                fetch(END_EXAM_EARLY_URL, {
                    method: 'POST',
                    headers: { 'X-CSRFToken': CSRF_TOKEN, 'Content-Type': 'application/json' }
                }).then(() => window.location.href = RESULTS_PAGE_URL);
            }
        } else {
            window.location.href = RESULTS_PAGE_URL;
        }
    });

    // --- Start the quiz ---
    getNextQuestion();
});