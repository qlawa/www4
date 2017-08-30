/**
 * Created by bl on 27.08.17.
 */

let myHost = 'http://127.0.0.1:8000';
//window.location.host;
// console.log(myHost)


function login() {
    logowanie(true)
}

function logout() {
    logowanie(false)
}


function logowanie(czyLogowac) {

    let login = '';
    let haslo = '';
    console.log(login);
    console.log(haslo);

    let data = {};
    if (czyLogowac === true) {
        login = document.getElementById('login').value;
        haslo = document.getElementById('password').value;
        data = {'uzytkownik': login, 'haslo': haslo, 'czynnosc': 'login'}
    }
    else if (czyLogowac === false) {
        login = sessionStorage.getItem('uzytkownik');
        haslo = sessionStorage.getItem('haslo');
        data = {'uzytkownik': login, 'czynnosc': 'logout'}
    }

    console.log(JSON.stringify(data));
    console.log(data);
    $.ajax({
        url: myHost + '/api/login/',
        type: 'POST',
        dataType: 'json',
        data: JSON.stringify(data),
        //data: JSON.stringify(formData),
        success: function (result) {
            console.log(result);
            if (czyLogowac === false) {
                sessionStorage.removeItem('zalogowano');
                sessionStorage.removeItem('uzytkownik');
                sessionStorage.removeItem('haslo');
                window.location.href = myHost;
            } else {
                sessionStorage.setItem('zalogowano', true);
                sessionStorage.setItem('uzytkownik', login);
                sessionStorage.setItem('haslo', haslo);
                window.location.href = myHost;
            }
        },
        error: function (error) {
            console.log(error);
            let text = error.responseText.substr(2, error.responseText.length-4);
                console.log(text);
            alert(text);
        }
    });
    return false;
}

$.ajaxSetup({
    beforeSend: function(xhr) {
        xhr.setRequestHeader('x-my-custom-header', 'some value');
    }
});

$(document).ready(function () {
    $('#formularzLogowania').submit(function () {
        logowanie(true);
        return false;
    });
});

