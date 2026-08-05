const password =
document.getElementById("password");


const toggle =
document.getElementById("togglePassword");


toggle.addEventListener(
"click",
()=>{


    if(password.type==="password"){

        password.type="text";

        toggle.classList.remove("fa-eye");

        toggle.classList.add("fa-eye-slash");

    }

    else{

        password.type="password";

        toggle.classList.remove("fa-eye-slash");

        toggle.classList.add("fa-eye");

    }


});



document
.getElementById("loginForm")
.addEventListener(
"submit",
(e)=>{

    e.preventDefault();

    alert(
    "Login system will be connected to backend authentication."
    );

});