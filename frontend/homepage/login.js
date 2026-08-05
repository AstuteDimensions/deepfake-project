// =========================================
// PASSWORD TOGGLE
// =========================================

const password = document.getElementById("password");
const togglePassword = document.getElementById("togglePassword");

if (password && togglePassword) {

    togglePassword.addEventListener("click", () => {

        if (password.type === "password") {

            password.type = "text";

            togglePassword.classList.remove("fa-eye");
            togglePassword.classList.add("fa-eye-slash");

        }

        else {

            password.type = "password";

            togglePassword.classList.remove("fa-eye-slash");
            togglePassword.classList.add("fa-eye");

        }

    });

}



// =========================================
// LOGIN FORM
// =========================================

const form = document.getElementById("loginForm");

if (form) {

    form.addEventListener("submit", function (e) {

        e.preventDefault();

        const username =
            document.querySelector("input[type='text']").value.trim();

        const passwordValue =
            document.getElementById("password").value.trim();

        if (username === "" || passwordValue === "") {

            alert("Please fill in all fields.");

            return;

        }

        const button =
            document.querySelector(".login-btn");

        const originalText =
            button.innerHTML;

        button.disabled = true;

        button.innerHTML =
            '<i class="fa-solid fa-spinner fa-spin"></i> Signing In...';

        setTimeout(() => {

            button.innerHTML = originalText;

            button.disabled = false;

            alert("Backend authentication will be connected here.");

        }, 1800);

    });

}



// =========================================
// PAGE LOAD ANIMATION
// =========================================

window.addEventListener("load", () => {

    document.body.style.opacity = "0";

    document.body.style.transition =
        "opacity 0.8s ease";

    setTimeout(() => {

        document.body.style.opacity = "1";

    }, 100);

});



// =========================================
// MAIN PANEL ANIMATION
// =========================================

const panel =
    document.querySelector(".main-panel");

if (panel) {

    panel.animate(

        [

            {
                opacity: 0,
                transform: "translateY(25px)"
            },

            {
                opacity: 1,
                transform: "translateY(0)"
            }

        ],

        {

            duration: 900,

            easing: "ease-out",

            fill: "forwards"

        }

    );

}



// =========================================
// INPUT FOCUS EFFECT
// =========================================

const inputs =
    document.querySelectorAll(".input-box input");

inputs.forEach(input => {

    input.addEventListener("focus", () => {

        input.parentElement.style.transform =
            "scale(1.02)";

    });

    input.addEventListener("blur", () => {

        input.parentElement.style.transform =
            "scale(1)";

    });

});



// =========================================
// RIPPLE EFFECT
// =========================================

const loginButton =
    document.querySelector(".login-btn");

if (loginButton) {

    loginButton.addEventListener("click", function (e) {

        const circle =
            document.createElement("span");

        const diameter =
            Math.max(
                this.clientWidth,
                this.clientHeight
            );

        const radius =
            diameter / 2;

        circle.style.width =
            circle.style.height =
            `${diameter}px`;

        circle.style.left =
            `${e.clientX - this.getBoundingClientRect().left - radius}px`;

        circle.style.top =
            `${e.clientY - this.getBoundingClientRect().top - radius}px`;

        circle.classList.add("ripple");

        const ripple =
            this.getElementsByClassName("ripple")[0];

        if (ripple) {

            ripple.remove();

        }

        this.appendChild(circle);

    });

}



// =========================================
// FEATURE CARD ANIMATION
// =========================================

const cards =
    document.querySelectorAll(".feature,.quote");

cards.forEach(card => {

    card.addEventListener("mouseenter", () => {

        card.style.transform =
            "translateY(-5px)";

    });

    card.addEventListener("mouseleave", () => {

        card.style.transform =
            "translateY(0)";

    });

});



// =========================================
// LOGO GLOW
// =========================================

const logo =
    document.querySelector(".logo");

if (logo) {

    setInterval(() => {

        logo.style.boxShadow =
            "0 0 45px rgba(0,217,255,.6)";

        setTimeout(() => {

            logo.style.boxShadow =
                "0 0 25px rgba(0,217,255,.35)";

        }, 800);

    }, 2000);

}



// =========================================
// CONSOLE MESSAGE
// =========================================

console.log(

    "%cDeepGuard AI",

    "color:#00d9ff;font-size:22px;font-weight:bold;"

);

console.log(

    "Enterprise Deepfake Detection Platform Loaded."

);