// auto_refresh.js

/**
 * enableAutoRefresh(seconds) - Refreshes the page every {seconds} seconds.
 * @param {number} seconds - Number of seconds between refreshes.
 */
function enableAutoRefresh(seconds) {
    setTimeout(function() {
        window.location.reload(true);
    }, seconds * 1000);
}
