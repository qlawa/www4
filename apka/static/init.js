/**
 * Created by bl on 23.08.17.
 */
//let myHost = 'http://127.0.0.1:8000/';

function getDataFromServer(url, callback, type='GET') {
    console.log(url);

    $.ajax({
        url: url,
        type: type,
        dataType: 'json',
        success: function(result) {
            let data = result;
            console.log('wyniki:');
            console.log(data);
            callback(data);
        },
        error: function(error) {
            console.log(error);
        },
    });
}

function updateLoginPanel() {
    let html = '';
    if (sessionStorage.getItem('zalogowano') === "true") {
        html = 'Jesteś zalogowany jako ' + sessionStorage.getItem('uzytkownik') +
            '. <a href="#" id="logoutLink">Wyloguj</a>'
    }
    else {
        html = '<a href="login/" id="loginLink">Zaloguj</a>'
    }
    $("#loginPanel").html(html);

}
function render(data) {
    console.log(data);
    if (data.hasOwnProperty('dane')) {
        let dane = data['dane'];
        //console.log(dane);
        if (dane.hasOwnProperty('zasieg')) {
            if (dane['zasieg'] === 'KRAJ') {
                changeHtml('Polska', dane['wynik'], dane['statystyki'], null, 'KRAJ');
                showMap(true);
                hideObwody();
                showSearchBox()
            }
            else if (dane['zasieg'] === 'WOJEWODZTWO') {
                changeHtml(dane['id_terenu'], dane['wynik'], dane['statystyki'], data['odnosniki'], 'WOJEWODZTWO');
                showMap(false);
                hideObwody();
                showSearchBox()
            }
            else if (dane['zasieg'] === 'OKREG') {
                changeHtml(dane['id_terenu'], dane['wynik'], dane['statystyki'], data['odnosniki'], 'OKREG');
                showMap(false);
                hideObwody();
                showSearchBox()
            }
            else if (dane['zasieg'] === 'GMINA') {
                changeHtml(dane['id_terenu'], dane['wynik'], dane['statystyki'], null, 'GMINA');
                showObwody(data['obwody']);
                showMap(false);
                showSearchBox()
            }
            else if (dane['zasieg'] === 'OBWOD') {
                //edycja
                if (canIEdit()) {
                    hideSearchBox();
                    prepareForm(data);
                }
                else {
                    alert("Edycja dostępna jest tylko dla zalogowanych użytkowników.")
                }
            }
        }
    }
    updateLoginPanel();
}

function hideSearchBox() {
    $(".wyszukiwarkaGmin").hide();
}

function showSearchBox() {
    $(".wyszukiwarkaGmin").show();
}

function canIEdit() {
    return sessionStorage.getItem('zalogowano') === 'true';

}

function prepareForm(data) {
    console.log(data);
    statystyki_form = data['dane']['statystyki'];
    data = data['wyniki'];

    console.log(statystyki_form);
    console.log(data);

    if (data[0].hasOwnProperty('id') && data[0].hasOwnProperty('liczba') && data[0].hasOwnProperty('kandydat')
            && data[0].hasOwnProperty('obwod')) {
        let html = '<tbody>';
        for (let i=0; i<data.length; i++) {
            let wynik = data[i];
            html += '<form class="formularzWynik"><tr><td>' + getCandidateName(wynik['kandydat']) + '</td>' +
                '<td><input class="wynikNumer" type="number" min="0" name="liczba" value="' + wynik['liczba'] + '" class="wynikForm" id="' + wynik['id'] + '"></td>' +
                '<td><input type="hidden" name="kandydat" value="' + wynik['kandydat'] + '"></td>' +
                '<td><input type="hidden" name="id" value="' + wynik['id'] + '"></td>' +
                '<td><input class="obwodInput" type="hidden" name="obwod" value="' + wynik['obwod'] + '"></td></tr></form>';
        }
        html += '<tr><td><input type="submit" value="Zapisz"></tr></td></tbody>';
        console.log(html);
        $(".wierszeFormularza").html(html);
        edycjaModeOn(true);
    }
}

