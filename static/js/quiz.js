document.addEventListener('DOMContentLoaded', function () {
    // --- STATE MANAGEMENT ---
    let currentQuestions = [];
    let currentQuestionIndex = 0;
    let score = 0;
    let timer;
    const TIME_LIMIT = 15; // Time per question

    // --- DOM ELEMENTS ---
    const categorySelectionView = document.getElementById('category-selection');
    const quizInterfaceView = document.getElementById('quiz-interface');
    const resultsView = document.getElementById('results-screen');
    const categoryCards = document.querySelectorAll('.category-card');

    const questionCounterEl = document.getElementById('question-counter');
    const quizCategoryTitleEl = document.getElementById('quiz-category-title');
    const progressBarEl = document.getElementById('progress-bar');
    const questionTextEl = document.getElementById('question-text');
    const optionsContainerEl = document.getElementById('options-container');
    const nextBtn = document.getElementById('next-btn');
    const timerEl = document.getElementById('time');

    const finalScoreEl = document.getElementById('final-score');
    const correctAnswersEl = document.getElementById('correct-answers');
    const incorrectAnswersEl = document.getElementById('incorrect-answers');

    // --- EVENT LISTENERS ---
    categoryCards.forEach(card => {
        card.addEventListener('click', () => {
            const category = card.dataset.category;
            startQuiz(category);
        });
    });

    nextBtn.addEventListener('click', handleNextQuestion);

    // --- FUNCTIONS ---
    function startQuiz(category) {
        currentQuestions = quizData[category];
        quizCategoryTitleEl.textContent = category;
        currentQuestionIndex = 0;
        score = 0;

        categorySelectionView.style.display = 'none';
        resultsView.style.display = 'none';
        quizInterfaceView.style.display = 'block'; // Use block instead of flex

        showQuestion();
    }

    function showQuestion() {
        resetState();
        const question = currentQuestions[currentQuestionIndex];

        questionCounterEl.textContent = `${currentQuestionIndex + 1} / ${currentQuestions.length}`;
        progressBarEl.style.width = `${((currentQuestionIndex) / currentQuestions.length) * 100}%`;
        // Animate the progress bar to its new width
        setTimeout(() => {
            progressBarEl.style.width = `${((currentQuestionIndex + 1) / currentQuestions.length) * 100}%`;
        }, 100);

        questionTextEl.textContent = question.question;

        question.options.forEach(optionText => {
            const button = document.createElement('button');
            button.textContent = optionText;
            button.classList.add('option');
            button.addEventListener('click', () => selectAnswer(button, optionText, question.answer));
            optionsContainerEl.appendChild(button);
        });

        startTimer();
    }

    function resetState() {
        clearInterval(timer);
        optionsContainerEl.innerHTML = '';
        nextBtn.disabled = true;
    }

    function startTimer() {
        let timeLeft = TIME_LIMIT;
        timerEl.textContent = timeLeft;
        timer = setInterval(() => {
            timeLeft--;
            timerEl.textContent = timeLeft;
            if (timeLeft <= 0) {
                clearInterval(timer);
                handleTimeUp();
            }
        }, 1000);
    }

    function handleTimeUp() {
        const correctAnswer = currentQuestions[currentQuestionIndex].answer;
        document.querySelectorAll('.option').forEach(opt => {
            if (opt.textContent === correctAnswer) {
                opt.classList.add('correct');
            }
            opt.disabled = true;
        });
        nextBtn.disabled = false;
    }

    function selectAnswer(button, selectedOption, correctAnswer) {
        clearInterval(timer);
        document.querySelectorAll('.option').forEach(opt => opt.disabled = true);

        if (selectedOption === correctAnswer) {
            button.classList.add('correct');
            score++;
        } else {
            button.classList.add('incorrect');
            document.querySelectorAll('.option').forEach(opt => {
                if (opt.textContent === correctAnswer) {
                    opt.classList.add('correct');
                }
            });
        }

        nextBtn.disabled = false;
    }

    function handleNextQuestion() {
        currentQuestionIndex++;
        if (currentQuestionIndex < currentQuestions.length) {
            showQuestion();
        } else {
            showResults();
        }
    }

    function showResults() {
        quizInterfaceView.style.display = 'none';
        resultsView.style.display = 'block'; // Use block instead of flex

        finalScoreEl.textContent = `${score} / ${currentQuestions.length}`;
        correctAnswersEl.textContent = score;
        incorrectAnswersEl.textContent = currentQuestions.length - score;
    }

    const dropdownSelected = document.getElementById('dropdown-selected');
    const dropdownOptions = document.getElementById('dropdown-options');
    const hiddenInput = document.getElementById('difficulty-hidden-input');

    // Toggle the dropdown menu on click
    dropdownSelected.addEventListener('click', (event) => {
        event.stopPropagation(); // Prevents the window click listener from firing immediately
        dropdownOptions.classList.toggle('show');
    });

    // Handle option selection
    document.querySelectorAll('.dropdown-option').forEach(option => {
        option.addEventListener('click', () => {
            // Update the text of the selected box
            dropdownSelected.querySelector('span').textContent = option.textContent;
            // Update the value of the hidden input field that gets submitted
            hiddenInput.value = option.dataset.value;
            // Hide the options
            dropdownOptions.classList.remove('show');
        });
    });

    // Close the dropdown if the user clicks anywhere else on the page
    window.addEventListener('click', () => {
        if (dropdownOptions.classList.contains('show')) {
            dropdownOptions.classList.remove('show');
        }
    });

    // Quiz start with category and difficulty
    // Get the new dropdown element
    const container = document.querySelector('.quiz-view-container');
    const START_QUIZ_URL = container.dataset.startQuizUrl;
    const CSRF_TOKEN = container.dataset.csrfToken;
    const difficultySelector = document.getElementById('difficulty-selector');

    function startQuizWithCategory(topic, difficulty) {
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = START_QUIZ_URL;

        // CSRF token input
        const csrfInput = document.createElement('input');
        csrfInput.type = 'hidden';
        csrfInput.name = 'csrfmiddlewaretoken';
        csrfInput.value = CSRF_TOKEN;
       
        // Topic input
        const topicInput = document.createElement('input');
        topicInput.type = 'hidden';
        topicInput.name = 'topic';
        topicInput.value = topic;
       
        // Quiz type input
        const typeInput = document.createElement('input');
        typeInput.type = 'hidden';
        typeInput.name = 'quiz_type';
        typeInput.value = 'category';
        // form.appendChild(typeInput);

        // Difficulty input
        const difficultyInput = document.createElement('input');
        difficultyInput.type = 'hidden';
        difficultyInput.name = 'difficulty';
        difficultyInput.value = difficulty;

        // Add all inputs to the form
        form.appendChild(csrfInput);
        form.appendChild(topicInput);
        form.appendChild(typeInput);
        form.appendChild(difficultyInput);
        
        document.body.appendChild(form);
        form.submit();
    }

    const categoryButtons = document.querySelectorAll('.category-btn');
    categoryButtons.forEach(button => {
        button.addEventListener('click', () => {
            const category = button.dataset.category;
            // Read the selected difficulty from the dropdown
            const selectedDifficulty = difficultySelector.value;
            // Pass both values to the function
            startQuizWithCategory(category, selectedDifficulty);
        });
    });

});