
let menuBtn = document.getElementsByClassName("menu-button")[0];
let navSlide = document.getElementsByClassName("menu-nav")[0];
let counterPressButton = 0;


menuBtn.addEventListener('click', onClick);

function onClick(){

    if(counterPressButton >= 1){
        counterPressButton = 0;
        navSlide.classList.remove('is--open');
        document.body.removeEventListener('click',onClickBody);
        return;
    }
    document.body.addEventListener('click',onClickBody);
    navSlide.classList.add('is--open');
    counterPressButton += 1;

}

function onClickBody(e){
    if(
        navSlide.contains(e.target) ||
        menuBtn.contains(e.target)
    ){
        return;
    }

    navSlide.classList.remove('is--open');
    counterPressButton = 0;
    document.body.removeEventListener('click',onClickBody);
}

function showForm(){
    document.getElementById('configForm').style.display = "block";
}

function hideForm(){
    document.getElementById('configForm').style.display = "none";
}

$(document).on('submit','#configForm',function(e){
    e.preventDefault();
    city = $('#inputCity').val();
    mode = $('#mode-selection').val();
    console.log(city);
    console.log(mode);
    $.ajax({
        type:'POST',
        url: "http://127.0.0.1:8000/accounts/profile-admin/",
        dataType: "json",
        async: false,
        data:JSON.stringify(
        {
            city: city,
            mode: mode,
        }),
        headers: {
            "X-Requested-For": "ConfigMode",
            "X-Requested-With": "XMLHttpRequest",
            "X-CSRFToken": getCookie("csrftoken"),
        },
        success:function(){
              alert('Saved');
                }
    });
});