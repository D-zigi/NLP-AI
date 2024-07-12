var old_platform = null

window.onload = function() {
    screenWidth = window.innerWidth;
    old_platform = screenWidth <= 800 ? "mobile" : "desktop";
    
    backgroundGeminiSparkle();
}

window.onresize = function() {
    screenWidth = window.innerWidth;
    var platform = screenWidth <= 800 ? "mobile" : "desktop";
    
    Menu(document.getElementById("selected-model"), "models", true);
}
