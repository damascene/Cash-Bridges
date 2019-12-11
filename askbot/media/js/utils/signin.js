const signInForm = document.querySelector("#signin-form");
signInForm.addEventListener("submit", SignInFormSaveTokenSubmitHandler);

function SignInFormSaveTokenSubmitHandler(event){
    event.preventDefault();
    const form = document.querySelector("#signin-form");
    const message = document.querySelector("#id_password").value;
    crypto.subtle.digest('SHA-512', new TextEncoder().encode(message)).then(
        (hashBuffer)=>{
            let hashArray = Array.from(new Uint8Array(hashBuffer));
            let hashHex = hashArray.map(
                b => b.toString(16).padStart(2, '0')
            ).join('');
            window.localStorage.setItem('token', hashHex);
        }
    );
    if(form){
        form.submit();
    }

}
