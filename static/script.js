document.getElementById('visualizeButton').addEventListener('click', function() {
    const testElement = document.getElementById('testElement');
    testElement.classList.add('slide-out');
    
    testElement.addEventListener('animationend', function() {
        window.location.href = '/visualize';
    });
});