/* global fetch */

document.addEventListener("DOMContentLoaded", () => {

  /* ───────── журнал: кліки по комірках ───────── */
  document.querySelectorAll(".att").forEach(td => {
    if (!td.dataset.stu) return;                // у батьків атрибутів немає
    td.addEventListener("click", async () => {
      const payload = { student_id: td.dataset.stu, date: td.dataset.date };
      const r = await fetch("/api/attendance/toggle", {
        method : "POST",
        headers: { "Content-Type": "application/json" },
        body   : JSON.stringify(payload)
      });
      if (!r.ok) return;
      const j = await r.json();
      td.classList.toggle("table-success");
      td.innerText = td.classList.contains("table-success") ? "✓" : "";
      td.parentElement.querySelector(".week-sum").innerText = j.week;
      document.getElementById("total").innerText            = j.total;
    });
  });

  /* ───────── add student ───────── */
  const addStudent = document.getElementById("addStudent");
  if (addStudent){
    addStudent.addEventListener("submit", async e => {
      e.preventDefault();
      const name = addStudent.elements.name.value.trim();
      if (!name) return;
      const r = await fetch("/api/student", {
        method:"POST", headers:{'Content-Type':'application/json'},
        body:JSON.stringify({name})
      });
      if (r.ok) location.reload();      // простіше перезавантажити
    });
  }

  /* ───────── add song ───────── */
  const addSong = document.getElementById("addSong");
  if (addSong){
    addSong.addEventListener("submit", async e => {
      e.preventDefault();
      const data = Object.fromEntries(new FormData(addSong));
      const r = await fetch("/api/song", {
        method:"POST", headers:{'Content-Type':'application/json'},
        body:JSON.stringify(data)
      });
      if (r.ok) location.reload();
    });
  }

  /* ───────── assign song ───────── */
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
