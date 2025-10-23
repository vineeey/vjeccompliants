// List of 10 background images (royalty-free, education, complaints, Vimal Jyothi Engineering College)
const images = [
  '/static/complaints/img/vjec4.jpg',
  '/static/complaints/img/vjec5.webp',
  '/static/complaints/img/vjec6.jpg',
];

let current = 0;
const slideshow = document.getElementById('bg-slideshow');
if (slideshow) {
  function showNext() {
    slideshow.style.backgroundImage = `url('${images[current]}')`;
    current = (current + 1) % images.length;
  }
  showNext();
  setInterval(showNext, 6000);
}
