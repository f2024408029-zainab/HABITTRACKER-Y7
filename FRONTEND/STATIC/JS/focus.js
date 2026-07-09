// focus.js — Focus Mode countdown timer + session logging.

document.addEventListener("DOMContentLoaded", () => {
  const hoursInput = document.getElementById("focusHours");
  const minutesInput = document.getElementById("focusMinutes");
  const secondsInput = document.getElementById("focusSeconds");
  const display = document.getElementById("focusDisplay");
  const startBtn = document.getElementById("focusStartBtn");
  const stopBtn = document.getElementById("focusStopBtn");

  if (!startBtn || !stopBtn || !display) return;

  let totalSeconds = 0;
  let remaining = 0;
  let timerId = null;

  function pad(n) {
    return n.toString().padStart(2, "0");
  }

  function renderDisplay(secs) {
    const h = Math.floor(secs / 3600);
    const m = Math.floor((secs % 3600) / 60);
    const s = secs % 60;
    display.textContent = `${pad(h)}:${pad(m)}:${pad(s)}`;
  }

  function setInputsDisabled(disabled) {
    hoursInput.disabled = disabled;
    minutesInput.disabled = disabled;
    secondsInput.disabled = disabled;
  }

  function logSession(completedSeconds) {
    if (completedSeconds <= 0) return;
    const formData = new FormData();
    formData.append("duration_seconds", completedSeconds);
    formData.append("session_date", new Date().toISOString().slice(0, 10));
    fetch("/focus", { method: "POST", body: formData })
      .then((res) => res.json())
      .then((data) => {
        const totalEl = document.querySelector(".focus-total strong");
        if (totalEl && data.total_focus) totalEl.textContent = data.total_focus;
      })
      .catch(() => {});
  }

  function finishSession(completedSeconds) {
    clearInterval(timerId);
    timerId = null;
    startBtn.disabled = false;
    stopBtn.disabled = true;
    setInputsDisabled(false);
    logSession(completedSeconds);
  }

  startBtn.addEventListener("click", () => {
    const h = parseInt(hoursInput.value, 10) || 0;
    const m = parseInt(minutesInput.value, 10) || 0;
    const s = parseInt(secondsInput.value, 10) || 0;
    totalSeconds = h * 3600 + m * 60 + s;

    if (totalSeconds <= 0) {
      alert("Please set a focus duration greater than zero.");
      return;
    }

    remaining = totalSeconds;
    renderDisplay(remaining);
    setInputsDisabled(true);
    startBtn.disabled = true;
    stopBtn.disabled = false;

    timerId = setInterval(() => {
      remaining -= 1;
      renderDisplay(remaining);
      if (remaining <= 0) {
        finishSession(totalSeconds);
        alert("Focus session complete! Great work.");
      }
    }, 1000);
  });

  stopBtn.addEventListener("click", () => {
    const completed = totalSeconds - remaining;
    finishSession(completed);
    renderDisplay(0);
  });
});

