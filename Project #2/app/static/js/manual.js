window.onload = function() {
const project_name = 'Чат-бот для центра развития карьеры и бренда работодателя Дом.рф'
let len = 0;
const title = document.getElementById('main-title')
let sleep_count = 0;

setInterval(() => {
    if (len >= project_name.length){
        return
    } else if (sleep_count == 0){
        title.innerHTML += project_name[len];
        len++;
    }
}, 70)

setTimeout(() => {
    document.getElementById("manual").scrollIntoView();

}, 6000)
};