function hideGminy() {
    $("#listaGmin").hide();
}

function showGminy(data) {
    let html = '';
    for (let i=0; i< data.length; i++) {
        html += '<li><a href="#" class="odnosnikGminaZSzukania" id=' + data[i]['numer'] + '>' + data[i]['nazwa'] + '</a></li>';
    }
    $("#listaGmin").html(html).show();
    dopiszGminy(data);
}

function dopiszGminy(data) {
    gminy = gminy.concat(data);
}

function searchGmina() {
    let gmina = document.getElementsByName("szukanaGmina")[0];
    let wartosc = gmina.value;
    gmina.value = '';

    $.ajax({
        url: myHost + '/api/szukaj/' + wartosc,
        type: "POST",
        dataType: 'json',
        success: function (result) {
            console.log(result);
            showGminy(result);
        },
        error: function (error) {
            console.log(error);
        },
    });
    return false;
}


function getStatystyka(etykieta) {
    for (let i=0; i<statystyki_form.length; i++) {
        if (statystyki_form[i]['etykieta'] === etykieta) {
            return Number(statystyki_form[i]['liczba'])
        }
    }
}


function validateForm() {
    let form = $(".wynikNumer");
    let suma = 0;
    for (let i=0; i<form.length; i++) {
        suma += Number(form[i].value);
        console.log(suma);
    }
    let niewazne = getStatystyka("Głosy nieważne");
    let karty = getStatystyka("Wydane karty");
    console.log(niewazne);
    console.log(karty);
    if (niewazne + suma > karty) {
        alert(`Suma głosów nieważnych i głosów oddanych na wszystkich kandydatów (${niewazne + suma}) jest większa niż liczba wydanych kart (${karty}).`);
        return false;
    }
    return true;
}


function sendForm() {

    let formData = $("#formularz").serializeArray();

    console.log(formData);

    let obwod = $(".obwodInput")[0].value;
    formData = JSON.stringify(formData);
    console.log(formData);
    if (obwod !== undefined) {
        $.ajax({
            url: myHost + '/api/obwod/' + obwod,
            type: "POST",
            data: formData,
            dataType: 'json',
            success: function () {
                getDataFromServer(myHost + '/api/gmina/' + gminaID, render)
            },
            error: function (error) {
                console.log(error);
                let text = error.responseText.substr(2, error.responseText.length-4);
                console.log(text);
                alert(text);
            },
        });
    }
    return false;
}


function showObwody(obwody) {
    console.log(obwody);
    //wyniki
    let html = '<thead><th>Nr obwodu</th>';
    for (let k=0; k<kandydaci.length; k++) {
        html+='<th>' + getCandidateName(kandydaci[k]['id']) + '</th>';
    }
    html += '</thead><tbody>';
    let id = 1;
    for (let i=0; i<obwody.length; i++) {
        let idNumber = obwody[i]['id_terenu'];
        html += '<tr><td class="odnosnikObwod" id="'+ idNumber +'">'+ id +'</td>';
        for (let k=0; k<kandydaci.length; k++) {
            html+='<td>' + obwody[i]['wynik'][k]['wynik'] + '</td>';
        }
        html += '<td>';
        id++;
    }
    html += '</tbody>';
    console.log(html);
    $(".wynikiObwody").html(html);

    //statystyki
    html = '<thead><th>Nr obwodu</th>';
    let statystyki = obwody[0]['statystyki'];
    if (statystyki !== undefined) {
        for (let s = 0; s < statystyki.length; s++) {
            html += '<th>' + statystyki[s]['etykieta'] +'</th>';
        }
        html += '</thead><tbody>';
        let id=1;
        for (let i = 0; i < obwody.length; i++) {
            html += '<tr><td>' + id + '</td>';
            id++;
            for (let s = 0; s < statystyki.length; s++) {
                html += '<td>' + obwody[i]['statystyki'][s]['liczba'] + '</td>';
            }
            html += '<td>'
        }
    } else {
        html = '';
    }
    $(".statystykiObwody").html(html);

    $(".obwody").show();
}

function hideObwody() {
    $(".obwody").hide();
}

