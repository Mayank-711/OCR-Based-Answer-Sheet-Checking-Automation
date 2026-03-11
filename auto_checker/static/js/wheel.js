/* Spin the Wheel — Canvas-based wheel with animation */

(function () {
    'use strict';

    var segments = [
        { label: '+5 Points',         color: '#22c55e' },
        { label: '+10 Points',        color: '#16a34a' },
        { label: '+5 to\nSomeone',    color: '#3b82f6' },
        { label: '-5 Points',         color: '#ef4444' },
        { label: 'Get a Hint',        color: '#8b5cf6' },
        { label: 'Bet up\nto 10',     color: '#f59e0b' },
    ];

    var canvas = document.getElementById('wheelCanvas');
    if (!canvas) return;
    var ctx = canvas.getContext('2d');
    var centerX = canvas.width / 2;
    var centerY = canvas.height / 2;
    var radius = 180;

    var currentAngle = 0;
    var spinning = false;
    var currentResult = null;

    var spinBtn = document.getElementById('spinBtn');
    var resultDisplay = document.getElementById('resultDisplay');
    var assignBtn = document.getElementById('assignBtn');
    var participantInput = document.getElementById('participantName');
    var logList = document.getElementById('logList');

    function drawWheel(rotation) {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        var arc = (2 * Math.PI) / segments.length;

        for (var i = 0; i < segments.length; i++) {
            var angle = rotation + i * arc;

            // Segment
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, angle, angle + arc);
            ctx.closePath();
            ctx.fillStyle = segments[i].color;
            ctx.fill();
            ctx.strokeStyle = '#fff';
            ctx.lineWidth = 2;
            ctx.stroke();

            // Label
            ctx.save();
            ctx.translate(centerX, centerY);
            ctx.rotate(angle + arc / 2);
            ctx.textAlign = 'right';
            ctx.fillStyle = '#fff';
            ctx.font = 'bold 13px Segoe UI, system-ui, sans-serif';

            var lines = segments[i].label.split('\n');
            for (var l = 0; l < lines.length; l++) {
                ctx.fillText(lines[l], radius - 14, 5 + (l - (lines.length - 1) / 2) * 16);
            }
            ctx.restore();
        }

        // Center circle
        ctx.beginPath();
        ctx.arc(centerX, centerY, 22, 0, 2 * Math.PI);
        ctx.fillStyle = '#fff';
        ctx.fill();
        ctx.strokeStyle = '#e2e8f0';
        ctx.lineWidth = 2;
        ctx.stroke();

        // Pointer (triangle at top)
        ctx.beginPath();
        ctx.moveTo(centerX - 12, 15);
        ctx.lineTo(centerX + 12, 15);
        ctx.lineTo(centerX, 38);
        ctx.closePath();
        ctx.fillStyle = '#1e293b';
        ctx.fill();
    }

    function getSegmentIndex(angle) {
        var arc = (2 * Math.PI) / segments.length;
        // The pointer is at the top (3π/2 or -π/2)
        var pointerAngle = (3 * Math.PI / 2);
        var normalized = (pointerAngle - angle) % (2 * Math.PI);
        if (normalized < 0) normalized += 2 * Math.PI;
        return Math.floor(normalized / arc) % segments.length;
    }

    function spin() {
        if (spinning) return;
        spinning = true;
        spinBtn.disabled = true;
        assignBtn.disabled = true;
        resultDisplay.textContent = 'Spinning...';
        resultDisplay.style.color = '#64748b';

        var totalRotation = (Math.random() * 4 + 5) * 2 * Math.PI; // 5-9 full rotations
        var duration = 4000;
        var startTime = null;
        var startAngle = currentAngle;

        function animate(timestamp) {
            if (!startTime) startTime = timestamp;
            var elapsed = timestamp - startTime;
            var progress = Math.min(elapsed / duration, 1);

            // Ease-out cubic
            var eased = 1 - Math.pow(1 - progress, 3);
            currentAngle = startAngle + totalRotation * eased;

            drawWheel(currentAngle);

            if (progress < 1) {
                requestAnimationFrame(animate);
            } else {
                spinning = false;
                spinBtn.disabled = false;

                var idx = getSegmentIndex(currentAngle);
                currentResult = segments[idx].label.replace('\n', ' ');
                resultDisplay.textContent = currentResult;
                resultDisplay.style.color = segments[idx].color;
                assignBtn.disabled = false;
            }
        }

        requestAnimationFrame(animate);
    }

    function assignResult() {
        var name = participantInput.value.trim();
        if (!name || !currentResult) return;

        var li = document.createElement('li');
        li.textContent = name + ' → ' + currentResult;
        logList.insertBefore(li, logList.firstChild);

        participantInput.value = '';
        assignBtn.disabled = true;
        currentResult = null;
        resultDisplay.textContent = 'Assigned! Spin again.';
        resultDisplay.style.color = '#22c55e';
    }

    // Event listeners
    spinBtn.addEventListener('click', spin);
    assignBtn.addEventListener('click', assignResult);

    // Initial draw
    drawWheel(currentAngle);
})();
