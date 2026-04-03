document.addEventListener('DOMContentLoaded', () => {
    const email = localStorage.getItem("email");
    const name = document.getElementById("name");
    const wins = document.getElementById("wins");
    const losses = document.getElementById("losses");
    const draws = document.getElementById("draws");
    const fights = document.getElementById("fights");
    const height = document.getElementById("height");
    const weight = document.getElementById("weight");
    const image = document.getElementById("image");
    const username = document.querySelector(".username");

    if (!email) {
        console.error("No logged in user email found in localStorage.");
        return;
    }

    fetch(`/api/profile?email=${encodeURIComponent(email)}`)
        .then((response) => response.json())
        .then((result) => {
            if (!result.success || !result.data) {
                alert(result.message || "Could not load profile.");
                return;
            }

            const data = result.data;

            name.textContent = data.name;
            wins.textContent = `${data.wins} W`;
            losses.textContent = `${data.losses} L`;
            draws.textContent = `${data.draws} D`;
            fights.textContent = `Total fights: ${data.fights}`;
            height.textContent = `Height: ${data.height}`;
            weight.textContent = `Weight: ${data.weight}`;
            username.textContent = `Welcome, ${data.name}`;

            if (data.image_path) {
                image.src = `/${data.image_path}`;
                image.alt = `${data.name} image`;
            }
        })
        .catch((error) => {
            console.error("Profile fetch error:", error);
            alert("Something went wrong while loading the profile.");
        });
});
