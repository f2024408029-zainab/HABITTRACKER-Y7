// calendar.js — powers the interactive monthly calendar + day-entry modal.

const overlay = document.getElementById("dayModalOverlay");
const modalContent = document.getElementById("modalContent");
const closeBtn = document.getElementById("modalCloseBtn");

function openModalForDate(dateStr) {
  fetch(`/day/${dateStr}`)
    .then((res) => res.text())
    .then((html) => {
      modalContent.innerHTML = html;
      overlay.classList.add("open");
      wireUpForm(dateStr);
    });
}

function closeModal() {
  overlay.classList.remove("open");
  modalContent.innerHTML = "";
}

closeBtn.addEventListener("click", closeModal);
overlay.addEventListener("click", (e) => {
  if (e.target === overlay) closeModal();
});

// Attach click listeners to every day cell on the calendar
document.querySelectorAll(".cal-day[data-date]").forEach((cell) => {
  cell.addEventListener("click", () => openModalForDate(cell.dataset.date));
});

function wireUpForm(dateStr) {
  const form = document.getElementById("dayForm");
  if (!form) return;

  // Mood: single-select
  const moodInput = document.getElementById("moodInput");
  form.querySelectorAll(".mood-option").forEach((btn) => {
    btn.addEventListener("click", () => {
      form.querySelectorAll(".mood-option").forEach((b) => b.classList.remove("selected"));
      btn.classList.add("selected");
      moodInput.value = btn.dataset.value;
    });
  });

  // Emotions: multi-select chips
  form.querySelectorAll(".emotion-chip").forEach((chip) => {
    chip.addEventListener("click", () => chip.classList.toggle("selected"));
  });

  // Hobby: single-select chips
  const hobbyInput = document.getElementById("hobbyInput");
  form.querySelectorAll(".hobby-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      form.querySelectorAll(".hobby-chip").forEach((c) => c.classList.remove("selected"));
      chip.classList.add("selected");
      hobbyInput.value = chip.dataset.value;
    });
  });

  // Health: single-select chips
  const healthInput = document.getElementById("healthInput");
  form.querySelectorAll(".health-chip").forEach((chip) => {
    chip.addEventListener("click", () => {
      form.querySelectorAll(".health-chip").forEach((c) => c.classList.remove("selected"));
      chip.classList.add("selected");
      healthInput.value = chip.dataset.value;
    });
  });

  // Submit via fetch so the calendar can update without a full reload
  form.addEventListener("submit", (e) => {
    e.preventDefault();

    if (!moodInput.value) {
      alert("Please select a mood before saving.");
      return;
    }

    const formData = new FormData(form);
    // Add selected emotions manually (chips aren't native form controls)
    form.querySelectorAll(".emotion-chip.selected").forEach((chip) => {
      formData.append("emotions", chip.dataset.value);
    });

    fetch(`/day/${dateStr}`, { method: "POST", body: formData })
      .then((res) => res.json())
      .then((data) => {
        const box = document.getElementById("recommendationsBox");
        const list = document.getElementById("recommendationsList");
        list.innerHTML = "";
        data.recommendations.forEach((r) => {
          const li = document.createElement("li");
          li.textContent = r;
          list.appendChild(li);
        });
        box.style.display = data.recommendations.length ? "block" : "none";

        // Reload the page shortly after so the calendar cell shows the new mood emoji
        setTimeout(() => window.location.reload(), 900);
      })
      .catch(() => alert("Something went wrong saving your entry. Please try again."));
  });
}