function edycjaModeOn(isOn) {
    if (isOn === true) {
        $(".wynikiWyborow").hide();
        $(".edycja").show();
    }
    else if (isOn === false) {
        $(".wynikiWyborow").show();
        $(".edycja").hide();
    }
}

function changeHtml(title, results, stats, links, zasieg) {
    changeTitle(title, zasieg);
    changeResults(results, stats[3]['liczba']);    //głosy ważne
    changeStats(stats);
    changeLinks(links, zasieg);
    showMap(false);
    edycjaModeOn(false);
    hideGminy();
}

function changeTitle(title, zasieg) {
    let h1Poland = $("#podtytulPolska");
    let h1Wojewodztwo = $("#podtytulWojewodztwo");
    let h1Okreg = $("#podtytulOkreg");
    let h1Gmina = $("#podtytulGmina");

    if (zasieg === 'KRAJ') {
        h1Poland.html('Polska');
        h1Wojewodztwo.hide();
        h1Okreg.hide();
        h1Gmina.hide();
    }
    else if (zasieg === 'WOJEWODZTWO') {
        h1Poland.html('<a href="#">Polska</a>');
        document.getElementById('podtytulPolska').onclick = function() {
            click('kraj/');
        };
        console.log(title);
        h1Wojewodztwo.html('<a href="#" >Wojewodztwo '+ wojewodztwa[title] +'</a>');
        document.getElementById('podtytulWojewodztwo').onclick = function() {
            click('wojewodztwo/'+title);
        };
        h1Wojewodztwo.show();
        h1Okreg.hide();
        h1Gmina.hide();
    }
    else if (zasieg === 'OKREG') {
        h1Okreg.html('<a href="#" >Okreg '+ title +'</a>');
        document.getElementById('podtytulOkreg').onclick = function() {
            click('okreg/'+title);
        };
        h1Okreg.show();
        h1Gmina.hide();
    }
    else if (zasieg === 'GMINA') {
        //$("#idGminy").html();
        //document.getElementById('idGminy').innerHTML = title;
        gminaID = title;
        h1Gmina.html('<a href="#" >Gmina '+ getGminaName(title) +'</a>');
        document.getElementById('podtytulGmina').onclick = function() {
            click('gmina/'+title);
        };
        h1Gmina.show();
    }
    else if (zasieg === 'GMINA_Z_SZUKANIA') {
        h1Okreg.hide();
        h1Wojewodztwo.hide();
        h1Poland.html('<a href="#">Polska</a>');
        document.getElementById('podtytulPolska').onclick = function() {
            click('kraj/');
        };
    }
}

function changeResults(results, sum) {
    let first = 0;
    let second = 0;
    for (let i = 0; i < results.length; i++) {
        if (results[i]['wynik'] > first) {
            second = first;
            first = results[i]['wynik'];
        }
        else if (results[i]['wynik'] > second) {
            second = results[i]['wynik'];
        }
    }

    let html = '<thead><th>Kandydaci</th><th>Wynik</th><th>%</th><th class="pasek"></th></thead><tbody>';
    for (let i = 0; i < results.length; i++) {
        let percentage = results[i]['wynik']/sum * 100;
        let divLength = percentage.toFixed(0);
        percentage = percentage.toFixed(2);
        html += '<tr><td>' + getCandidateName(results[i]['kandydat']) +'</td>' +
                '<td>' + results[i]['wynik'] + '</td>' +
                '<td>' + percentage + '</td><td class="pasek">';

        if (results[i]['wynik'] === first) {
            html += '<div class="pierwszy dlugosc_paska-'+ divLength;
        }
        else if (results[i]['wynik'] === second) {
            html += '<div class="drugi dlugosc_paska-'+ divLength;
        }
        else {
            html += '<div class="reszta dlugosc_paska-'+ divLength;
        }
        html += '"></div></td></tr>';
    }
    html += '</tbody>';
    document.getElementsByClassName('tabela_wynikow')[0].innerHTML = html;
}

