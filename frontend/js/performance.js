document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("performance-form");
    const feedback = document.getElementById("performance-feedback");
    const statusBadge = document.getElementById("performance-status-badge");
    const snapshotGrid = document.getElementById("snapshot-grid");
    const refreshButton = document.getElementById("refresh-performance-btn");

    const fieldIds = [
        "sprint_100m_seconds",
        "sprint_400m_seconds",
        "run_5k_minutes",
        "bench_press_kg",
        "squat_kg",
        "deadlift_kg",
        "pull_ups",
        "push_ups",
        "rounds_completed"
    ];

    const metricLabels = {
        sprint_100m_seconds: "100m Sprint",
        sprint_400m_seconds: "400m Sprint",
        run_5k_minutes: "5k Run",
        bench_press_kg: "Bench Press",
        squat_kg: "Squat",
        deadlift_kg: "Deadlift",
        pull_ups: "Pull-ups",
        push_ups: "Push-ups",
        rounds_completed: "Rounds"
    };

    function getEmail() {
        return localStorage.getItem("email");
    }

    function fillForm(data = {}) {
        fieldIds.forEach((id) => {
            const input = document.getElementById(id);
            if (!input) {
                return;
            }
            input.value = data[id] ?? "";
        });
    }

    function formatMetricValue(id, value) {
        if (value === null || value === undefined || value === "") {
            return "Not set";
        }

        if (id.includes("_kg")) {
            return `${value} kg`;
        }

        if (id.includes("seconds")) {
            return `${value} sec`;
        }

        if (id === "run_5k_minutes") {
            return `${value} min`;
        }

        if (id === "rounds_completed") {
            return `${value} rounds`;
        }

        return `${value} reps`;
    }

    function renderSnapshot(data = {}) {
        snapshotGrid.innerHTML = fieldIds.map((id) => `
            <article class="snapshot-item">
                <strong>${metricLabels[id]}</strong>
                <span>${formatMetricValue(id, data[id])}</span>
            </article>
        `).join("");
    }

    function buildPayload() {
        const email = getEmail();
        const payload = { email };

        fieldIds.forEach((id) => {
            const value = document.getElementById(id).value.trim();
            payload[id] = value === "" ? null : Number(value);
        });

        return payload;
    }

    async function parseApiResponse(response) {
        const text = await response.text();

        try {
            return text ? JSON.parse(text) : {};
        } catch (error) {
            throw new Error(`Server returned non-JSON response (${response.status}). Check that the backend is running and the route exists.`);
        }
    }

    async function loadPerformance() {
        const email = getEmail();

        if (!email) {
            feedback.textContent = "Please log in first to manage performance data.";
            statusBadge.textContent = "Login required";
            return;
        }

        feedback.textContent = "Loading your saved performance...";

        try {
            const response = await fetch(`/api/performance?email=${encodeURIComponent(email)}`);
            const result = await parseApiResponse(response);

            if (!result.success) {
                fillForm();
                renderSnapshot();
                feedback.textContent = "No saved performance yet. Enter your numbers and save them.";
                statusBadge.textContent = "New profile";
                return;
            }

            fillForm(result.data);
            renderSnapshot(result.data);
            feedback.textContent = "Saved performance loaded.";
            statusBadge.textContent = "Loaded";
        } catch (error) {
            feedback.textContent = "Could not load performance data.";
            statusBadge.textContent = "Error";
        }
    }

    refreshButton.addEventListener("click", () => {
        loadPerformance();
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const email = getEmail();
        if (!email) {
            feedback.textContent = "Please log in first to save performance data.";
            statusBadge.textContent = "Login required";
            return;
        }

        const payload = buildPayload();
        feedback.textContent = "Saving performance...";
        statusBadge.textContent = "Saving";

        try {
            const createResponse = await fetch("/performance", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const createResult = await parseApiResponse(createResponse);

            if (createResult.success) {
                renderSnapshot(payload);
                feedback.textContent = "Performance saved successfully.";
                statusBadge.textContent = "Saved";
                return;
            }

            if (!createResult.message || !createResult.message.includes("already exists")) {
                throw new Error(createResult.message || "Could not save performance.");
            }

            const updateResponse = await fetch("/performance", {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            const updateResult = await parseApiResponse(updateResponse);

            if (!updateResult.success) {
                throw new Error(updateResult.message || "Could not update performance.");
            }

            renderSnapshot(payload);
            feedback.textContent = "Performance updated successfully.";
            statusBadge.textContent = "Updated";
        } catch (error) {
            feedback.textContent = error.message || "Something went wrong while saving performance.";
            statusBadge.textContent = "Error";
        }
    });

    renderSnapshot();
    loadPerformance();
});
