// Amazon Clone JavaScript

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl)
    });

    // Initialize carousel with enhanced options
    const dailyOffersCarousel = document.getElementById('dailyOffersCarousel');
    if (dailyOffersCarousel) {
        const carousel = new bootstrap.Carousel(dailyOffersCarousel, {
            interval: 5000,
            wrap: true,
            touch: true,
            pause: 'hover'
        });
        
        // Add swipe support for mobile
        let touchStartX = 0;
        let touchEndX = 0;
        
        dailyOffersCarousel.addEventListener('touchstart', function(e) {
            touchStartX = e.changedTouches[0].screenX;
        }, false);
        
        dailyOffersCarousel.addEventListener('touchend', function(e) {
            touchEndX = e.changedTouches[0].screenX;
            handleSwipe();
        }, false);
        
        function handleSwipe() {
            if (touchEndX < touchStartX) {
                // Swipe left - next slide
                carousel.next();
            }
            if (touchEndX > touchStartX) {
                // Swipe right - previous slide
                carousel.prev();
            }
        }
        
        // Add keyboard navigation
        document.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowLeft') {
                carousel.prev();
            } else if (e.key === 'ArrowRight') {
                carousel.next();
            }
        });
        
        // Pause carousel on hover
        dailyOffersCarousel.addEventListener('mouseenter', function() {
            carousel.pause();
        });
        
        dailyOffersCarousel.addEventListener('mouseleave', function() {
            carousel.cycle();
        });
        
        // Add click event to entire slide
        const slides = dailyOffersCarousel.querySelectorAll('.carousel-item');
        slides.forEach(function(slide) {
            slide.addEventListener('click', function(e) {
                // Only navigate if the click wasn't on a button or link
                if (!e.target.closest('a') && !e.target.closest('button')) {
                    const shopNowBtn = this.querySelector('.btn-warning');
                    if (shopNowBtn) {
                        shopNowBtn.click();
                    }
                }
            });
        });
    }

    // Cart quantity update
    const quantityInputs = document.querySelectorAll('.cart-quantity');
    if (quantityInputs) {
        quantityInputs.forEach(input => {
            input.addEventListener('change', function() {
                // Here you would typically update the cart via AJAX
                console.log('Quantity updated to: ' + this.value);
            });
        });
    }

    // Product image gallery (for product detail page)
    const thumbnails = document.querySelectorAll('.product-thumbnail');
    if (thumbnails) {
        thumbnails.forEach(thumb => {
            thumb.addEventListener('click', function() {
                const mainImg = document.querySelector('.product-main-image');
                if (mainImg) {
                    mainImg.src = this.src;
                }
            });
        });
    }

    // Search suggestions
    const searchInput = document.querySelector('input[type="search"]');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            // Here you would typically fetch search suggestions via AJAX
            console.log('Searching for: ' + this.value);
        });
    }
    
    // Add parallax effect to carousel
    window.addEventListener('scroll', function() {
        const carousel = document.querySelector('.amazon-carousel');
        if (carousel) {
            const scrollPosition = window.scrollY;
            if (scrollPosition < 400) {
                const offerImages = document.querySelectorAll('.offer-image');
                offerImages.forEach(function(img) {
                    img.style.transform = `translateY(${scrollPosition * 0.1}px)`;
                });
            }
        }
    });
});