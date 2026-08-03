document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("predictForm");
  const resultBox = document.getElementById("result");
  const modelTable = document.getElementById("modelTable");

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const gender = document.getElementById("gender").value;
    const study_time_hours = parseFloat(document.getElementById("study_time_hours").value);
    const attendance_percent = parseFloat(document.getElementById("attendance_percent").value);
    const sleep_hours = parseFloat(document.getElementById("sleep_hours").value);
    const parental_education = document.getElementById("parental_education").value;
    const internet_access = document.getElementById("internet_access").value;
    const extracurricular_activities = document.getElementById("extracurricular_activities").value;
    const part_time_job = document.getElementById("part_time_job").value;
    const previous_grade = parseFloat(document.getElementById("previous_grade").value);

    const btn = form.querySelector(".predict-btn");
    btn.disabled = true;
    btn.textContent = "Predicting...";
    resultBox.classList.add("hidden");

    try {
      const response = await fetch("/api/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          gender,
          study_time_hours,
          attendance_percent,
          sleep_hours,
          parental_education,
          internet_access,
          extracurricular_activities,
          part_time_job,
          previous_grade,
        }),
      });

      const data = await response.json();

      if (data.error) {
        showError(data.error);
      } else {
        showResult(data.prediction);
      }
    } catch (err) {
      showError("Network error. Please try again.");
    } finally {
      btn.disabled = false;
      btn.textContent = "Predict";
    }
  });

  function showResult(score) {
    resultBox.classList.remove("hidden", "error");
    resultBox.classList.add("success");
    resultBox.innerHTML =
      '<div class="label">Predicted Final Exam Score</div>' +
      '<div class="score">' + score + ' / 100</div>';
  }

  function showError(msg) {
    resultBox.classList.remove("hidden", "success");
    resultBox.classList.add("error");
    resultBox.textContent = "Error: " + msg;
  }

  async function loadModelInfo() {
    try {
      const response = await fetch("/api/model-info");
      const data = await response.json();

      if (data.models && data.models.length > 0) {
        let html = "<table><thead><tr>";
        html += "<th>Model</th><th>MAE</th><th>RMSE</th><th>R2</th>";
        html += "</tr></thead><tbody>";
        data.models.forEach((m) => {
          html +=
            "<tr>" +
            "<td>" + m.Model + "</td>" +
            "<td>" + m.MAE + "</td>" +
            "<td>" + m.RMSE + "</td>" +
            "<td>" + m.R2 + "</td>" +
            "</tr>";
        });
        html += "</tbody></table>";
        modelTable.innerHTML = html;
      }
    } catch (err) {
      modelTable.innerHTML = "<p>Could not load model comparison data.</p>";
    }
  }

  loadModelInfo();
});