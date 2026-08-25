from pathlib import Path
import zipfile, shutil

out = Path("/mnt/data/workup_staff_html_v1")
if out.exists():
    shutil.rmtree(out)
out.mkdir()

html = r'''<!doctype html>
<html lang="bn">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>WorkUp Staff Management</title>
<style>
:root{--bg:#f4f7fb;--card:#fff;--text:#172033;--muted:#667085;--primary:#2563eb;--danger:#dc2626;--border:#e5e7eb}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Arial,sans-serif;background:var(--bg);color:var(--text)}
button,input,select,textarea{font:inherit}button{cursor:pointer;border:0}.hidden{display:none!important}
.login{min-height:100vh;display:grid;place-items:center;padding:20px}.login-card{width:min(420px,100%);background:#fff;padding:28px;border-radius:20px;box-shadow:0 12px 40px #0002}
.logo{font-size:28px;font-weight:800;margin-bottom:8px}.muted{color:var(--muted)}label{display:block;font-weight:600;margin:14px 0 6px}input,select,textarea{width:100%;padding:11px 12px;border:1px solid var(--border);border-radius:10px;background:#fff}textarea{min-height:100px;resize:vertical}
.btn{padding:11px 16px;border-radius:10px;background:var(--primary);color:#fff;font-weight:700}.btn.secondary{background:#eef2ff;color:#1d4ed8}.btn.danger{background:var(--danger)}.btn.gray{background:#eef0f3;color:#222}
.nav{position:sticky;top:0;z-index:5;background:#111827;color:#fff;padding:13px 4%;display:flex;align-items:center;gap:18px}.nav b{font-size:19px}.nav .grow{flex:1}.nav button{background:transparent;color:#fff;padding:8px}
.layout{display:grid;grid-template-columns:240px 1fr;min-height:calc(100vh - 58px)}aside{background:#fff;border-right:1px solid var(--border);padding:16px}.menu{display:block;width:100%;text-align:left;padding:12px;margin:4px 0;border-radius:10px;background:transparent}.menu.active,.menu:hover{background:#eef2ff;color:#1d4ed8;font-weight:700}
main{padding:22px;max-width:1400px;width:100%;margin:auto}.page{display:none}.page.active{display:block}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}.grid2{display:grid;grid-template-columns:repeat(2,1fr);gap:14px}.card{background:var(--card);border:1px solid var(--border);border-radius:16px;padding:18px;margin-bottom:16px}.stat strong{display:block;font-size:28px;margin-top:6px}.table-wrap{overflow:auto}.table{width:100%;border-collapse:collapse}.table th,.table td{text-align:left;padding:11px;border-bottom:1px solid var(--border);white-space:nowrap}.badge{display:inline-block;padding:5px 9px;border-radius:999px;background:#eef2ff;color:#1d4ed8;font-size:12px;font-weight:700}.badge.green{background:#dcfce7;color:#166534}.badge.red{background:#fee2e2;color:#991b1b}.actions{display:flex;gap:8px;flex-wrap:wrap}.chat{height:390px;overflow:auto;background:#f8fafc;border:1px solid var(--border);border-radius:14px;padding:14px}.bubble{max-width:78%;padding:10px 12px;border-radius:14px;margin:8px 0}.mine{margin-left:auto;background:#dbeafe}.theirs{background:#fff;border:1px solid var(--border)}.form-row{display:grid;grid-template-columns:repeat(2,1fr);gap:12px}.search{display:flex;gap:10px}.search input{flex:1}.small{font-size:13px}
@media(max-width:900px){.layout{grid-template-columns:1fr}aside{display:flex;overflow:auto;gap:6px;border-right:0;border-bottom:1px solid var(--border)}.menu{white-space:nowrap;width:auto}.grid{grid-template-columns:repeat(2,1fr)}}
@media(max-width:560px){main{padding:13px}.grid,.grid2,.form-row{grid-template-columns:1fr}.nav{padding:12px}.card{padding:14px}}
</style>
</head>
<body>

<section id="login" class="login">
  <div class="login-card">
    <div class="logo">WorkUp Staff</div>
    <p class="muted">Admin / Staff Login</p>
    <label>Username</label><input id="loginUser" placeholder="Username">
    <label>Password</label><input id="loginPass" type="password" placeholder="Password">
    <label>Login as</label>
    <select id="loginRole"><option value="admin">Admin</option><option value="staff">Staff</option></select>
    <button class="btn" style="width:100%;margin-top:18px" onclick="login()">Login</button>
    <p id="loginMsg" class="small muted"></p>
    <p class="small muted">Demo UI: আসল authentication/database backend-এর সাথে যুক্ত নয়।</p>
  </div>
</section>

<section id="app" class="hidden">
<nav class="nav"><b>WorkUp Staff</b><span class="grow"></span><span id="who"></span><button onclick="logout()">Logout</button></nav>
<div class="layout">
<aside id="side"></aside>
<main>
  <section id="dashboard" class="page active"></section>
  <section id="staff" class="page"></section>
  <section id="gmail" class="page"></section>
  <section id="work" class="page"></section>
  <section id="payment" class="page"></section>
  <section id="search" class="page"></section>
  <section id="chat" class="page"></section>
  <section id="security" class="page"></section>
</main>
</div>
</section>

<script>
const demo={
 admin:{username:"admin",password:"admin123",name:"Administrator"},
 staff:{username:"staff01",password:"staff123",name:"মিজানুর",mobile:"01XXXXXXXXX"},
 gmails:[
  {email:"example1@gmail.com",mobile:"01XXXXXXXXX",note:"কাজের Gmail"},
  {email:"example2@gmail.com",mobile:"01XXXXXXXXX",note:"কাজের Gmail"}
 ],
 works:[
  {staff:"মিজানুর",gmail:"example1@gmail.com",date:"26-08-2026",time:"10:30",qty:50,comment:"আজকের কাজ জমা",status:"Pending"},
  {staff:"মিজানুর",gmail:"example2@gmail.com",date:"26-08-2026",time:"14:20",qty:35,comment:"কমেন্ট কাজ",status:"Approved"}
 ],
 payments:[
  {staff:"মিজানুর",month:"August 2026",amount:"10000",date:"05-08-2026",status:"Paid"},
  {staff:"মিজানুর",month:"July 2026",amount:"10000",date:"05-07-2026",status:"Paid"}
 ],
 messages:[
  {from:"staff",text:"আজকের কাজ জমা দিয়েছি।",time:"10:45 AM"},
  {from:"admin",text:"ঠিক আছে, আমি দেখে দিচ্ছি।",time:"10:50 AM"}
 ]
};
let role=null;

function login(){
 const u=document.getElementById('loginUser').value.trim(), p=document.getElementById('loginPass').value, r=document.getElementById('loginRole').value;
 const ok=r==="admin"?u===demo.admin.username&&p===demo.admin.password:u===demo.staff.username&&p===demo.staff.password;
 if(!ok){document.getElementById('loginMsg').textContent="Username বা Password সঠিক নয়।";return}
 role=r; document.getElementById('login').classList.add('hidden');document.getElementById('app').classList.remove('hidden');
 document.getElementById('who').textContent=r==="admin"?"Admin":demo.staff.name; buildSide(); renderAll();
}
function logout(){role=null;document.getElementById('app').classList.add('hidden');document.getElementById('login').classList.remove('hidden')}
function buildSide(){
 const adminItems=[["dashboard","Dashboard"],["staff","Staff Account"],["gmail","Gmail"],["work","কাজ জমা/কাজের হিসাব"],["payment","Payment"],["search","Search"],["chat","Chat"],["security","Security"]];
 const staffItems=[["dashboard","Dashboard"],["gmail","আমার Gmail"],["work","কাজ জমা"],["payment","Payment"],["chat","Admin Chat"]];
 const items=role==="admin"?adminItems:staffItems;
 document.getElementById('side').innerHTML=items.map((x,i)=>`<button class="menu ${i===0?'active':''}" onclick="showPage('${x[0]}',this)">${x[1]}</button>`).join('');
}
function showPage(id,el){
 document.querySelectorAll('.page').forEach(x=>x.classList.remove('active'));document.getElementById(id).classList.add('active');
 document.querySelectorAll('.menu').forEach(x=>x.classList.remove('active'));if(el)el.classList.add('active');
 renderPage(id);
}
function renderAll(){["dashboard","staff","gmail","work","payment","search","chat","security"].forEach(renderPage)}
function renderPage(id){
 if(id==="dashboard") dashboard();
 if(id==="staff"&&role==="admin") staffPage();
 if(id==="gmail") gmailPage();
 if(id==="work") workPage();
 if(id==="payment") paymentPage();
 if(id==="search"&&role==="admin") searchPage();
 if(id==="chat") chatPage();
 if(id==="security"&&role==="admin") securityPage();
}
function dashboard(){
 const w=demo.works.reduce((a,b)=>a+b.qty,0), pay=demo.payments.filter(x=>x.status==="Paid").length;
 document.getElementById('dashboard').innerHTML=`<h1>${role==="admin"?"Admin Dashboard":"Staff Dashboard"}</h1>
 <div class="grid"><div class="card stat"><span>মোট Gmail</span><strong>${demo.gmails.length}</strong></div>
 <div class="card stat"><span>মোট কাজ</span><strong>${w}</strong></div>
 <div class="card stat"><span>Paid</span><strong>${pay}</strong></div>
 <div class="card stat"><span>Unread Chat</span><strong>1</strong></div></div>
 <div class="card"><h2>Quick Actions</h2><div class="actions">
 <button class="btn" onclick="showPage('work')">কাজ জমা</button><button class="btn secondary" onclick="showPage('chat')">Admin Chat</button>
 ${role==="admin"?'<button class="btn secondary" onclick="showPage(\\'staff\\')">Staff তৈরি</button>':''}</div></div>`;
}
function staffPage(){
 document.getElementById('staff').innerHTML=`<h1>Staff Account</h1>
 <div class="card"><h2>নতুন Staff তৈরি</h2><div class="form-row">
 <div><label>নাম</label><input id="newName" placeholder="নাম"></div><div><label>Username</label><input id="newUser" placeholder="Username"></div>
 <div><label>Mobile</label><input id="newMob" placeholder="Mobile"></div><div><label>Password</label><input id="newPass" type="password" placeholder="Temporary password"></div></div>
 <button class="btn" onclick="addStaff()">Create Staff</button></div>
 <div class="card"><h2>Staff List</h2><div class="table-wrap"><table class="table"><tr><th>Name</th><th>Username</th><th>Mobile</th><th>Status</th><th>Action</th></tr>
 <tr><td>${demo.staff.name}</td><td>${demo.staff.username}</td><td>${demo.staff.mobile}</td><td><span class="badge green">Active</span></td><td><button class="btn gray" onclick="alert('Demo: Edit Staff')">Edit</button></td></tr></table></div></div>`;
}
function addStaff(){alert("Demo UI: Staff তৈরি করার form ready. Backend যুক্ত হলে database-এ save হবে।")}
function gmailPage(){
 document.getElementById('gmail').innerHTML=`<h1>${role==="admin"?"Gmail Management":"আমার Gmail"}</h1>
 ${role==="admin"?'<div class="card"><h2>Gmail যোগ করুন</h2><div class="form-row"><input placeholder="Gmail"><input type="password" placeholder="Gmail Password"><input placeholder="কাজের Password"><input placeholder="কাজের Mobile"></div><button class="btn" onclick="alert(\\'Demo: Gmail save\\')">Save Gmail</button><p class="small muted">Production version-এ credential encrypted storage হবে।</p></div>':''}
 <div class="card"><div class="table-wrap"><table class="table"><tr><th>Gmail</th><th>Mobile</th><th>Note</th><th>Work Count</th><th>Comment</th></tr>
 ${demo.gmails.map(g=>{let c=demo.works.filter(w=>w.gmail===g.email).reduce((a,b)=>a+b.qty,0);return `<tr><td>${g.email}</td><td>${g.mobile}</td><td>${g.note}</td><td>${c}</td><td><button class="btn gray" onclick="alert('Gmail-wise comment history দেখাবে')">View</button></td></tr>`}).join('')}</table></div></div>`;
}
function workPage(){
 const rows=role==="admin"?demo.works:demo.works.filter(w=>w.staff===demo.staff.name);
 document.getElementById('work').innerHTML=`<h1>${role==="admin"?"কাজের হিসাব":"কাজ জমা দিন"}</h1>
 ${role==="staff"?`<div class="card"><h2>কাজ জমা</h2><div class="form-row"><select id="wg">${demo.gmails.map(g=>`<option>${g.email}</option>`).join('')}</select><input id="wq" type="number" placeholder="কতটি কাজ"></div><textarea id="wc" placeholder="Comment / কাজের বিবরণ"></textarea><button class="btn" onclick="submitWork()">Submit Work</button></div>`:''}
 <div class="card"><div class="table-wrap"><table class="table"><tr><th>Staff</th><th>Gmail</th><th>Date</th><th>Time</th><th>Qty</th><th>Comment</th><th>Status</th>${role==="admin"?'<th>Action</th>':''}</tr>
 ${rows.map((w,i)=>`<tr><td>${w.staff}</td><td>${w.gmail}</td><td>${w.date}</td><td>${w.time}</td><td>${w.qty}</td><td>${w.comment}</td><td><span class="badge ${w.status==="Approved"?'green':''}">${w.status}</span></td>${role==="admin"?`<td><button class="btn gray" onclick="approve(${i})">Approve</button></td>`:''}</tr>`).join('')}</table></div></div>`;
}
function submitWork(){demo.works.unshift({staff:demo.staff.name,gmail:document.getElementById('wg').value,date:"26-08-2026",time:new Date().toLocaleTimeString(),qty:+document.getElementById('wq').value||0,comment:document.getElementById('wc').value,status:"Pending"});alert("কাজ জমা হয়েছে।");renderPage("work");}
function approve(i){if(confirm("Security Password লাগবে। Demo-তে অনুমোদন করবেন?")){demo.works[i].status="Approved";renderPage("work")}}
function paymentPage(){
 const rows=demo.payments;
 document.getElementById('payment').innerHTML=`<h1>Payment</h1>${role==="admin"?'<div class="card"><h2>Payment যোগ করুন</h2><div class="form-row"><input placeholder="Staff Name"><input placeholder="Month"><input placeholder="Amount"><input type="date"></div><button class="btn" onclick="alert(\\'Demo: Payment save\\')">Save Payment</button></div>':''}<div class="card"><table class="table"><tr><th>Staff</th><th>Month</th><th>Amount</th><th>Date</th><th>Status</th></tr>${rows.map(p=>`<tr><td>${p.staff}</td><td>${p.month}</td><td>৳${p.amount}</td><td>${p.date}</td><td><span class="badge green">${p.status}</span></td></tr>`).join('')}</table></div>`;
}
function searchPage(){
 document.getElementById('search').innerHTML=`<h1>Search</h1><div class="card"><div class="search"><input id="sq" placeholder="নাম / Gmail / Mobile / Date"><button class="btn" onclick="doSearch()">Search</button></div><div id="sr" style="margin-top:15px"></div></div>`;
}
function doSearch(){const q=document.getElementById('sq').value.toLowerCase();const r=demo.works.filter(x=>Object.values(x).join(" ").toLowerCase().includes(q));document.getElementById('sr').innerHTML=`<p>${r.length}টি work record পাওয়া গেছে।</p>`+r.map(x=>`<div class="card">${x.staff} — ${x.gmail} — ${x.date} — ${x.qty} — ${x.comment}</div>`).join('')}
function chatPage(){
 document.getElementById('chat').innerHTML=`<h1>Admin ↔ Staff Chat</h1><div class="card"><div class="chat">${demo.messages.map(m=>`<div class="bubble ${m.from===role?'mine':'theirs'}"><b>${m.from==="admin"?"Admin":"Staff"}:</b> ${m.text}<br><small>${m.time}</small></div>`).join('')}</div><div style="display:flex;gap:8px;margin-top:10px"><input id="msg" placeholder="মেসেজ লিখুন..."><button class="btn" onclick="sendMsg()">Send</button></div></div>`;
}
function sendMsg(){const v=document.getElementById('msg').value.trim();if(!v)return;demo.messages.push({from:role,text:v,time:new Date().toLocaleTimeString()});renderPage("chat")}
function securityPage(){
 document.getElementById('security').innerHTML=`<h1>Security Password</h1><div class="card"><h2>Sensitive Action</h2><p>Delete/Edit/Password Change-এর আগে আলাদা Security Password যাচাই হবে।</p><input type="password" id="sec" placeholder="Security Password"><button class="btn danger" style="margin-top:10px" onclick="verifySec()">Verify</button><p class="small muted">Demo: আসল security password এখানে রাখা হয়নি।</p></div>`;
}
function verifySec(){alert("Demo security flow: production backend-এ server-side verification হবে।")}
</script>
</body>
</html>'''

(out/"index.html").write_text(html, encoding="utf-8")
readme = """# WorkUp Staff Management — HTML V1

`index.html` একটি মোবাইল/কম্পিউটার responsive UI prototype।

Demo login:
- Admin: username `admin`, password `admin123`
- Staff: username `staff01`, password `staff123`

এটি frontend prototype। Real online login, database, encrypted Gmail credentials, real-time chat, secure deletion/editing, payment persistence ইত্যাদির জন্য backend/server লাগবে।
"""
(out/"README.txt").write_text(readme, encoding="utf-8")

zip_path=Path("/mnt/data/workup_staff_html_v1.zip")
with zipfile.ZipFile(zip_path,"w",zipfile.ZIP_DEFLATED) as z:
    for p in out.rglob("*"):
        if p.is_file(): z.write(p,p.relative_to(out))
print(zip_path)
