/* global fetch */

document.addEventListener("DOMContentLoaded", () => {

  /* lesson +/- кнопки (только у админа) */
  document.querySelectorAll(".add-btn").forEach(btn => {
    btn.addEventListener("click", () => handleLesson(btn.dataset.id, "POST"));
  });
  document.querySelectorAll(".del-btn").forEach(btn => {
    btn.addEventListener("click", () => handleLesson(btn.dataset.id, "DELETE"));
  });

  async function handleLesson(id, method) {
    const r = await fetch(`/api/attendance/${id}`, { method });
    if (!r.ok) return;
    const j = await r.json();
    updateRow(id, j);
  }
  function updateRow(id, j) {
    const row = document.getElementById(`row-${id}`);
    row.querySelector(".lessons").innerText = j.week / 130;
    row.querySelector(".sum").innerText     = j.week;
    document.getElementById("total").innerText = `Усього: ${j.total} ₴`;
  }

  /* assign song (только у админа) */
  document.querySelectorAll(".song-select").forEach(sel => {
    sel.addEventListener("change", async () => {
      const song  = sel.dataset.songId;
      const stud  = sel.value;
      if (!stud) return;
      await fetch("/api/assign", {
        method : "POST",
        headers: { "Content-Type": "application/json" },
        body   : JSON.stringify({ student_id: stud, song_id: song })
      });
      sel.selectedIndex = 0;
    });
  });

});
