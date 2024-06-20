screenHeight = window.innerHeight;
var textInput = document.getElementById("text-input")

function resizeOptimization() {
    if (this.clientHeight < screenHeight * 0.5) {
        this.style = ""
    }
    else {
        this.style = "overflow-y: scroll !important;"
    }
}

textInput.addEventListener("input", resizeOptimization)