/* adjusts correctly Gemini-Sparkle SVG mask on chat div */
(function(size = 100) {

    var gemini_sparkle_mask = document.getElementById("gemini-sparkle-mask-chat");
    var gs_mask_svg = gemini_sparkle_mask.children[0];

    gs_mask_svg.setAttribute('height', `${size}px`);
    gs_mask_svg.setAttribute('width', `${size}px`);
})();



var old_platform = null
window.onload = function() {
    screenWidth = window.innerWidth;
    old_platform = screenWidth <= 800 ? "mobile" : "desktop";
}

//window elements resize optimization
//Desktop-Mobile bound
window.onresize = function() {
    screenWidth = window.innerWidth;
    var platform = screenWidth <= 800 ? "mobile" : "desktop" 
    
    document.getElementById("models").classList.add("hidden");
}
