(function () {
  const dataEl = document.getElementById("bracket-data");
  const data = JSON.parse(dataEl.textContent);
  const canvas = document.getElementById("bracket-canvas");
  const ctx = canvas.getContext("2d");

  function resize() {
    canvas.width = canvas.clientWidth;
    canvas.height = canvas.clientHeight;
    draw();
  }
  window.addEventListener("resize", resize);

  const FEED_COLOR = "#6b8cae";
  const FEED_WIDTH = 1.5;

  const nodes = data.nodes.map((n, i) => ({
    ...n,
    x: 80 + (n.round_index || 0) * 220,
    y: 60 + (n.match_index ?? i) * 72,
    w: 200,
    h: 56,
  }));

  const nodeMap = {};
  nodes.forEach((n) => { nodeMap[n.id] = n; });

  let drag = null;
  let pan = { x: 0, y: 0 };
  let scale = 1;
  let lastPos = null;

  function drawConnectors() {
    for (const n of nodes) {
      if (!n.feeds_from || n.feeds_from.length === 0) continue;
      const cx = n.x;
      const cy = n.y + n.h / 2;
      for (const fid of n.feeds_from) {
        const parent = nodeMap[fid];
        if (!parent) continue;
        const px = parent.x + parent.w;
        const py = parent.y + parent.h / 2;
        const mx = (px + cx) / 2;

        ctx.strokeStyle = FEED_COLOR;
        ctx.lineWidth = FEED_WIDTH;
        ctx.beginPath();
        ctx.moveTo(px, py);
        ctx.lineTo(mx, py);
        ctx.lineTo(mx, cy);
        ctx.lineTo(cx, cy);
        ctx.stroke();

        ctx.fillStyle = FEED_COLOR;
        ctx.beginPath();
        ctx.arc(cx, cy, 3, 0, Math.PI * 2);
        ctx.fill();
      }
    }
  }

  function draw() {
    ctx.save();
    ctx.setTransform(scale, 0, 0, scale, pan.x, pan.y);

    ctx.fillStyle = "#0a0e14";
    ctx.fillRect(-pan.x / scale, -pan.y / scale, canvas.width / scale, canvas.height / scale);

    drawConnectors();

    nodes.forEach((n) => {
      const isBye = n.is_bye;
      ctx.fillStyle = isBye ? "#2a3a28" : "#1e2d42";
      ctx.strokeStyle = "#3d8bfd";
      ctx.lineWidth = isBye ? 1 : 2;
      ctx.fillRect(n.x, n.y, n.w, n.h);

      if (isBye) {
        ctx.strokeStyle = "#4a7a4a";
        ctx.setLineDash([4, 3]);
      }
      ctx.strokeRect(n.x, n.y, n.w, n.h);
      ctx.setLineDash([]);

      const mid = n.y + n.h / 2;

      ctx.strokeStyle = "#4a5f7a";
      ctx.lineWidth = 0.5;
      ctx.beginPath();
      ctx.moveTo(n.x + 6, mid);
      ctx.lineTo(n.x + n.w - 6, mid);
      ctx.stroke();

      ctx.fillStyle = "#e7ecf3";
      ctx.font = "10px sans-serif";
      ctx.fillText(n.id, n.x + 8, n.y + 14);

      ctx.fillStyle = "#8b9cb3";
      const label = (n.a + " vs " + n.b).slice(0, 28);
      ctx.fillText(label, n.x + 8, n.y + 30);

      if (isBye) {
        ctx.fillStyle = "#8fbc8f";
        ctx.font = "italic 8px sans-serif";
        ctx.fillText("BYE", n.x + n.w - 30, n.y + 14);
      }

      if (drag && drag.node === n) {
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 2;
        ctx.strokeRect(n.x - 1, n.y - 1, n.w + 2, n.h + 2);
      }
    });

    ctx.restore();
  }

  function hit(mx, my) {
    const x = (mx - pan.x) / scale;
    const y = (my - pan.y) / scale;
    for (let i = nodes.length - 1; i >= 0; i--) {
      const n = nodes[i];
      if (x >= n.x && x <= n.x + n.w && y >= n.y && y <= n.y + n.h) return n;
    }
    return null;
  }

  canvas.addEventListener("mousedown", (e) => {
    const n = hit(e.offsetX, e.offsetY);
    if (n) {
      drag = { node: n, ox: e.offsetX, oy: e.offsetY, nx: n.x, ny: n.y };
    } else {
      lastPos = { x: e.offsetX, y: e.offsetY };
    }
  });

  canvas.addEventListener("mousemove", (e) => {
    if (drag) {
      drag.node.x = Math.round(drag.nx + (e.offsetX - drag.ox) / scale);
      drag.node.y = Math.round(drag.ny + (e.offsetY - drag.oy) / scale);
      draw();
    } else if (lastPos) {
      pan.x += e.offsetX - lastPos.x;
      pan.y += e.offsetY - lastPos.y;
      lastPos = { x: e.offsetX, y: e.offsetY };
      draw();
    }
  });

  canvas.addEventListener("mouseup", () => { drag = null; lastPos = null; });
  canvas.addEventListener("mouseleave", () => { drag = null; lastPos = null; });

  canvas.addEventListener("dblclick", (e) => {
    const n = hit(e.offsetX, e.offsetY);
    if (!n) return;
    const w = prompt(`Winner for ${n.id}?`, n.a);
    if (w) {
      const pk = window.location.pathname.split("/").filter(Boolean).pop();
      fetch(`/bracket/${pk}/api/winner/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
        body: JSON.stringify({ match_id: n.id, winner: w }),
      }).then((r) => {
        if (r.ok) alert(`Winner: ${w}`);
        else alert("Failed to record winner");
      });
    }
  });

  canvas.addEventListener("wheel", (e) => {
    e.preventDefault();
    const delta = e.deltaY > 0 ? 0.9 : 1.1;
    const ns = Math.max(0.2, Math.min(5, scale * delta));

    const mx = e.offsetX;
    const my = e.offsetY;
    pan.x = mx - (mx - pan.x) * (ns / scale);
    pan.y = my - (my - pan.y) * (ns / scale);
    scale = ns;

    draw();
  }, { passive: false });

  document.getElementById("btn-fit")?.addEventListener("click", () => {
    pan = { x: 40, y: 40 };
    scale = 1;
    draw();
  });

  document.getElementById("btn-zoom-in")?.addEventListener("click", () => {
    scale = Math.min(5, scale * 1.3);
    draw();
  });

  document.getElementById("btn-zoom-out")?.addEventListener("click", () => {
    scale = Math.max(0.2, scale * 0.7);
    draw();
  });

  document.getElementById("btn-save")?.addEventListener("click", async () => {
    const layout = nodes.map((n) => ({ id: n.id, x: n.x, y: n.y }));
    const pk = window.location.pathname.split("/").filter(Boolean).pop();
    try {
      const r = await fetch(`/workspace/${pk}/layout/`, {
        method: "POST",
        headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
        body: JSON.stringify(layout),
      });
      if (r.ok) {
        const btn = document.getElementById("btn-save");
        btn.textContent = "Saved!";
        setTimeout(() => { btn.textContent = "Save layout"; }, 1500);
      } else {
        alert("Failed to save layout");
      }
    } catch {
      alert("Failed to save layout");
    }
  });

  function getCookie(name) {
    const v = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return v ? v.pop() : "";
  }

  resize();
})();
