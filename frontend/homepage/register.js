javascript
const form = document.getElementById("registerForm");

const password = document.getElementById("password");
const confirmPassword = document.getElementById("confirmPassword");

const togglePassword = document.getElementById("togglePassword");

if (togglePassword) {
    togglePassword.addEventListener("click", () => {
        password.type =
            password.type === "password" ? "text" : "password";

        togglePassword.classList.toggle("fa-eye");
        togglePassword.classList.toggle("fa-eye-slash");
    });
}

if (form) {
    form.addEventListener("submit", async (e) => {

        e.preventDefault();

        const username = document.getElementById("username").value.trim();
        const email = document.getElementById("email").value.trim();
        const passwordValue = password.value;
        const confirmPasswordValue = confirmPassword.value;

        if (passwordValue !== confirmPasswordValue) {
            alert("Passwords do not match.");
            return;
        }

        const button = form.querySelector(".login-btn");

        button.disabled = true;
        button.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Creating Account...';

        try {

            const response = await fetch("/api/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    username: username,
                    email: email,
                    password: passwordValue
                })
            });

            let data;

            try {
                data = await response.json();
            } catch (jsonError) {
                data = {
                    message: "Database is temporarily unavailable. Please try again later."
                };
            }

            if (response.ok) {

                alert(data.message || "Account created successfully!");

                window.location.href = "/frontend/homepage/login.html";

            } else {

                alert(
                    data.message ||
                    "Database is temporarily unavailable. Please try again later."
                );

                button.disabled = false;
                button.innerHTML =
                    'Create Account <i class="fa-solid fa-arrow-right"></i>';
            }

        } catch (error) {

            alert(
                "Database is temporarily unavailable. Please try again later."
            );

            button.disabled = false;
            button.innerHTML =
                'Create Account <i class="fa-solid fa-arrow-right"></i>';
        }

    });
}

