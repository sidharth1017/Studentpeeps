
function expireHours(brand, timer) {
    var date = new Date();
    var hrs = date.getHours();
    if (timer == 2) {
        if (hrs % 2 == 0) {
            brand.textContent = 2 + " hours left ";
        }
        if (hrs % 2 == 1) {
            brand.textContent = 1 + " hour left ";
        }
    }
    if (timer == 3) {
        if (hrs <= 23 && hrs >= 21) {
            brand.textContent = 24 - hrs + " hours left ";
        }
        if (hrs <= 20 && hrs >= 18) {
            brand.textContent = 21 - hrs + " hours left ";
        }
        if (hrs <= 17 && hrs >= 15) {
            brand.textContent = 18 - hrs + " hours left ";
        }
        if (hrs <= 14 && hrs >= 12) {
            brand.textContent = 15 - hrs + " hours left ";
        }
        if (hrs <= 11 && hrs >= 9) {
            brand.textContent = 12 - hrs + " hours left ";
        }
        if (hrs <= 8 && hrs >= 6) {
            brand.textContent = 9 - hrs + " hours left ";
        }
        if (hrs <= 5 && hrs >= 3) {
            brand.textContent = 6 - hrs + " hours left ";
        }
        if (hrs <= 2 && hrs >= 0) {
            brand.textContent = 3 - hrs + " hours left ";
        }
    }
    if (timer == 6) {
        if (hrs <= 4 && hrs >= 0) {
            brand.textContent = 5 - hrs + " hours left ";
        }
        if (hrs == 23) {
            brand.textContent = 28 - hrs + " hours left ";
        }
        if (hrs <= 22 && hrs >= 17) {
            brand.textContent = 23 - hrs + " hours left ";
        }
        if (hrs <= 16 && hrs >= 11) {
            brand.textContent = 17 - hrs + " hours left ";
        }
        if (hrs <= 10 && hrs >= 5) {
            brand.textContent = 11 - hrs + " hours left ";
        }
    }
    if (timer == 9) {
        if (hrs <= 26 && hrs >= 18) {
            brand.textContent = 27 - hrs + " hours left ";
        }
        else if (hrs <= 17 && hrs >= 9) {
            brand.textContent = 18 - hrs + " hours left ";
        }
        else {
            brand.parentElement.style.display = "none";
        }
    }
    if (timer == 12) {
        if (hrs >= 0 && hrs <= 5) {
            brand.textContent = 6 - hrs + " hours left ";
        }
        if ((hrs <= 23 && hrs >= 18)) {
            brand.textContent = 29 - hrs + " hours left ";
        }
        if (hrs <= 17 && hrs >= 6) {
            brand.textContent = 18 - hrs + " hours left ";
        }
    }
    if (timer == 15) {
        if (hrs <= 35 && hrs >= 20) {
            brand.textContent = 36 - hrs + " hours left ";
        }
        if (hrs <= 20 && hrs >= 5) {
            brand.textContent = 21 - hrs + " hours left ";
        }
        else {
            brand.parentElement.style.display = "none";
        }
    }
    if (timer == 18) {
        var hrs = hrs - 2;
        if (hrs <= 20 && hrs >= 3) {
            brand.textContent = 21 - hrs + " hours left ";
        }
        else {
            brand.parentElement.style.display = "none";
        }
    }
}
function expireDays(brand, timer) {
    var date = new Date();
    var day = date.getDay();
    if (timer == 2) {
        if (day % 2 == 0) {
            brand.textContent = 2 + " days left ";
        }
        if (day % 2 == 1) {
            brand.textContent = 1 + " day left ";
        }
    }
}

//rapido
const expireTimeRapido = document.getElementById('expire-time-rapido');
if (expireTimeRapido !== null)
expireHours(expireTimeRapido, 2);


//peesafe
const expireTimePeesafe = document.getElementById('expire-time-peasafe');
if (expireTimePeesafe !== null)
expireHours(expireTimePeesafe, 12);


//bitclass
const expireTimeBitclass = document.getElementById('expire-time-bitclass');
if (expireTimeBitclass !== null)
expireHours(expireTimeBitclass, 6);


//bookchor
const expireTimeBookchor = document.getElementById('expire-time-bookchor');
if (expireTimeBookchor !== null)
expireHours(expireTimeBookchor, 3);


//unlu2
const expireTimeUnlu2 = document.getElementById('expire-time-unlu-2');
if (expireTimeUnlu2 !== null)
expireHours(expireTimeUnlu2, 9);


//avni
const expireTimeAvni = document.getElementById('expire-time-avni');
if (expireTimeAvni !== null)
expireDays(expireTimeAvni, 2);


//unlu1
const expireTimeUnlu1 = document.getElementById('expire-time-unlu-1');
if (expireTimeUnlu1 !== null)
expireHours(expireTimeUnlu1, 9);


//womenc
const expireTimeWomenc = document.getElementById('expire-time-womenc');
if (expireTimeWomenc !== null)
expireHours(expireTimeWomenc, 15);


//mypaperclip
const expireTimeMypaperclip = document.getElementById('expire-time-mypaperclip');
if (expireTimeMypaperclip !== null)
expireHours(expireTimeMypaperclip, 18);


//mittihub
const expireTimeMittihub = document.getElementById('expire-time-mittihub');
if (expireTimeMittihub !== null)
expireHours(expireTimeMittihub, 2);


//peesafe
const expireTimePropshop24 = document.getElementById('expire-time-propshop24');
if (expireTimePropshop24 !== null)
expireHours(expireTimePropshop24, 12);

