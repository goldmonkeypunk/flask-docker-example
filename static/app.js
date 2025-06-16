/* global fetch */

document.addEventListener("DOMContentLoaded", () => {

  /* ───────── Journal click ───────── */
  document.querySelectorAll(".att").forEach(td => {
    if (!td.dataset.stu) return;
    td.addEventListener("click", async () => {
      const r = await fetch("/api/attendance/toggle", {
        method : "POST",
        headers: { "Content-Type": "application/json" },
        body   : JSON.stringify({ student_id: td.dataset.stu,
                                  date      : td.dataset.date })
      });
      if (!r.ok) return;
      const j = await r.json();
      td.classList.toggle("table-success");
      td.innerText = td.classList.contains("table-success") ? "✓" : "";
      td.parentElement.querySelector(".month-sum").innerText = j.month_sum;
      document.getElementById("total").innerText             = j.total;
    });
  });

  /* ───────── Add Student ───────── */
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

  /* ───────── Delete Student ───────── */
  document.querySelectorAll(".del-stu").forEach(btn=>{
    btn.addEventListener("click", async ()=>{
      if(!confirm("Видалити учня разом із відвідуваністю?")) return;
      const id=btn.dataset.id;
      const r = await fetch(`/api/student/${id}`,{method:"DELETE"});
      if(r.ok){
        document.getElementById(`stu-${id}`)?.remove();
        document.getElementById(`row-${id}`)?.remove();
      }
    });
  });

  /* ───────── Add Song ───────── */
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

  /* ───────── Delete Song ───────── */
  document.querySelectorAll(".del-song").forEach(btn=>{
    btn.addEventListener("click", async ()=>{
      if(!confirm("Видалити пісню з каталогу?")) return;
      const id=btn.dataset.id;
      const r = await fetch(`/api/song/${id}`,{method:"DELETE"});
      if(r.ok) document.getElementById(`song-${id}`)?.remove();
    });
  });

  /* ───────── Assign Song ───────── */
  document.querySelectorAll(".song-select").forEach(sel => {
    sel.addEventListener("change", async () => {
      const sid = sel.dataset.stu;
      const tid = sel.value;
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