function changeStats(stats) {
    let html = '<tbody>';
    for (let i=0; i<stats.length; i++) {
        html += '<tr><td>' + stats[i]['etykieta'] + '</td><td>'+stats[i]['liczba']+'</td><tr>';
    }
    html +='</tbody>';
    document.getElementsByClassName('tabela_statystyk')[0].innerHTML = html;
}

function changeLinks(links, zasieg) {
    if (links === null) {
        document.getElementsByClassName('linki')[0].innerHTML = '';
    } else {
        let html = '<ul>';
        if (zasieg === 'WOJEWODZTWO') {
            for (let i = 0; i < links.length; i++) {
                html += '<li class="odnosnikOkreg" id="' + links[i]['numer'] + '"><a href="#">Okreg ' + links[i]['numer'] + '</a></li>';
            }
        } else if (zasieg === 'OKREG') {
            for (let i = 0; i < links.length; i++) {
                html += '<li class="odnosnikGmina" id="' + links[i]['numer'] + '"><a href="#">Gmina ' + links[i]['nazwa'] + '</a></li>';
            }
            console.log(links);
            gminy = links;
        }
        html += '</ul>';

        console.log(html);
        document.getElementsByClassName('linki')[0].innerHTML = html;
    }
}

function showMap(visible) {
    if (visible === true) {
        $(".mapa").show();
    }
    else {
        $(".mapa").hide();
    }
}

function click(url) {
    getDataFromServer(myHost + '/api/' + url, render);
    return false;
}

function getCandidateName(id) {
    for (let i=0; i<kandydaci.length; i++) {
        if (kandydaci[i]['id'] === id) {
            return (kandydaci[i]['imie'] + ' ' + kandydaci[i]['nazwisko'])
        }
    }
    return id
}

function getGminaName(id) {
    for (let i=0; i< gminy.length; i++) {
        if (gminy[i]['numer'] === id) {
            return gminy[i]['nazwa']
        }
    }
    return id
}

function getCandidatesDataFromServer() {
    $.ajax({
        url: myHost + '/api/kandydaci/',
        type: 'GET',
        dataType: 'json',
        success: function(result) {
            kandydaci = result;
            console.log("Kandydaci: " + kandydaci);

            for (let i=0; i < kandydaci.length; i++) {
                console.log(kandydaci[i]);
            }
        },
        error: function(error) {
            console.log(error);
        },
    });
}

function makeLinksWork() {
    let body = $('body');
    body.delegate('.odnosnikOkreg', 'click', function () {
        click('okreg/' + this.id);
        return false;
    });
    body.delegate('.odnosnikGmina', 'click', function () {
        click('gmina/' + this.id);
        return false;
    });
    body.delegate('.odnosnikGminaZSzukania', 'click', function () {
        click('gmina/' + this.id);
        changeTitle('', 'GMINA_Z_SZUKANIA');
        return false;
    });
    body.delegate('.odnosnikObwod', 'click', function () {
        //
        getDataFromServer(myHost + '/api/obwod/' + this.id, render);
        return false;
    });
    $('#formularz').submit(function () {
        if (validateForm()) {
            sendForm();
        }
        return false;
    });
    $('#formularzDoGmin').submit(function () {
        searchGmina();
        return false;
    });
    body.delegate('#logoutLink', 'click', function () {
        logout();
        return false;
    });
}

let kandydaci = null;
let wojewodztwa = {
    2: 'Dolnośląskie',
    4: 'Kujawsko-pomorskie',
    6: 'Lubelskie',
    8: 'Lubuskie',
    10: 'Łódzkie',
    12: 'Małopolskie',
    14: 'Mazowieckie',
    16: 'Opolskie',
    18: 'Podkarpackie',
    20: 'Podlaskie',
    22: 'Pomorskie',
    24: 'Śląskie',
    26: 'Świętokrzyskie',
    28: 'Warmińsko-mazurskie',
    30: 'Wielkopolskie',
    32: 'Zachodniopomorskie',
};
let gminy = [];
let gminaID = 0;
let statystyki_form = [];

$(document).ready(function () {
    getCandidatesDataFromServer();
    makeLinksWork();
    getDataFromServer(myHost + '/api/kraj/', render);
});

