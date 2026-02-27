document.addEventListener('DOMContentLoaded', function() {
    // Навигация по модулям
    const moduleNavBtns = document.querySelectorAll('.module-nav-btn');
    const moduleContents = document.querySelectorAll('.module-content');
    
    moduleNavBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const moduleId = this.getAttribute('data-module');
            
            // Убираем активный класс у всех кнопок и контента
            moduleNavBtns.forEach(b => b.classList.remove('active'));
            moduleContents.forEach(c => c.classList.remove('active'));
            
            // Добавляем активный класс текущей кнопке
            this.classList.add('active');
            
            // Показываем соответствующий контент
            if (moduleId === 'practice') {
                document.getElementById('module-practice').classList.add('active');
            } else {
                document.getElementById(`module-${moduleId}`).classList.add('active');
            }
        });
    });
    
    // Раскрытие подсказок
    const hintBtns = document.querySelectorAll('.hint-btn');
    hintBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const hintContent = this.nextElementSibling;
            hintContent.classList.toggle('active');
            
            // Меняем текст кнопки
            if (hintContent.classList.contains('active')) {
                this.textContent = 'Скрыть подсказку';
            } else {
                this.textContent = 'Подсказка';
            }
        });
    });
    
    // Кнопки решения заданий
    const solutionBtns = document.querySelectorAll('.task-card .lesson-btn');
    solutionBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            alert('Решение задания будет доступно после выполнения самостоятельной попытки!');
        });
    });
});
// Функция для открытия уроков
function openLesson(lessonName) {
    // Проверяем, существует ли страница урока
    const lessonPages = {
        'lesson1': 'lesson1.html',
        'lesson2': 'lesson2.html',
        'lesson3': 'lesson3.html',
        'lesson4': 'lesson4.html',
        'lesson5': 'lesson5.html',
        'lesson6': 'lesson6.html',
        'lesson7': 'lesson7.html',
        'lesson8': 'lesson8.html',
        'lesson9': 'lesson9.html',
        'lesson10': 'lesson10.html',
        'lesson11': 'lesson11.html',
        'lesson12': 'lesson12.html',
        'lesson13': 'lesson13.html',
        'lesson14': 'lesson14.html'
    };
    
    if (lessonPages[lessonName]) {
        window.location.href = lessonPages[lessonName];
    } else {
        alert('Страница урока пока не готова!');
    }
}
