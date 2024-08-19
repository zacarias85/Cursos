document.addEventListener('DOMContentLoaded', function() {
    // Exemplo de lazy loading para imagens
    const images = document.querySelectorAll('img[data-src]');
    const config = {
        rootMargin: '0px 0px 50px 0px',
        threshold: 0
    };

    let observer = new IntersectionObserver(function(entries, self) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                preloadImage(entry.target);
                self.unobserve(entry.target);
            }
        });
    }, config);

    images.forEach(image => {
        observer.observe(image);
    });

    function preloadImage(img) {
        const src = img.getAttribute('data-src');
        if (!src) { return; }
        img.src = src;
    }
});