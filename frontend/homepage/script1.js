// =============================
// PASSWORD TOGGLE
// =============================

const password = document.getElementById("password");
const toggle = document.getElementById("togglePassword");

if (password && toggle) {

    toggle.addEventListener("click", () => {

        if (password.type === "password") {

            password.type = "text";

            toggle.classList.replace(
                "fa-eye",
                "fa-eye-slash"
            );

        }

        else {

            password.type = "password";

            toggle.classList.replace(
                "fa-eye-slash",
                "fa-eye"
            );

        }

    });

}


// =============================
// LOGIN BUTTON
// =============================

const form = document.getElementById("loginForm");

if (form) {

    form.addEventListener("submit", (e) => {

        e.preventDefault();

        const button =
        document.querySelector(".login-btn");

        const original =
        button.innerHTML;

        button.disabled = true;

        button.innerHTML =
        '<i class="fa-solid fa-spinner fa-spin"></i> Signing In...';

        setTimeout(() => {

            button.innerHTML = original;

            button.disabled = false;

            alert(
                "Backend authentication will be connected here."
            );

        }, 1800);

    });

}


// =============================
// PAGE LOAD ANIMATION
// =============================

window.addEventListener("load", () => {

    document.body.style.opacity = "0";

    setTimeout(() => {

        document.body.style.transition =
        "opacity 0.8s ease";

        document.body.style.opacity = "1";

    }, 100);

});


// =============================
// HERO FADE-IN
// =============================

const hero =
document.querySelector(".hero");

const login =
document.querySelector(".login-card");

if(hero && login){

    hero.animate(

        [

            {
                opacity:0,
                transform:"translateX(-40px)"
            },

            {
                opacity:1,
                transform:"translateX(0)"
            }

        ],

        {

            duration:900,

            easing:"ease-out",

            fill:"forwards"

        }

    );


    login.animate(

        [

            {
                opacity:0,
                transform:"translateX(40px)"
            },

            {
                opacity:1,
                transform:"translateX(0)"
            }

        ],

        {

            duration:900,

            easing:"ease-out",

            fill:"forwards"

        }

    );

}


// =============================
// INPUT GLOW EFFECT
// =============================

const inputs =
document.querySelectorAll(".input-box input");

inputs.forEach((input)=>{

    input.addEventListener("focus",()=>{

        input.parentElement.style.transform =
        "scale(1.02)";

    });

    input.addEventListener("blur",()=>{

        input.parentElement.style.transform =
        "scale(1)";

    });

});


// =============================
// BUTTON HOVER GLOW
// =============================

const loginButton =
document.querySelector(".login-btn");

if(loginButton){

    loginButton.addEventListener("mouseenter",()=>{

        loginButton.style.boxShadow =
        "0 15px 35px rgba(0,217,255,.45)";

    });

    loginButton.addEventListener("mouseleave",()=>{

        loginButton.style.boxShadow =
        "none";

    });

}


// =============================
// OPTIONAL CONSOLE MESSAGE
// =============================

console.log(
"%cDeepGuard AI",
"color:#00d9ff;font-size:22px;font-weight:bold;"
);

console.log(
"Frontend initialized successfully."
);