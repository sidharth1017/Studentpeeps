function copyElementText(id) {
    var text = document.getElementById(id).innerText;
    var elem = document.createElement("textarea");
    document.body.appendChild(elem);
    elem.value = text;
    elem.select();
    document.execCommand("copy");
    document.body.removeChild(elem);

}

window.onload = function () {
    window.scroll({
        top: 300, 
        left: 0, 
        behavior: 'smooth'
      });
    copybtns = document.querySelectorAll(".copy-btn");
    copybtnsArray = Array.from(copybtns);
    copybtnsArray.forEach(element => {
        element.addEventListener("click", () => {
            if (!element.classList.contains('active') && !element.classList.contains('copied')) {
                element.classList.add("active");
                element.classList.add("copy");
                setTimeout(() => {
                    element.classList.remove("active");
                    element.classList.remove("copy");
                    element.classList.add("copied");
                }, 1500);
            }
        });
    });
    document.querySelector(".wrapper").addEventListener("click", overlayDisplay);
}

var counter = 0;
setTimeout(() => {
    document.querySelector("body").classList.add("active");
    document.querySelector(".wrapper").classList.add("active");
}, 10);

document.addEventListener("click", () => {
    if (counter == 0) {
        document.querySelector("body").classList.remove("active");
        document.querySelector(".wrapper").classList.remove("active");
        document.querySelector(".wrapper").removeEventListener("click", overlayDisplay);
    }
    counter--;
});

function overlayDisplay() {
    ++counter;
};
