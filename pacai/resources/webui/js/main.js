"use strict";

let fps = 10;

function main() {
    init();
}

function init() {
    makeRequest('/api/init', {})
        .then(function(body) {
            fps = body.fps;

            // Update twice an FPS period (since we are polling and updates are not pushed).
            let delayMS = 1.0 / fps * 1000.0;

            // Update the UI according to the FPS from the server.
            setInterval(update, delayMS);
        })
    ;
}

function update() {
    // TEST
    let data = {
        'user_inputs': ['STOP'],
    }

    makeRequest('/api/update', data)
        .then(function(body) {
            document.querySelector('.page .image-area img').src = body.image_url;
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
    return Promise.reject(response);
}

document.addEventListener("DOMContentLoaded", main);
