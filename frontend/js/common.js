document.addEventListener("DOMContentLoaded", async () => {
    const usernameNodes = document.querySelectorAll(".username");
    if (usernameNodes.length === 0) {
        return;
    }

    const email = localStorage.getItem("email");
    if (!email) {
        usernameNodes.forEach((node) => {
            node.textContent = "Welcome";
        });
        return;
    }

    try {
        const response = await fetch(`/api/user_summary?email=${encodeURIComponent(email)}`);
        const text = await response.text();
        const result = text ? JSON.parse(text) : {};

        if (!result.success || !result.data) {
            usernameNodes.forEach((node) => {
                node.textContent = "Welcome";
            });
            return;
        }

        usernameNodes.forEach((node) => {
            node.textContent = `Welcome, ${result.data.name}`;
        });
    } catch (error) {
        usernameNodes.forEach((node) => {
            node.textContent = "Welcome";
        });
    }
});
