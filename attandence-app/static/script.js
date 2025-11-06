const video = document.getElementById("camera");
const canvas = document.getElementById("canvas");
const scanStatus = document.getElementById("scanStatus");

if (video) {
  const ctx = canvas.getContext("2d");
  navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
    .then(stream => {
      video.srcObject = stream;
      video.setAttribute("playsinline", true);
      video.play();
      requestAnimationFrame(scanFrame);
    });

  async function scanFrame() {
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
      canvas.height = video.videoHeight;
      canvas.width = video.videoWidth;
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(imageData.data, imageData.width, imageData.height);

      if (code) {
        scanStatus.innerText = "✅ QR Detected! Marking attendance...";
        const res = await fetch("/mark_attendance", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ qr_data: code.data })
        });
        const result = await res.json();
        scanStatus.innerText = result.message;
        await new Promise(r => setTimeout(r, 3000)); // wait 3s before next scan
      } else {
        scanStatus.innerText = "Scanning...";
      }
    }
    requestAnimationFrame(scanFrame);
  }
}

async function fetchData() {
  const res = await fetch("/attendance_data");
  const data = await res.json();
  const tbody = document.querySelector("#attendanceTable tbody");
  tbody.innerHTML = "";
  data.forEach(row => {
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${row.StudentID}</td><td>${row.Name}</td><td>${row.Date}</td><td>${row.Time}</td>`;
    tbody.appendChild(tr);
  });
}

window.onload = () => {
  if (document.getElementById("attendanceTable")) fetchData();
};
