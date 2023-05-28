// expire time code
// rapido
const expireTimeRapido = document.getElementById('expire-time-rapido');

    const startingHoursRapido= 6 * 60 * 60;
    let timeRapido = startingHoursRapido;
    const oneDay = 60 * 60 * 24;
    const oneHour = 60 * 60;
    const oneMinute = 60;

    setInterval(updateCountDownRapido, 1000);

            function updateCountDownRapido() {
               
                let hours = Math.floor(timeRapido  / oneHour);
                let minutes = Math.floor( (timeRapido % oneHour)  / oneMinute);
                let seconds = Math.floor( (timeRapido % oneMinute));
                // seconds = seconds < 10 ? '0' + seconds : seconds;
                // hours = hours < 10 ? '0' + hours : hours;

                timeRapido--;
                timeRapido = timeRapido < 0 ? startingHoursRapido : timeRapido;
                expireTimeRapido.innerHTML = `${hours} hrs left`;
            }
            updateCountDownRapido();
            
// bitclass
const expireTimeBitclass = document.getElementById('expire-time-bitclass');

    const startingHoursBitclass= 3 * 60 * 60;
    let timeBitclass = startingHoursBitclass;

    setInterval(updateCountDownBitclass, 1000);

            function updateCountDownBitclass() {
               
                let hours = Math.floor(timeBitclass  / oneHour);
                let minutes = Math.floor( (timeBitclass % oneHour)  / oneMinute);
                let seconds = Math.floor( (timeBitclass % oneMinute));
                // seconds = seconds < 10 ? '0' + seconds : seconds;
                // hours = hours < 10 ? '0' + hours : hours;

                timeBitclass--;
                timeBitclass = timeBitclass < 0 ? startingHoursRapido : timeBitclass;
                expireTimeBitclass.innerHTML = `${hours} hrs left`;
            }
            updateCountDownBitclass();
// unlu
const expireTimeUnlu1 = document.getElementById('expire-time-unlu-1');

    const startingHoursUnlu1= 8 * 60 * 60;
    let timeUnlu1 = startingHoursUnlu1;

    setInterval(updateCountDownUnlu1, 1000);

            function updateCountDownUnlu1() {
               
                let hours = Math.floor(timeUnlu1  / oneHour);
                let minutes = Math.floor( (timeUnlu1 % oneHour)  / oneMinute);
                let seconds = Math.floor( (timeUnlu1 % oneMinute));
                // seconds = seconds < 10 ? '0' + seconds : seconds;
                // hours = hours < 10 ? '0' + hours : hours;

                timeUnlu1--;
                timeUnlu1 = timeUnlu1 < 0 ? startingHoursUnlu1 : timeUnlu1;
                expireTimeUnlu1.innerHTML = `${hours} hrs left`;
            }
            updateCountDownUnlu1();
const expireTimeUnlu2 = document.getElementById('expire-time-unlu-2');

    const startingHoursUnlu2= 8 * 60 * 60;
    let timeUnlu2 = startingHoursUnlu2;

    setInterval(updateCountDownUnlu2, 1000);

            function updateCountDownUnlu2() {
               
                let hours = Math.floor(timeUnlu2  / oneHour);
                let minutes = Math.floor( (timeUnlu2 % oneHour)  / oneMinute);
                let seconds = Math.floor( (timeUnlu2 % oneMinute));
                // seconds = seconds < 10 ? '0' + seconds : seconds;
                // hours = hours < 10 ? '0' + hours : hours;

                timeUnlu2--;
                timeUnlu2 = timeUnlu2 < 0 ? startingHoursUnlu2 : timeUnlu2;
                expireTimeUnlu2.innerHTML = `${hours} hrs left`;
            }
            updateCountDownUnlu2();

// bookchor
const expireTime1 = document.getElementById('expire-time-bookchor');

    const startingHours1= 5 * 60 * 60;
    let time1 = startingHours1;

    setInterval(updateCountDown1, 1000);

            function updateCountDown1() {
               
                let hours = Math.floor(time1  / oneHour);
                let minutes = Math.floor( (time1 % oneHour)  / oneMinute);
                let seconds = Math.floor( (time1 % oneMinute));

                time1--;
                time1 = time1 < 0 ? startingHoursUnlu1 : time1;
                expireTime1.innerHTML = `${hours} hrs left`;
            }
            updateCountDown1();
