screenHeight = window.innerHeight;

/**
 * checks `element` height if above `max_height`
 * that is 0-1 which is the % from screen height
 * changes the overflow accordingly
 * @param {HTMLElement} element - optimized element
 * @param {Number} max_height - max height 0-1
 */
function resizeOptimization(element, max_height) {
    if (element.clientHeight < screenHeight * max_height) {
        element.style = "";
    }
    else {
        element.style = "overflow-y: scroll !important;";
    }
}

/** 
 * Scrolls to the bottom of some element
 * @param {HTMLElement} element - scrolled element
*/
function scrollToBottom(element) {
    element.scrollTop = element.scrollHeight;
}
/** 
 * Scrolls to the top of some element
 * @param {HTMLElement} element - scrolled element
*/
function scrollToTop(element) {
    element.scrollTop = 0;
}

/**
 * Shows/Hides menu accordingly when clicked on toggle button and outside of the menu
 * @param {HTMLElement} button - clicked button
 * @param {String} menu_id - menu id
 */
function Menu(button, menu_id, consistent = false) {
    let menu = document.getElementById(menu_id);

    const visible = !menu.classList.contains("hidden");

    if ((!consistent && !visible) || (consistent && visible)) {
        var rect = button.getBoundingClientRect();
    
        menu.style.top = `${rect.top + button.offsetHeight}px`;
        menu.style.left = `${rect.left}px`;
    
        button.classList.add("active");
        menu.classList.remove("hidden");
        document.addEventListener("mousedown", (e) => {
            if (!menu.contains(e.target) && !button.contains(e.target)) {
                menu.classList.add("hidden");
                button.classList.remove("active");
            }
        });
    }

    else if ((!consistent && visible) || (consistent && !visible)) {
        menu.classList.add("hidden");
        button.classList.remove("active");
        document.removeEventListener("mousedown", (e) => {
            if (!menu.contains(e.target) && e.target != button) {
                menu.classList.add("hidden");
                button.classList.remove("active");
            }
        });
    }

}


/**
 * Appends custom alert to a html body
 * @param {String} message 
 * @param {String} color 
 */
function customAlert(message, style_class) {
    var alert = document.createElement('div');
    alert.classList = 'alert ' + style_class;

    var alert_message = document.createElement('span');
    alert_message.classList = 'alert_message';
    alert_message.textContent = message;

    alert.appendChild(alert_message)
    document.body.appendChild(alert);
    
    setTimeout(() => {
        document.body.removeChild(alert);
    }, 5000);
}

/**
 * calls custom alert in red color and error message
 * @param {String} error_message
 * @param {Number} error_code
 */
function errorAlert(error_message, error_code) {
    console.log("Error")
    console.error(`Error ${error_code}:${error_message}`);
    customAlert(error_message, 'error');
}


/**
 * changes document class cotaining root variables of colors
 */
function changeTheme() {
    document.documentElement.classList.toggle("light-theme");
}

/**
 * adjusts correctly Gemini-Sparkle SVG mask on chat div
 * @param {Number} size - sparkle size diameter
 */
function backgroundGeminiSparkle(size = 100) {

    var gemini_sparkle_mask = document.getElementById("gemini-sparkle-mask-chat");
    var gs_mask_svg = gemini_sparkle_mask.children[0];

    gs_mask_svg.setAttribute('height', `${size}px`);
    gs_mask_svg.setAttribute('width', `${size}px`);
}