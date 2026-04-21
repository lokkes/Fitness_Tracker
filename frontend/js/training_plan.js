document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("training-plan-form");
    const steps = Array.from(document.querySelectorAll(".question-step"));
    const nextButton = document.getElementById("next-step-btn");
    const prevButton = document.getElementById("prev-step-btn");
    const submitButton = document.getElementById("submit-plan-btn");
    const stepLabel = document.getElementById("step-label");
    const progressPercent = document.getElementById("progress-percent");
    const progressFill = document.getElementById("progress-fill");
    const feedback = document.getElementById("form-feedback");
    const resultsCard = document.getElementById("results-card");
    const overviewGrid = document.getElementById("overview-grid");
    const planTableBody = document.getElementById("plan-table-body");
    const buildAnotherButton = document.getElementById("build-another-btn");

    const daysRange = document.getElementById("days-range");
    const durationRange = document.getElementById("duration-range");
    const fatigueRange = document.getElementById("fatigue-range");
    const daysValue = document.getElementById("days-range-value");
    const durationValue = document.getElementById("duration-range-value");
    const fatigueValue = document.getElementById("fatigue-range-value");

    let currentStep = 0;

    function syncRangeLabels() {
        daysValue.textContent = `${daysRange.value} day${daysRange.value === "1" ? "" : "s"}`;
        durationValue.textContent = `${durationRange.value} min`;
        fatigueValue.textContent = `${fatigueRange.value} / 10`;
    }

    function renderStep() {
        steps.forEach((step, index) => {
            step.classList.toggle("active", index === currentStep);
        });

        const progress = Math.round(((currentStep + 1) / steps.length) * 100);
        stepLabel.textContent = `Step ${currentStep + 1} of ${steps.length}`;
        progressPercent.textContent = `${progress}%`;
        progressFill.style.width = `${progress}%`;

        prevButton.classList.toggle("hidden", currentStep === 0);
        nextButton.classList.toggle("hidden", currentStep === steps.length - 1);
        submitButton.classList.toggle("hidden", currentStep !== steps.length - 1);
        feedback.textContent = "";
    }

    function getCheckedValues(name) {
        return Array.from(document.querySelectorAll(`input[name="${name}"]:checked`)).map((input) => input.value);
    }

    function validateStep() {
        if (currentStep === 1 && getCheckedValues("primary_goals").length === 0) {
            feedback.textContent = "Choose at least one training goal before moving on.";
            return false;
        }

        return true;
    }

    function buildPayload() {
        const preferredTime = document.querySelector('input[name="preferred_time"]:checked');
        const fightDate = form.elements.fight_date.value;
        const weaknesses = getCheckedValues("weakness");

        return {
            experience: document.querySelector('input[name="experience"]:checked').value,
            goal: {
                primary_goals: getCheckedValues("primary_goals"),
                fight_date: fightDate || null
            },
            availability: {
                days_per_week: Number(form.elements.days_per_week.value),
                session_duration: Number(form.elements.session_duration.value),
                preferred_time: preferredTime ? preferredTime.value : null
            },
            equipment: {
                has_heavy_bag: form.elements.has_heavy_bag.checked,
                has_speed_bag: form.elements.has_speed_bag.checked,
                has_sparring_partner: form.elements.has_sparring_partner.checked,
                has_gym: form.elements.has_gym.checked,
                has_weights: form.elements.has_weights.checked
            },
            weakness: weaknesses.length > 0 ? weaknesses : null,
            context: {
                current_week: Number(form.elements.current_week.value),
                missed_sessions_last_week: Number(form.elements.missed_sessions_last_week.value),
                fatigue_level: Number(form.elements.fatigue_level.value)
            }
        };
    }

    async function parseApiResponse(response) {
        const text = await response.text();

        try {
            return text ? JSON.parse(text) : {};
        } catch (error) {
            throw new Error(`Server returned non-JSON response (${response.status}). Check that the backend is running and the route exists.`);
        }
    }

    function renderOverview(planOverview) {
        const items = [
            { label: "Days Per Week", value: planOverview.days_per_week },
            { label: "Experience", value: capitalize(planOverview.experience) },
            { label: "Primary Goals", value: planOverview.primary_goals.map(formatToken).join(", ") }
        ];

        overviewGrid.innerHTML = items.map((item) => `
            <article class="overview-item">
                <strong>${item.label}</strong>
                <span>${item.value}</span>
            </article>
        `).join("");
    }

    function createList(items) {
        if (!items || items.length === 0) {
            return "<span>No details provided.</span>";
        }

        return `<ul>${items.map((item) => `<li>${item}</li>`).join("")}</ul>`;
    }

    function renderPlan(weekPlan) {
        planTableBody.innerHTML = weekPlan.map((dayPlan) => `
            <tr>
                <td>${dayPlan.day}</td>
                <td>${dayPlan.focus}</td>
                <td>${dayPlan.duration_minutes} min</td>
                <td>${createList(dayPlan.workout)}</td>
                <td>${createList(dayPlan.notes)}</td>
            </tr>
        `).join("");
    }

    function capitalize(value) {
        return value.charAt(0).toUpperCase() + value.slice(1);
    }

    function formatToken(value) {
        return value
            .split("_")
            .map((part) => capitalize(part))
            .join(" ");
    }

    nextButton.addEventListener("click", () => {
        if (!validateStep()) {
            return;
        }

        currentStep = Math.min(currentStep + 1, steps.length - 1);
        renderStep();
    });

    prevButton.addEventListener("click", () => {
        currentStep = Math.max(currentStep - 1, 0);
        renderStep();
    });

    buildAnotherButton.addEventListener("click", () => {
        resultsCard.classList.add("hidden");
        window.scrollTo({ top: 0, behavior: "smooth" });
    });

    [daysRange, durationRange, fatigueRange].forEach((input) => {
        input.addEventListener("input", syncRangeLabels);
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        if (!validateStep()) {
            return;
        }

        const payload = buildPayload();
        feedback.textContent = "Building your plan...";
        submitButton.disabled = true;
        submitButton.textContent = "Building...";

        try {
            const response = await fetch("/training_plan", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await parseApiResponse(response);

            if (!response.ok || !data.success) {
                throw new Error(data.detail || data.message || "Unable to generate the training plan.");
            }

            renderOverview(data.plan_overview);
            renderPlan(data.week_plan);
            resultsCard.classList.remove("hidden");
            feedback.textContent = "Plan generated successfully.";
            resultsCard.scrollIntoView({ behavior: "smooth", block: "start" });
        } catch (error) {
            feedback.textContent = error.message || "Something went wrong while creating the training plan.";
        } finally {
            submitButton.disabled = false;
            submitButton.textContent = "Build Plan";
        }
    });

    syncRangeLabels();
    renderStep();
});
