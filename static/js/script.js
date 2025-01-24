// import * as rive from "/static/lib/rive.js";

document.addEventListener('DOMContentLoaded', (event) => {
    const visualizeButton = document.getElementById('visualizeButton');

    let countdownInterval; // Countdown interval
    if (visualizeButton) {
        visualizeButton.addEventListener('click', function () {
            const testElement = document.getElementById('testElement');
            const countdownElement = document.getElementById('countdown');
            const countdownTimer = document.getElementById('countdownTimer');

            if (testElement) {
                testElement.classList.add('slide-out');
            }
            if (countdownElement) {
                countdownElement.style.display = 'block';
            }

            let countdown = 3;
            if (countdownTimer) {
                countdownTimer.textContent = countdown;
            }

            const countdownInterval = setInterval(() => {
                countdown -= 1;
                if (countdownTimer) {
                    countdownTimer.textContent = countdown;
                }

                if (countdown <= 0) {
                    clearInterval(countdownInterval);
                    window.location.href = '/visualize';
                }
            }, 1000);
        });
    }




    let flyTrigger; // Rive fly trigger
    window.rive.RuntimeLoader.setWasmUrl('/static/lib/rive.wasm');

    try {
        const r = new window.rive.Rive({
            src: "/static/assets/mach24.riv",
            canvas: document.getElementById("canvas"),
            autoplay: true,
            stateMachines: "State Machine 1",
            onLoad: () => {
                r.resizeDrawingSurfaceToCanvas();
                const inputs = r.stateMachineInputs('State Machine 1');
                flyTrigger = inputs.find(i => i.name === 'fly'); // Assign flyTrigger here
            },
            onLoadError: (err) => {
                console.error('Rive load error:', err);
            }
        });

        //trigger button event listener
        const triggerButton = document.getElementById('triggerFly');
        if (triggerButton) {
            triggerButton.addEventListener('click', () => {
                if (flyTrigger) {
                    flyTrigger.fire();
                } else {
                    console.error('flyTrigger is not defined');
                }
            });
        }
    } catch (err) {
        console.error('Rive initialization error:', err);
    }

    var socket = io();
        
        socket.on('connect', function() {
            console.log('Connected to server');
        });

        // socket.on('status', function(data) {
        //     console.log('Status received:', data);
        //     // Update images based on data values
        //     updateImage('ready', data.k1);
        //     updateImage('clear', data.k2);
        //     updateImage('fly', data.k3);

        //     // Check if all values are 1 and redirect
        //     if (data.k1 === 1 && data.k2 === 1 && data.k3 === 1) {
        //         window.location.href = '/visualize';
        //     }
        // });

        socket.on('new_data', function(data) {
            console.log('websocket Status received:', data);
        });

        socket.on('status_update', function(status) {
            console.log('websocket Status received:', status);
        });

        socket.on('disconnect', function() {
            console.log('Disconnected from server');
        });

    // Fetch status from /status endpoint
    const fetchData = () => {
        fetch('/status')
        .then(response => response.json())
        .then(data => {
            console.log('Status fetched:', data);
            // document.getElementById('statusK1').textContent = data.k1;
            // document.getElementById('statusK2').textContent = data.k2;
            // document.getElementById('statusK3').textContent = data.k3;
            document.getElementById('dataK1Value').textContent = data.k1; // Set data.k1 value

            // Update images based on data values
            updateImage('ready', data.k1);
            updateImage('clear', data.k2);
            updateImage('fly', data.k3);

            // Check if all values are 1 and redirect
            if (data.k1 === 1 && data.k2 === 1 && data.k3 === 1) {
                if (flyTrigger) {
                    flyTrigger.fire();
                }
                let countdown = 3;
                countdownInterval = setInterval(() => {
                    countdown -= 1;
                    if (countdownTimer) {
                        countdownTimer.textContent = countdown;
                    }
    
                    if (countdown <= 0) {
                        clearInterval(countdownInterval);
                        window.location.href = '/visualize';
                    }
                }, 1000);;
            }
        })
        .catch(error => {
            console.error('Error fetching status:', error);
        });
    };

    const updateImage = (id, value) => {
        const image = document.getElementById(id);
        if (image) {
            image.src = value === 1 ? `static/assets/${id}.png` : "static/assets/off.png";
        }
    };

    // setInterval(fetchData, 1000);
});

// function changeImage(id) {
//     var image = document.getElementById(id);
//     if (image.src.match("off")) {
//         switch (id) {
//             case 'ready':
//                 image.src = "static/assets/yellow.png";
//                 break;
//             case 'clear':
//                 image.src = "static/assets/green.png";
//                 break;
//             case 'fly':
//                 image.src = "static/assets/red.png";
//                 break;
//         }
//     } else {
//         image.src = "static/assets/off.png";
//     }
// }