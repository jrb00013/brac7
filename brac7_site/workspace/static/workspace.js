(function () {
  const dataEl = document.getElementById("bracket-data");
  const data = JSON.parse(dataEl.textContent);
  const canvas = document.getElementById("bracket-canvas");
  const ctx = canvas.getContext("2d");

  const nodes = data.nodes.map((n, i) => ({
    ...n,
    x: 80 + (n.round_index || 0) * 220,
    y: 60 + (n.match_index ?? i) * 72,
    w: 200,
    h: 56,
  }));

  let drag = null;
  let pan = { x: 0, y: 0 };
  let scale = 1;

  function draw() {
    ctx.save();
    ctx.setTransform(scale, 0, 0, scale, pan.x, pan.y);
    ctx.fillStyle = "#0a0e14";
    ctx.fillRect(-pan.x / scale, -pan.y / scale, canvas.width / scale, canvas.height / scale);

    nodes.forEach((n) => {
      ctx.fillStyle = n.is_bye ? "#2a3a28" : "#1e2d42";
      ctx.strokeStyle = "#3d8bfd";
      ctx.lineWidth = 2;
      ctx.fillRect(n.x, n.y, n.w, n.h);
      ctx.strokeRect(n.x, n.y, n.w, n.h);
      ctx.fillStyle = "#e7ecf3";
      ctx.font = "11px sans-serif";
      ctx.fillText(n.id, n.x + 8, n.y + 16);
      ctx.fillStyle = "#8b9cb3";
      ctx.fillText(`${n.a} vs ${n.b}`.slice(0, 28), n.x + 8, n.y + 36);
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
    if (n) drag = { node: n, ox: e.offsetX, oy: e.offsetY, nx: n.x, ny: n.y };
  });
  canvas.addEventListener("mousemove", (e) => {
    if (!drag) return;
    drag.node.x = drag.nx + (e.offsetX - drag.ox) / scale;
    drag.node.y = drag.ny + (e.offsetY - drag.oy) / scale;
    draw();
  });
  canvas.addEventListener("mouseup", () => { drag = null; });
  canvas.addEventListener("dblclick", (e) => {
    const n = hit(e.offsetX, e.offsetY);
    if (!n) return;
    const w = prompt(`Winner for ${n.id}?`, n.a);
    if (w) console.log("Winner recorded (wire to API):", n.id, w);
  });

  document.getElementById("btn-fit")?.addEventListener("click", () => {
    pan = { x: 40, y: 40 };
    scale = 1;
    draw();
  });

  document.getElementById("btn-save")?.addEventListener("click", async () => {
    const layout = nodes.map((n) => ({ id: n.id, x: n.x, y: n.y }));
    const pk = window.location.pathname.split("/").filter(Boolean).pop();
    await fetch(`/workspace/${pk}/layout/`, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRFToken": getCookie("csrftoken") },
      body: JSON.stringify(layout),
    });
    alert("Layout saved");
  });

  function getCookie(name) {
    const v = document.cookie.match("(^|;)\\s*" + name + "\\s*=\\s*([^;]+)");
    return v ? v.pop() : "";
  }

  draw();
})();
