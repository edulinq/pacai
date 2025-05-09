"use strict";

let fps = 10;
let pressedKeys = undefined;
let intervalID = undefined;

function main() {
    registerKeys();
    init();
}

function registerKeys() {
    pressedKeys = [];

    window.addEventListener("keydown", function(event) {
        pressedKeys.push(event.key);
    });
}

function init() {
    makeRequest('/api/init', {})
        .then(function(body) {
            document.title = body.title;

            fps = body.fps;

            // Update twice an FPS period (since we are polling and updates are not pushed).
            let delayMS = 1.0 / fps * 1000.0 / 2.0;

            // Update the UI according to the FPS from the server.
            intervalID = setInterval(update, delayMS);
        })
    ;
}

function close() {
    if (intervalID) {
        clearInterval(intervalID);
        intervalID = undefined;
    }
}

function update() {
    let oldKeys = pressedKeys;
    pressedKeys = [];

    let data = {
        'keys': oldKeys,
    }

    makeRequest('/api/update', data)
        .then(function(body) {
            document.querySelector('.page .image-area img').src = body.image_url;

            // Check if the game has ended.
            if (body.state.game_over) {
                close();
                console.log("Game Over");
            }
        })
    ;
}

function makeRequest(url, body) {
    let data = {
        'method': 'POST',
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': JSON.stringify(body),
    }

    return fetch(url, data).then(apiSuccess, apiFailure);
}

async function apiSuccess(response) {
    let body = await response.json()
    return Promise.resolve(body);
}

async function apiFailure(response) {
    console.error("Failed to make API request.");
    console.error(response);

    close();

    return Promise.reject(response);
}

document.addEventListener("DOMContentLoaded", main);
