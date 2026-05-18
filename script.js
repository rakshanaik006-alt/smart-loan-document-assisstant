// script.js

// Theme Toggle
const themeToggle = document.getElementById("themeToggle");

themeToggle.addEventListener("click", () => {
  document.body.classList.toggle("light-mode");

  if(document.body.classList.contains("light-mode")){
    themeToggle.innerHTML = `<i class="fa-solid fa-sun"></i>`;
  } else {
    themeToggle.innerHTML = `<i class="fa-solid fa-moon"></i>`;
  }
});

// Circular Progress Animation
let circularProgress = document.querySelector(".circular-progress");
let valueContainer = document.querySelector(".value-container");

let progressValue = 0;
let progressEndValue = 85;

let speed = 20;

let progress = setInterval(() => {
  progressValue++;

  valueContainer.textContent = `${progressValue}%`;

  circularProgress.style.background = `
    conic-gradient(
      #00c6ff ${progressValue * 3.6}deg,
      #1f2a44 0deg
    )
  `;

  if(progressValue == progressEndValue){
    clearInterval(progress);
  }

}, speed);

// Drag Upload Effect
const dropArea = document.getElementById("dropArea");

dropArea.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropArea.style.borderColor = "#7f5cff";
});

dropArea.addEventListener("dragleave", () => {
  dropArea.style.borderColor = "#00c6ff";
});

dropArea.addEventListener("drop", (e) => {
  e.preventDefault();

  dropArea.innerHTML = `
    <i class="fa-solid fa-circle-check"></i>
    <h3>Upload Successful</h3>
  `;
});

// Toast Notification
const submitBtn = document.getElementById("submitBtn");
const toast = document.getElementById("toast");

submitBtn.addEventListener("click", () => {

  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 4000);

});

// Smooth Reveal Animation
const cards = document.querySelectorAll(
  ".feature-card, .loan-card, .checker-card, .verify-card, .widget"
);

window.addEventListener("scroll", () => {

  cards.forEach(card => {

    const cardTop = card.getBoundingClientRect().top;

    if(cardTop < window.innerHeight - 100){
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    }

  });

});

// Initial hidden state
cards.forEach(card => {
  card.style.opacity = "0";
  card.style.transform = "translateY(40px)";
  card.style.transition = "0.6s ease";
});