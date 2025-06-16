/* global fetch */

document.addEventListener("DOMContentLoaded", () => {

  /** ───────── журнал ───────── **/
  document.querySelectorAll(".att").forEach(td => {
    if (!td.dataset.stu) return;           // у батьків немає атрибутів
    td.addEventListener("click", async () => {
      const r = await fetch("/api/attendance/toggle", {
        method : "POST",
        headers: { "Content-Type": "application/json" },
        body   : JSON.stringify({ student_id: td.dataset.stu,
                                  date: td.dataset.date })
      });
      if (!r.ok) return;
      const j = await r.json();
      td.classList.toggle("table-success");
      td.innerText = td.classList.contains("table-success") ? "✓" : "";
      td.parentElement.querySelector(".month-sum").innerText = j.month_sum;
      document.getElementById("total").innerText             = j.total;
    });
  });

  /** ───────── add student ───────── **/
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
      if (r.ok) location.reload();
    });
  }

  /** ───────── add song ───────── **/
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

  /** ───────── assign song ───────── **/
  document.querySelectorAll(".song-select").forEach(sel => {
    sel.addEventListener("change", async () => {
      const sid = sel.dataset.stu || sel.value;   // у різних шаблонів свій атрибут
      const tid = sel.dataset.songId || sel.value && sel.closest("li")?.dataset?.songId;
      if (!(sid && tid)) return;
      await fetch("/api/assign", {
        method : "POST",
        headers: { "Content-Type": "application/json" },
        body   : JSON.stringify({ student_id: sid, song_id: tid })
      });
      sel.selectedIndex = 0;
    });
  });

});
  