// woman company
const expireTime2 = document.getElementById('expire-time-womenc');

    const startingHours2= 13 * 60 * 60;
    let time2 = startingHours2;

    setInterval(updateCountDown2, 1000);

            function updateCountDown2() {
               
                let hours = Math.floor(time2  / oneHour);
                let minutes = Math.floor( (time2 % oneHour)  / oneMinute);
                let seconds = Math.floor( (time2 % oneMinute));

                time2--;
                time2 = time2 < 0 ? startingHoursUnlu2 : time2;
                expireTime2.innerHTML = `${hours} hrs left`;
            }
            updateCountDown2();
// Pea safe
const expireTime3 = document.getElementById('expire-time-peasafe');

    const startingHours3= 11 * 60 * 60;
    let time3 = startingHours3;

    setInterval(updateCountDown3, 1000);

            function updateCountDown3() {
               
                let hours = Math.floor(time3  / oneHour);
                let minutes = Math.floor( (time3 % oneHour)  / oneMinute);
                let seconds = Math.floor( (time3 % oneMinute));

                time3--;
                time3 = time3 < 0 ? startingHoursUnlu3 : time3;
                expireTime3.innerHTML = `${hours} hrs left`;
            }
            updateCountDown3();
// Pea safe
const expireTime4 = document.getElementById('expire-time-mypaperclip');

    const startingHours4= 7 * 60 * 60;
    let time4 = startingHours4;

    setInterval(updateCountDown4, 1000);

            function updateCountDown4() {
               
                let hours = Math.floor(time4  / oneHour);
                let minutes = Math.floor( (time4 % oneHour)  / oneMinute);
                let seconds = Math.floor( (time4 % oneMinute));

                time4--;
                time4 = time4 < 0 ? startingHoursUnlu4 : time4;
                expireTime4.innerHTML = `${hours} hrs left`;
            }
            updateCountDown4();
// propshop24
const expireTime5 = document.getElementById('expire-time-propshop24');

    const startingHours5= 5 * 60 * 60;
    let time5 = startingHours5;

    setInterval(updateCountDown5, 1000);

            function updateCountDown5() {
               
                let hours = Math.floor(time5  / oneHour);
                let minutes = Math.floor( (time5 % oneHour)  / oneMinute);
                let seconds = Math.floor( (time5 % oneMinute));

                time5--;
                time5 = time5 < 0 ? startingHoursUnlu5 : time5;
                expireTime5.innerHTML = `${hours} hrs left`;
            }
            updateCountDown5();
// mittihub
const expireTime6 = document.getElementById('expire-time-mittihub');

    const startingHours6= 9 * 60 * 60;
    let time6 = startingHours6;

    setInterval(updateCountDown6, 1000);

            function updateCountDown6() {
               
                let hours = Math.floor(time6  / oneHour);
                let minutes = Math.floor( (time6 % oneHour)  / oneMinute);
                let seconds = Math.floor( (time6 % oneMinute));

                time6--;
                time6 = time6 < 0 ? startingHoursUnlu6 : time6;
                expireTime6.innerHTML = `${hours} hrs left`;
            }
            updateCountDown6();
// avni
const expireTime7 = document.getElementById('expire-time-avni');

    const startingHours7= 3 * 60 * 60 * 24;
    let time7 = startingHours7;

    setInterval(updateCountDown7, 1000);

            function updateCountDown7() {
               
                let days = Math.floor(time7  / oneDay);
                let hours = Math.floor(time7 % oneDay  / oneHour);
                let minutes = Math.floor( (time7 % oneHour)  / oneMinute);
                let seconds = Math.floor( (time7 % oneMinute));

                time7--;
                time7 = time7 < 0 ? startingHoursUnlu7 : time7;
                expireTime7.innerHTML = `${days} days left`;
            }
            updateCountDown7();