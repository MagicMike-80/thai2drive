import React, { useRef, useState, useEffect } from 'react';
import {
  View, Text, StyleSheet, TouchableOpacity, ScrollView,
  SafeAreaView, Linking, Platform, Animated, Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';
import { useAppStore } from '../src/store/appStore';

const maleeCasual = require('../assets/malee_casual.png');
const michaelAthletic = require('../assets/michael_athletic.png');

// ── Neon Quiz HTML (full document for srcDoc iframe) ─────────────────────────
const QUIZ_HTML = `<!DOCTYPE html><html lang="no"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Exo+2:wght@300;400;500;600&display=swap" rel="stylesheet"><style>:root{--cy:#00F5FF;--mg:#FF00E5;--gd:#FFD700;--dk:#020510;--tx:#E8F4FF;--mu:rgba(200,230,255,0.45);--bc:rgba(0,245,255,0.18)}*{box-sizing:border-box;margin:0;padding:0}body{background:var(--dk);font-family:'Exo 2',sans-serif;color:var(--tx);min-height:100vh;overflow-x:hidden}.qr{position:relative;overflow:hidden;min-height:100vh}.qc{position:fixed;inset:0;z-index:0;pointer-events:none}.scan{position:fixed;inset:0;background:repeating-linear-gradient(0deg,transparent,transparent 2px,rgba(0,0,0,.025) 2px,rgba(0,0,0,.025) 4px);pointer-events:none;z-index:2}.qb{position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;padding:28px 22px;min-height:100vh}.qs{display:none;width:100%;animation:fu .4s cubic-bezier(.22,1,.36,1)}.qs.on{display:flex;flex-direction:column;align-items:center}@keyframes fu{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}.ey{font-size:11px;letter-spacing:.25em;text-transform:uppercase;color:rgba(0,245,255,.6);margin-bottom:8px;font-weight:500;text-align:center}.bt{font-family:'Orbitron',sans-serif;font-size:clamp(28px,10vw,46px);font-weight:900;line-height:1;text-align:center;background:linear-gradient(135deg,var(--cy) 0%,#fff 45%,var(--mg) 100%);-webkit-background-clip:text;background-clip:text;color:transparent;margin-bottom:6px;position:relative}.bt::before{content:attr(data-t);position:absolute;inset:0;background:inherit;-webkit-background-clip:text;background-clip:text;color:transparent;filter:blur(20px);opacity:.35}.ts{font-size:13px;color:var(--mu);text-align:center;margin-bottom:22px}.sg{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;width:100%;margin-bottom:18px}.sb{background:rgba(0,245,255,.04);border:1px solid rgba(0,245,255,.12);border-radius:10px;padding:13px 8px;text-align:center}.sn{font-family:'Orbitron',sans-serif;font-size:20px;font-weight:700;color:var(--cy);text-shadow:0 0 12px rgba(0,245,255,.6);display:block}.sl{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--mu);margin-top:3px;display:block}.tw{width:100%;background:rgba(0,245,255,.03);border:1px solid rgba(0,245,255,.1);border-radius:12px;padding:16px;margin-bottom:20px}.th{font-size:10px;letter-spacing:.18em;text-transform:uppercase;color:rgba(0,245,255,.5);margin-bottom:10px;font-weight:600}.tr{display:flex;flex-wrap:wrap;gap:7px}.tg{border-radius:20px;padding:5px 12px;font-size:11px;border:1px solid}.tc{color:rgba(0,245,255,.85);border-color:rgba(0,245,255,.2);background:rgba(0,245,255,.06)}.tm{color:rgba(255,0,229,.85);border-color:rgba(255,0,229,.2);background:rgba(255,0,229,.06)}.tg2{color:rgba(255,215,0,.85);border-color:rgba(255,215,0,.2);background:rgba(255,215,0,.06)}.bn{width:100%;background:transparent;border:1px solid var(--cy);border-radius:10px;padding:14px;font-family:'Orbitron',sans-serif;font-size:13px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:var(--cy);cursor:pointer;position:relative;overflow:hidden;transition:all .3s;animation:bp 2.5s ease infinite}@keyframes bp{0%,100%{box-shadow:0 0 14px rgba(0,245,255,.1)}50%{box-shadow:0 0 26px rgba(0,245,255,.3)}}.bn::before{content:'';position:absolute;inset:0;background:linear-gradient(90deg,transparent,rgba(0,245,255,.12),transparent);transform:translateX(-100%);transition:transform .5s}.bn:hover{background:rgba(0,245,255,.08);transform:translateY(-2px)}.bn:hover::before{transform:translateX(100%)}.bn:active{transform:translateY(0)}.pr{display:flex;justify-content:space-between;align-items:center;width:100%;margin-bottom:7px}.qn{font-family:'Orbitron',sans-serif;font-size:11px;font-weight:600;color:var(--cy);letter-spacing:.08em}.pt{font-family:'Orbitron',sans-serif;font-size:11px;font-weight:600;color:var(--gd);text-shadow:0 0 8px rgba(255,215,0,.5)}.pb{width:100%;height:3px;background:rgba(0,245,255,.08);border-radius:2px;overflow:hidden;margin-bottom:16px}.pf{height:100%;background:linear-gradient(90deg,#0080FF,var(--cy));border-radius:2px;box-shadow:0 0 8px rgba(0,245,255,.6);transition:width .6s cubic-bezier(.22,1,.36,1)}.qcard{width:100%;perspective:800px;margin-bottom:12px}.qface{background:rgba(4,10,26,.93);border:1px solid var(--bc);border-radius:13px;padding:20px;position:relative;transition:transform .15s ease;transform-style:preserve-3d;will-change:transform}.qface::before{content:'';position:absolute;inset:-1px;border-radius:14px;background:linear-gradient(135deg,rgba(0,245,255,.22),transparent 50%,rgba(255,0,229,.1));pointer-events:none}.qpill{display:inline-block;font-size:9px;letter-spacing:.2em;text-transform:uppercase;font-weight:600;color:var(--cy);border:1px solid rgba(0,245,255,.25);border-radius:20px;padding:4px 10px;margin-bottom:11px;position:relative;z-index:1}.qtxt{font-size:15px;font-weight:500;line-height:1.55;position:relative;z-index:1}.ol{display:flex;flex-direction:column;gap:7px;width:100%}.op{background:rgba(0,245,255,.03);border:1px solid rgba(0,245,255,.1);border-radius:9px;padding:11px 13px;display:flex;align-items:center;gap:10px;cursor:pointer;font-family:'Exo 2',sans-serif;font-size:13px;color:rgba(232,244,255,.85);text-align:left;width:100%;position:relative;overflow:hidden;transition:all .2s}.op::before{content:'';position:absolute;left:0;top:0;bottom:0;width:0;background:linear-gradient(90deg,rgba(0,245,255,.07),transparent);transition:width .3s}.op:hover:not(:disabled){border-color:rgba(0,245,255,.3);background:rgba(0,245,255,.07);transform:translateX(3px)}.op:hover:not(:disabled)::before{width:70%}.op.right{border-color:rgba(0,255,150,.5);background:rgba(0,255,150,.07);color:#00FF96}.op.wrong{border-color:rgba(255,0,229,.4);background:rgba(255,0,229,.07);color:var(--mg);animation:sk .4s ease}@keyframes sk{0%,100%{transform:translateX(0)}20%{transform:translateX(-5px)}40%{transform:translateX(5px)}60%{transform:translateX(-3px)}80%{transform:translateX(3px)}}.ol2{width:24px;height:24px;border-radius:5px;background:rgba(0,245,255,.06);border:1px solid rgba(0,245,255,.14);display:flex;align-items:center;justify-content:center;font-family:'Orbitron',sans-serif;font-size:9px;font-weight:700;color:var(--cy);flex-shrink:0}.op.right .ol2{background:rgba(0,255,150,.12);border-color:rgba(0,255,150,.35);color:#00FF96}.op.wrong .ol2{background:rgba(255,0,229,.12);border-color:rgba(255,0,229,.35);color:var(--mg)}.ex{width:100%;padding:11px 13px;background:rgba(0,245,255,.05);border:1px solid rgba(0,245,255,.14);border-left:2px solid var(--cy);border-radius:9px;font-size:12px;line-height:1.6;color:rgba(232,244,255,.72);margin-top:9px;display:none;animation:fu .3s ease}.ex.on{display:block}.bnn{width:100%;margin-top:11px;background:transparent;border:1px solid rgba(0,245,255,.22);border-radius:9px;padding:11px;font-family:'Orbitron',sans-serif;font-size:11px;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--cy);cursor:pointer;transition:all .2s;display:none}.bnn:hover{background:rgba(0,245,255,.08);border-color:var(--cy)}.bnn.on{display:block;animation:fu .3s ease}.rl{font-size:10px;letter-spacing:.22em;text-transform:uppercase;color:var(--mu);text-align:center;margin-bottom:18px}.rw{width:130px;height:130px;position:relative;display:flex;align-items:center;justify-content:center;margin:0 auto 22px}.rs{position:absolute;inset:0;width:100%;height:100%}.rn{font-family:'Orbitron',sans-serif;font-size:30px;font-weight:900;color:var(--cy);text-shadow:0 0 16px rgba(0,245,255,.7);text-align:center;line-height:1}.rd{font-size:13px;font-weight:400;color:var(--mu);display:block;text-align:center}.rm{font-family:'Orbitron',sans-serif;font-size:16px;font-weight:700;text-align:center;margin-bottom:6px}.rsu{font-size:13px;color:var(--mu);text-align:center;margin-bottom:26px;line-height:1.55}.bm{width:100%;background:transparent;border:1px solid var(--mg);border-radius:10px;padding:13px;font-family:'Orbitron',sans-serif;font-size:12px;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--mg);cursor:pointer;transition:all .3s}.bm:hover{background:rgba(255,0,229,.08);transform:translateY(-2px)}</style></head><body><div class="qr"><canvas class="qc" id="qcv"></canvas><div class="scan"></div><div class="qb"><div class="qs on" id="si"><p class="ey">Thai2Drive</p><h1 class="bt" data-t="TEORI QUIZ">TEORI<br>QUIZ</h1><p class="ts">Test dine kunnskaper om norsk trafikkteori</p><div class="sg"><div class="sb"><span class="sn">8</span><span class="sl">Sp&#248;rsm&#229;l</span></div><div class="sb"><span class="sn">3</span><span class="sl">Kategorier</span></div><div class="sb"><span class="sn">&#8734;</span><span class="sl">Fors&#248;k</span></div></div><div class="tw"><div class="th">Emner dekket</div><div class="tr"><span class="tg tc">Vikeplikt</span><span class="tg tc">Fartsgrense</span><span class="tg tc">Trafikkskilt</span><span class="tg tc">Gangfelt</span><span class="tg tm">Rundkj&#248;ring</span><span class="tg tm">Lysbruk</span><span class="tg tg2">Parkering</span><span class="tg tg2">Sikkerhet</span></div></div><button class="bn" onclick="startQ()">INITIALISER QUIZ &#9654;</button></div><div class="qs" id="sq"><div class="pr"><span class="qn" id="qn">SP. 1 / 8</span><span class="pt" id="spt">0 PT</span></div><div class="pb"><div class="pf" id="pf" style="width:0%"></div></div><div class="qcard" id="qcard"><div class="qface" id="qf"><div class="qpill" id="qtp"></div><div class="qtxt" id="qt"></div></div></div><div class="ol" id="ol"></div><div class="ex" id="ex"></div><button class="bnn" id="bn2" onclick="nextQ()">NESTE SP&#216;RSM&#197;L &#8594;</button></div><div class="qs" id="sr"><p class="rl">Quiz fullf&#248;rt</p><div class="rw"><svg class="rs" viewBox="0 0 130 130"><defs><linearGradient id="rg" x1="0" y1="0" x2="1" y2="1"><stop offset="0%" stop-color="#00F5FF"/><stop offset="100%" stop-color="#FF00E5"/></linearGradient></defs><circle cx="65" cy="65" r="56" fill="none" stroke="rgba(0,245,255,0.07)" stroke-width="6"/><circle id="rr" cx="65" cy="65" r="56" fill="none" stroke="url(#rg)" stroke-width="6" stroke-linecap="round" stroke-dasharray="352" stroke-dashoffset="352" transform="rotate(-90 65 65)" style="transition:stroke-dashoffset 1.3s cubic-bezier(.22,1,.36,1)"/></svg><div class="rn" id="rnm">0<span class="rd">/ 8</span></div></div><p class="rm" id="rmg"></p><p class="rsu" id="rsb"></p><button class="bm" onclick="startQ()">&#8635; KJ&#216;R IGJEN</button></div></div></div><script>const QD=[{t:'Vikeplikt',q:'Hvem har vikeplikt i et kryss uten skilt?',o:['Den fra h\\u00f8yre','Den fra venstre','Den raskeste','Den med stopp-skilt'],c:0,e:'H\\u00f8yreregelen: Du skal gi vikeplikt for trafikk fra h\\u00f8yre.'},{t:'Fartsgrense',q:'Standard fartsgrense i tettbygd str\\u00f8k i Norge?',o:['40 km/t','50 km/t','60 km/t','80 km/t'],c:1,e:'50 km/t er standard i tettbygd str\\u00f8k.'},{t:'Trafikkskilt',q:'Hva betyr rundt r\\u00f8dt skilt med hvit horisontal strek?',o:['Parkering forbudt','All innkj\\u00f8ring forbudt','Stopp-plikt','Forbikj\\u00f8ring forbudt'],c:1,e:'Rundt r\\u00f8dt skilt med hvit strek = all innkj\\u00f8ring forbudt.'},{t:'Gangfelt',q:'Hvem plikter \\u00e5 stanse for fotgjengere i gangfelt?',o:['Fotgjengeren','Bilisten alltid','Begge likt','Ingen plikt'],c:1,e:'Bilisten plikter alltid \\u00e5 stanse for fotgjengere i gangfelt.'},{t:'Rundkj\\u00f8ring',q:'Hvem har forkj\\u00f8rsrett i en rundkj\\u00f8ring?',o:['Den som kj\\u00f8rer inn','Trafikk inne i ringen','Den med stopp-skilt','Trafikk fra h\\u00f8yre'],c:1,e:'Trafikk inne i rundkj\\u00f8ringen har alltid forkj\\u00f8rsrett.'},{t:'Lysbruk',q:'N\\u00e5r skal n\\u00e6rlys brukes i Norge?',o:['Bare om natten','I tunnel og t\\u00e5ke','Alltid under kj\\u00f8ring','Bare ved d\\u00e5rlig sikt'],c:2,e:'N\\u00e6rlys skal brukes ved all kj\\u00f8ring i Norge.'},{t:'Parkering',q:'Minste lovlige avstand til kryss ved parkering?',o:['2 meter','5 meter','10 meter','15 meter'],c:1,e:'Minste lovlige avstand til et kryss er 5 meter.'},{t:'Sikkerhet',q:'Normal reaksjonstid for en utkvilt, edru sj\\u00e5f\\u00f8r?',o:['0,2 sekunder','0,5\\u20131 sekund','2 sekunder','3 sekunder'],c:1,e:'Normal reaksjonstid er omtrent 0,5\\u20131 sekund.'}];let cur=0,score=0,answered=false;function show(id){document.querySelectorAll('.qs').forEach(s=>s.classList.remove('on'));document.getElementById(id).classList.add('on');}function startQ(){cur=0;score=0;answered=false;renderQ();show('sq');}function renderQ(){const q=QD[cur];document.getElementById('qn').textContent='SP. '+(cur+1)+' / '+QD.length;document.getElementById('spt').textContent=score+' PT';document.getElementById('pf').style.width=(cur/QD.length*100)+'%';document.getElementById('qtp').textContent=q.t.toUpperCase();document.getElementById('qt').textContent=q.q;document.getElementById('ex').className='ex';document.getElementById('bn2').className='bnn';answered=false;document.getElementById('ol').innerHTML=q.o.map((o,i)=>'<button class="op" id="op'+i+'" onclick="pick('+i+')"><span class="ol2">'+('ABCD'[i])+'</span>'+o+'</button>').join('');}function pick(i){if(answered)return;answered=true;const q=QD[cur];document.querySelectorAll('.op').forEach(b=>b.disabled=true);document.getElementById('op'+q.c).classList.add('right');if(i!==q.c)document.getElementById('op'+i).classList.add('wrong');else score++;document.getElementById('ex').textContent=q.e;document.getElementById('ex').classList.add('on');const nb=document.getElementById('bn2');nb.textContent=cur<QD.length-1?'NESTE SP\\u00d8RSM\\u00c5L \\u2192':'SE RESULTAT \\u2192';nb.classList.add('on');}function nextQ(){cur++;if(cur>=QD.length){showRes();return;}renderQ();}function showRes(){show('sr');const pct=score/QD.length;const M=[['\\u00d8v mer!','Les teoriboken og pr\\u00f8v igjen.'],['Bra fors\\u00f8k!','Du er p\\u00e5 vei. Fokuser p\\u00e5 svake emner.'],['Veldig bra!','Du har god teoriforst\\u00e5else!'],['PERFEKT!','Ekspertniv\\u00e5 — du er klar for teorikj\\u00f8ring!']];const mi=pct<.4?0:pct<.63?1:pct<1?2:3;document.getElementById('rmg').textContent=M[mi][0];document.getElementById('rsb').textContent=M[mi][1];let n=0;const tm=setInterval(()=>{if(n>=score){clearInterval(tm);return;}document.getElementById('rnm').innerHTML=(++n)+'<span class="rd">/ 8</span>';},160);setTimeout(()=>{document.getElementById('rr').style.strokeDashoffset=352*(1-pct);},200);}const face=document.getElementById('qf'),card=document.getElementById('qcard');if(card&&face){card.addEventListener('mousemove',e=>{const r=card.getBoundingClientRect();if(!r.width)return;const mx=(e.clientX-r.left)/r.width-.5,my=(e.clientY-r.top)/r.height-.5;face.style.transform='rotateY('+(mx*8)+'deg) rotateX('+(-my*5)+'deg)';});card.addEventListener('mouseleave',()=>{face.style.transform='';});}const cv=document.getElementById('qcv'),cx=cv.getContext('2d');let W,H,pts=[];function rsz(){W=cv.width=window.innerWidth;H=cv.height=window.innerHeight;}rsz();window.addEventListener('resize',rsz);class Dot{constructor(){this.reset();}reset(){this.x=Math.random()*W;this.y=Math.random()*H;this.vx=(Math.random()-.5)*.38;this.vy=(Math.random()-.5)*.38;this.r=Math.random()*1.4+.4;this.cy=Math.random()>.45;this.a=Math.random()*.35+.1;}step(){this.x+=this.vx;this.y+=this.vy;if(this.x<0||this.x>W||this.y<0||this.y>H)this.reset();}draw(){cx.beginPath();cx.arc(this.x,this.y,this.r,0,Math.PI*2);cx.fillStyle=this.cy?'rgba(0,245,255,'+this.a+')':'rgba(255,0,229,'+this.a+')';cx.fill();}}for(let i=0;i<55;i++)pts.push(new Dot());(function loop(){cx.clearRect(0,0,W,H);for(let i=0;i<pts.length;i++){pts[i].step();pts[i].draw();for(let j=i+1;j<pts.length;j++){const dx=pts[i].x-pts[j].x,dy=pts[i].y-pts[j].y,d=Math.sqrt(dx*dx+dy*dy);if(d<90){cx.beginPath();cx.moveTo(pts[i].x,pts[i].y);cx.lineTo(pts[j].x,pts[j].y);cx.strokeStyle='rgba(0,245,255,'+(1-d/90)*.065+')';cx.lineWidth=.5;cx.stroke();}}}requestAnimationFrame(loop);})();</script></body></html>`;

const getHeroHtml = (imageSrc: string) => `<!DOCTYPE html><html lang="no"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@700;900&family=Exo+2:ital,wght@0,300;0,400;1,300&display=swap" rel="stylesheet"><style>*{box-sizing:border-box;margin:0;padding:0}html,body{height:480px;overflow:hidden}body{background:#000508;font-family:'Exo 2',sans-serif;color:#F0F8FF}#r{position:relative;height:480px;overflow:hidden;display:grid;grid-template-columns:54% 46%;align-items:center;padding:36px 24px 28px}canvas{position:absolute;inset:0;z-index:0;pointer-events:none}#vig{position:absolute;inset:0;background:radial-gradient(ellipse at 50% 50%,transparent 40%,rgba(0,2,8,.92) 100%);z-index:1;pointer-events:none}.rv{opacity:0;animation:rv .7s cubic-bezier(.22,1,.36,1) var(--d,0ms) both}@keyframes rv{from{opacity:0;transform:translateY(18px)}to{opacity:1;transform:none}}#lc{position:relative;z-index:4;display:flex;flex-direction:column;padding-right:10px}.badge{display:inline-block;font-family:'Orbitron',sans-serif;font-size:8px;letter-spacing:.25em;color:rgba(0,245,255,.6);border:1px solid rgba(0,245,255,.2);padding:5px 11px;border-radius:20px;background:rgba(0,245,255,.04);text-transform:uppercase}h1{font-family:'Orbitron',sans-serif;font-size:clamp(22px,5vw,40px);font-weight:900;line-height:1.1;letter-spacing:-.01em;margin-top:13px}.g{background:linear-gradient(135deg,#00F5FF 0%,#7DF9FF 40%,#FF2D78 100%);-webkit-background-clip:text;background-clip:text;color:transparent}.sub{color:rgba(180,210,240,.36);font-size:11px;font-weight:300;line-height:1.65;margin-top:11px;font-style:italic}.cta{display:inline-block;background:linear-gradient(135deg,#00D4E8,#00F5FF);color:#000814;font-family:'Orbitron',sans-serif;font-size:9px;font-weight:700;letter-spacing:.1em;border:none;padding:11px 20px;border-radius:6px;cursor:pointer;position:relative;overflow:hidden;margin-top:17px;transition:transform .2s,box-shadow .2s}.cta:hover{transform:translateY(-2px);box-shadow:0 8px 28px rgba(0,245,255,.4)}.stats{display:flex;align-items:center;margin-top:20px}.sn{font-family:'Orbitron',sans-serif;font-size:17px;font-weight:900;color:#00F5FF;text-shadow:0 0 12px rgba(0,245,255,.5)}.sl{font-size:8px;color:rgba(150,190,220,.38);letter-spacing:.08em;text-transform:uppercase;margin-top:3px}.sdiv{width:1px;height:28px;background:rgba(255,255,255,.1);margin:0 12px}#rc{position:relative;z-index:4;display:flex;align-items:center;justify-content:center;height:100%}.cglow{position:absolute;width:200px;height:200px;border-radius:50%;background:radial-gradient(circle,rgba(0,245,255,.17) 0%,transparent 70%)}.cbeam{position:absolute;width:2px;height:400%;top:-150%;left:50%;transform:translateX(-50%);background:linear-gradient(180deg,transparent,rgba(0,245,255,.18) 40%,transparent);filter:blur(4px)}#nong{animation:fl 4s ease-in-out infinite;filter:drop-shadow(0 0 18px rgba(200,126,24,0.35));z-index:2;position:relative;max-height:100%;max-width:100%;object-fit:contain}@keyframes fl{0%,100%{transform:translateY(0)}50%{transform:translateY(-8px)}}.fb{position:absolute;background:rgba(2,5,16,.85);border:1px solid rgba(0,245,255,.22);border-radius:20px;padding:4px 10px;font-size:9px;font-weight:600;color:rgba(200,240,255,.8);white-space:nowrap;z-index:3;font-family:'Exo 2',sans-serif}#fa{top:8%;right:2%;animation:fba 4s ease infinite}#fb{top:36%;right:-2%;animation:fbb 5s ease infinite .5s}#fc{bottom:12%;right:4%;animation:fba 3.5s ease infinite 1s}#fd{top:14%;left:-2%;animation:fbb 4.5s ease infinite .25s}@keyframes fba{0%,100%{transform:translateY(0) rotate(-2deg)}50%{transform:translateY(-5px) rotate(1deg)}}@keyframes fbb{0%,100%{transform:translateY(0) rotate(1deg)}50%{transform:translateY(-4px) rotate(-2deg)}}</style></head><body><div id="r"><canvas id="pc"></canvas><div id="vig"></div><div id="lc"><span class="rv badge" style="--d:0ms">V5 &middot; NESTE GENERASJON</span><h1><span class="rv" style="--d:180ms">Best&aring;</span><br><span class="rv g" style="--d:360ms">teoripøven</span><br><span class="rv" style="--d:540ms">første gang.</span></h1><p class="rv sub" style="--d:720ms">Norsk trafikkteori forklart p&aring; thai<br>med AI-l&aelig;rer, quiz og video.</p><button class="rv cta" style="--d:900ms">Last ned gratis &#8599;</button><div class="rv stats" style="--d:1100ms"><div><div class="sn" id="s1">0</div><div class="sl">Studenter</div></div><div class="sdiv"></div><div><div class="sn" id="s2">0</div><div class="sl">% Best&aring;tt</div></div><div class="sdiv"></div><div><div class="sn" id="s3">0</div><div class="sl">Leksjoner</div></div></div></div><div id="rc" class="rv" style="--d:280ms"><div class="cglow"></div><div class="cbeam"></div><div class="fb" id="fa">&#9889; 8/8 Quiz</div><div class="fb" id="fb">&#128293; 7 dager</div><div class="fb" id="fc">&#127942; Rank #1</div><div class="fb" id="fd">&#127481;&#127469; &#8594; &#127475;&#127476;</div><img id="nong" src="${imageSrc}" /></div></div><script>setTimeout(function(){var targets=[[document.getElementById('s1'),12450,''],[document.getElementById('s2'),94,'%'],[document.getElementById('s3'),48,'']];targets.forEach(function(item){var el=item[0],t=item[1],sfx=item[2],n=0;var iv=setInterval(function(){n+=Math.ceil((t-n)/8);el.textContent=(n>=t?t:n).toLocaleString('no')+sfx;if(n>=t)clearInterval(iv);},50);});},1200);var cv=document.getElementById('pc'),cx=cv.getContext('2d'),W,H,ps=[];function rsz(){W=cv.width=window.innerWidth;H=cv.height=480;}rsz();window.addEventListener('resize',rsz);function P(){this.reset(true);}P.prototype.reset=function(i){this.x=Math.random()*W;this.y=Math.random()*H;this.vx=(Math.random()-.5)*.18;this.vy=(Math.random()-.5)*.18;this.r=Math.random()*1.8+.5;this.c=Math.random()>.6?'rgba(0,245,255,':'rgba(100,80,255,';this.a=Math.random()*.13+.03;this.life=i?Math.random()*400:0;this.mx=Math.random()*350+180;};P.prototype.step=function(){this.x+=this.vx;this.y+=this.vy;this.life++;if(this.life>this.mx||this.x<0||this.x>W||this.y<0||this.y>H)this.reset(false);};P.prototype.draw=function(){var p=Math.sin(Math.PI*this.life/this.mx);cx.beginPath();cx.arc(this.x,this.y,this.r,0,Math.PI*2);cx.fillStyle=this.c+(this.a*p)+')';cx.fill();};for(var i=0;i<22;i++)ps.push(new P());(function loop(){cx.clearRect(0,0,W,H);ps.forEach(function(p){p.step();p.draw();});requestAnimationFrame(loop);})();</script></body></html>`;

// ── Social links ─────────────────────────────────────────────────────────────
const FACEBOOK_URL   = 'https://www.facebook.com/profile.php?id=61565991554372';
const TIKTOK_URL     = 'https://www.tiktok.com/@thai2drive.no';
const YOUTUBE_CHAN   = 'https://www.youtube.com/channel/UCe965d1YB8Ds7mPSa5LOvRA';

// Facebook Page Plugin iframe (works cross-origin in browsers)
const FB_EMBED_SRC =
  'https://www.facebook.com/plugins/page.php' +
  '?href=https%3A%2F%2Fwww.facebook.com%2Fprofile.php%3Fid%3D61565991554372' +
  '&tabs=timeline&width=320&height=480' +
  '&small_header=true&adapt_container_width=true&hide_cover=false&show_facepile=false';

// YouTube latest-uploads embed (channel RSS → embed via YouTube channel)
const YT_EMBED_SRC =
  'https://www.youtube.com/embed?listType=user_uploads' +
  '&list=UCe965d1YB8Ds7mPSa5LOvRA&rel=0&modestbranding=1';

// ── Web-only iframe helper ────────────────────────────────────────────────────
function WebIframe({ src, height }: { src: string; height: number }) {
  if (Platform.OS !== 'web') return null;
  return React.createElement('iframe', {
    src,
    width: '100%',
    height,
    style: {
      border: 'none',
      borderRadius: 12,
      display: 'block',
      background: 'transparent',
    },
    allow: 'accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture',
    allowFullScreen: true,
    loading: 'lazy',
  });
}

// ── Translations ──────────────────────────────────────────────────────────────
const TR: Record<string, Record<string, string>> = {
  no: {
    title: 'Følg Thai2Drive',
    subtitle: 'Videoer, tips og trafikklærdom på sosiale medier',
    follow: 'Følg oss',
    open: 'Åpne',
    watchVideos: 'Se videoer',
    ytTitle: 'YouTube-kanal',
    ytDesc: 'Fullstendige video­forklaringer av trafikkteori, vikeplikt, bremselengde og mer — på norsk og thai.',
    fbTitle: 'Facebook-side',
    fbDesc: 'Oppdateringer, læringsinnhold og fellesskap for Thai-studenter som tar norsk lappen.',
    ttTitle: 'TikTok',
    ttDesc: 'Korte tips fra Michael Trafikklærer — perfekt for en rask repetisjon i hverdagen.',
    ytSubs: 'Videoer',
    fbLikes: 'Følgere',
    ttFollowers: 'Følgere',
    share: 'Del med venner',
    embedded: 'Innebygd visning',
    tapToOpen: 'Trykk for å åpne',
  },
  th: {
    title: 'ติดตาม Thai2Drive',
    subtitle: 'วิดีโอ เคล็ดลับ และความรู้จราจรบนโซเชียลมีเดีย',
    follow: 'ติดตาม',
    open: 'เปิด',
    watchVideos: 'ดูวิดีโอ',
    ytTitle: 'YouTube Channel',
    ytDesc: 'วิดีโออธิบายทฤษฎีจราจรแบบเต็มเรื่อง — วิกพลิกต์ ระยะเบรก และอีกมาก เป็นภาษานอร์เวย์และภาษาไทย',
    fbTitle: 'Facebook Page',
    fbDesc: 'อัปเดตและคอมมูนิตี้สำหรับนักเรียนไทยที่สอบใบขับขี่นอร์เวย์',
    ttTitle: 'TikTok',
    ttDesc: 'เคล็ดลับสั้นจากครูไมเคิล — เหมาะสำหรับทบทวนเร็วๆ ในชีวิตประจำวัน',
    ytSubs: 'วิดีโอ',
    fbLikes: 'ผู้ติดตาม',
    ttFollowers: 'ผู้ติดตาม',
    share: 'แชร์กับเพื่อน',
    embedded: 'ดูแบบฝัง',
    tapToOpen: 'แตะเพื่อเปิด',
  },
  en: {
    title: 'Follow Thai2Drive',
    subtitle: 'Videos, tips and traffic theory on social media',
    follow: 'Follow',
    open: 'Open',
    watchVideos: 'Watch videos',
    ytTitle: 'YouTube Channel',
    ytDesc: 'Full video explanations of traffic theory, right-of-way, braking distance and more — in Norwegian and Thai.',
    fbTitle: 'Facebook Page',
    fbDesc: 'Updates, learning content and community for Thai students taking the Norwegian driving test.',
    ttTitle: 'TikTok',
    ttDesc: 'Quick tips from Michael the Driving Instructor — perfect for a fast daily review.',
    ytSubs: 'Videos',
    fbLikes: 'Followers',
    ttFollowers: 'Followers',
    share: 'Share with friends',
    embedded: 'Embedded view',
    tapToOpen: 'Tap to open',
    quizTitle: 'Theory Quiz',
    quizDesc: 'Test your Norwegian traffic theory knowledge — 8 questions, neon design, instant feedback.',
    quizPlay: 'Play Quiz',
    quizWeb: 'Web only — open in browser to play',
  },
};

// extra keys for no/th
(TR.no as Record<string, string>).quizTitle = 'Teori Quiz';
(TR.no as Record<string, string>).quizDesc = 'Test teorikunnskapene dine — 8 spørsmål med neon-design og øyeblikkelig tilbakemelding.';
(TR.no as Record<string, string>).quizPlay = 'Spill Quiz';
(TR.no as Record<string, string>).quizWeb = 'Kun web — åpne i nettleser for å spille';
(TR.th as Record<string, string>).quizTitle = 'ควิซทฤษฎี';
(TR.th as Record<string, string>).quizDesc = 'ทดสอบความรู้ทฤษฎีจราจร — 8 คำถาม ดีไซน์นีออน พร้อมคำตอบทันที';
(TR.th as Record<string, string>).quizPlay = 'เล่นควิซ';
(TR.th as Record<string, string>).quizWeb = 'เฉพาะเว็บ — เปิดในเบราว์เซอร์เพื่อเล่น';

// ── Animated platform card ────────────────────────────────────────────────────
function PlatformCard({
  children,
  onPress,
}: {
  children: React.ReactNode;
  onPress: () => void;
}) {
  const scale = useRef(new Animated.Value(1)).current;
  const pressIn  = () => Animated.spring(scale, { toValue: 0.97, useNativeDriver: true, speed: 50, bounciness: 0 }).start();
  const pressOut = () => Animated.spring(scale, { toValue: 1,    useNativeDriver: true, speed: 40, bounciness: 5 }).start();

  return (
    <Animated.View style={{ transform: [{ scale }] }}>
      <TouchableOpacity
        onPress={onPress}
        onPressIn={pressIn}
        onPressOut={pressOut}
        activeOpacity={1}
      >
        {children}
      </TouchableOpacity>
    </Animated.View>
  );
}

// ── Main screen ───────────────────────────────────────────────────────────────
export default function SocialScreen() {
  const router = useRouter();
  const { language, colors } = useAppStore();
  const c = colors;
  const isDark = c.bg === '#0F172A' || c.bg === '#0B1222';
  const t = TR[language] || TR.en;

  const open = (url: string) => Linking.openURL(url);

  return (
    <SafeAreaView style={[st.safe, { backgroundColor: c.bg }]}>
      {/* Header */}
      <View style={[st.header, { borderBottomColor: c.divider }]}>
        <TouchableOpacity onPress={() => router.back()} style={st.backBtn}
          hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}>
          <Ionicons name="arrow-back" size={24} color={c.text} />
        </TouchableOpacity>
        <View style={{ flex: 1, marginLeft: 12 }}>
          <Text style={[st.headerTitle, { color: c.text }]}>{t.title}</Text>
          <Text style={[st.headerSub, { color: c.textMuted }]}>{t.subtitle}</Text>
        </View>
      </View>

      <ScrollView contentContainerStyle={st.scroll} showsVerticalScrollIndicator={false}>

        {/* ── YOUTUBE ─────────────────────────────────────────────────────── */}
        <View style={st.section}>
          {/* Branded banner */}
          <LinearGradient
            colors={['#1A0000', '#CC0000', '#FF4444']}
            start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
            style={st.platformBanner}
          >
            <View style={st.bannerInner}>
              <View style={st.platformIconWrap}>
                {/* YouTube play button */}
                <View style={[st.ytPlay, { backgroundColor: '#fff' }]}>
                  <Ionicons name="logo-youtube" size={28} color="#FF0000" />
                </View>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={st.platformName}>YouTube</Text>
                <Text style={st.platformHandle}>Thai2Drive</Text>
              </View>
              <TouchableOpacity
                style={st.followBtn}
                onPress={() => open(YOUTUBE_CHAN)}
              >
                <Text style={[st.followBtnText, { color: '#CC0000' }]}>{t.watchVideos}</Text>
              </TouchableOpacity>
            </View>
          </LinearGradient>

          {/* Description card */}
          <View style={[st.descCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={[st.descText, { color: c.textMuted }]}>{t.ytDesc}</Text>
          </View>

          {/* Embedded player (web only) — wraps in a pressable fallback on native */}
          {Platform.OS === 'web' ? (
            <View style={[st.embedWrap, { backgroundColor: '#000', borderColor: '#333' }]}>
              <WebIframe src={YT_EMBED_SRC} height={200} />
            </View>
          ) : (
            <PlatformCard onPress={() => open(YOUTUBE_CHAN)}>
              <LinearGradient
                colors={['#1a0000', '#300000']}
                style={[st.nativePreview, { borderColor: '#CC0000' }]}
              >
                <Ionicons name="logo-youtube" size={48} color="#FF0000" />
                <Text style={[st.nativePreviewText, { color: '#fff' }]}>{t.tapToOpen}</Text>
              </LinearGradient>
            </PlatformCard>
          )}

          {/* Open button */}
          <TouchableOpacity
            style={[st.openBtn, { backgroundColor: '#FF0000' }]}
            onPress={() => open(YOUTUBE_CHAN)}
          >
            <Ionicons name="logo-youtube" size={18} color="#fff" />
            <Text style={st.openBtnText}>{t.watchVideos}</Text>
            <Ionicons name="open-outline" size={16} color="rgba(255,255,255,0.7)" />
          </TouchableOpacity>
        </View>

        {/* ── FACEBOOK ────────────────────────────────────────────────────── */}
        <View style={st.section}>
          <LinearGradient
            colors={['#001A40', '#0866FF', '#4299FF']}
            start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
            style={st.platformBanner}
          >
            <View style={st.bannerInner}>
              <View style={st.platformIconWrap}>
                <View style={[st.ytPlay, { backgroundColor: '#fff' }]}>
                  <Ionicons name="logo-facebook" size={28} color="#0866FF" />
                </View>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={st.platformName}>Facebook</Text>
                <Text style={st.platformHandle}>Thai2Drive</Text>
              </View>
              <TouchableOpacity
                style={st.followBtn}
                onPress={() => open(FACEBOOK_URL)}
              >
                <Text style={[st.followBtnText, { color: '#0866FF' }]}>{t.follow}</Text>
              </TouchableOpacity>
            </View>
          </LinearGradient>

          <View style={[st.descCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={[st.descText, { color: c.textMuted }]}>{t.fbDesc}</Text>
          </View>

          {/* Facebook Page Plugin — web only */}
          {Platform.OS === 'web' ? (
            <View style={[st.embedWrap, { backgroundColor: isDark ? '#18191A' : '#f0f2f5', borderColor: '#0866FF' }]}>
              <WebIframe src={FB_EMBED_SRC} height={480} />
            </View>
          ) : (
            <PlatformCard onPress={() => open(FACEBOOK_URL)}>
              <LinearGradient
                colors={['#001a40', '#001e4a']}
                style={[st.nativePreview, { borderColor: '#0866FF' }]}
              >
                <Ionicons name="logo-facebook" size={48} color="#0866FF" />
                <Text style={[st.nativePreviewText, { color: '#fff' }]}>{t.tapToOpen}</Text>
              </LinearGradient>
            </PlatformCard>
          )}

          <TouchableOpacity
            style={[st.openBtn, { backgroundColor: '#0866FF' }]}
            onPress={() => open(FACEBOOK_URL)}
          >
            <Ionicons name="logo-facebook" size={18} color="#fff" />
            <Text style={st.openBtnText}>{t.follow} · Thai2Drive</Text>
            <Ionicons name="open-outline" size={16} color="rgba(255,255,255,0.7)" />
          </TouchableOpacity>
        </View>

        {/* ── TIKTOK ──────────────────────────────────────────────────────── */}
        <View style={st.section}>
          <LinearGradient
            colors={['#010101', '#161616', '#2a2a2a']}
            start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
            style={st.platformBanner}
          >
            <View style={st.bannerInner}>
              <View style={st.platformIconWrap}>
                <View style={[st.ytPlay, { backgroundColor: '#000' }]}>
                  {/* TikTok logo: a musical note in brand colors */}
                  <Text style={{ fontSize: 24 }}>♪</Text>
                </View>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={st.platformName}>TikTok</Text>
                <Text style={[st.platformHandle, { color: '#69C9D0' }]}>@thai2drive.no</Text>
              </View>
              <TouchableOpacity
                style={[st.followBtn, { backgroundColor: '#FE2C55' }]}
                onPress={() => open(TIKTOK_URL)}
              >
                <Text style={[st.followBtnText, { color: '#fff' }]}>{t.follow}</Text>
              </TouchableOpacity>
            </View>
          </LinearGradient>

          <View style={[st.descCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={[st.descText, { color: c.textMuted }]}>{t.ttDesc}</Text>
          </View>

          {/* TikTok: no public profile embed API — premium card + link */}
          <PlatformCard onPress={() => open(TIKTOK_URL)}>
            <View style={[st.ttPreview, { borderColor: '#FE2C55' }]}>
              {/* Glowing lines behind */}
              <View style={st.ttGlow1} />
              <View style={st.ttGlow2} />
              <View style={st.ttContent}>
                <View style={st.ttHandleRow}>
                  <View style={st.ttIcon}>
                    <Text style={{ fontSize: 28 }}>♪</Text>
                  </View>
                  <View>
                    <Text style={st.ttHandle}>@thai2drive.no</Text>
                    <Text style={[st.ttSub, { color: '#94A3B8' }]}>TikTok</Text>
                  </View>
                </View>

                <View style={st.ttStatsRow}>
                  <View style={st.ttStat}>
                    <Text style={st.ttStatNum}>🎬</Text>
                    <Text style={st.ttStatLbl}>Reels</Text>
                  </View>
                  <View style={[st.ttStatDivider]} />
                  <View style={st.ttStat}>
                    <Text style={st.ttStatNum}>🚗</Text>
                    <Text style={st.ttStatLbl}>Tips</Text>
                  </View>
                  <View style={st.ttStatDivider} />
                  <View style={st.ttStat}>
                    <Text style={st.ttStatNum}>📖</Text>
                    <Text style={st.ttStatLbl}>Teori</Text>
                  </View>
                </View>

                <View style={[st.ttOpenRow]}>
                  <Text style={st.ttOpenLabel}>{t.tapToOpen}</Text>
                  <Ionicons name="arrow-forward-circle" size={22} color="#FE2C55" />
                </View>
              </View>
            </View>
          </PlatformCard>

          <TouchableOpacity
            style={[st.openBtn, { backgroundColor: '#FE2C55' }]}
            onPress={() => open(TIKTOK_URL)}
          >
            <Text style={{ fontSize: 16 }}>♪</Text>
            <Text style={st.openBtnText}>@thai2drive.no</Text>
            <Ionicons name="open-outline" size={16} color="rgba(255,255,255,0.7)" />
          </TouchableOpacity>
        </View>

        {/* ── NEON QUIZ ───────────────────────────────────────────────────── */}
        <View style={st.section}>
          <LinearGradient
            colors={['#020510', '#040820', '#060B24']}
            start={{ x: 0, y: 0 }} end={{ x: 1, y: 0 }}
            style={[st.platformBanner, { borderWidth: 1, borderColor: 'rgba(0,245,255,0.25)' }]}
          >
            <View style={st.bannerInner}>
              <View style={st.platformIconWrap}>
                <View style={[st.ytPlay, { backgroundColor: '#020510', borderWidth: 1.5, borderColor: '#00F5FF' }]}>
                  <Text style={{ fontSize: 22 }}>⚡</Text>
                </View>
              </View>
              <View style={{ flex: 1 }}>
                <Text style={[st.platformName, { color: '#00F5FF' }]}>{t.quizTitle}</Text>
                <Text style={[st.platformHandle, { color: 'rgba(0,245,255,0.5)' }]}>Thai2Drive</Text>
              </View>
              {Platform.OS === 'web' && (
                <View style={[st.followBtn, { backgroundColor: 'transparent', borderWidth: 1, borderColor: '#00F5FF' }]}>
                  <Text style={[st.followBtnText, { color: '#00F5FF' }]}>{t.quizPlay}</Text>
                </View>
              )}
            </View>
          </LinearGradient>

          <View style={[st.descCard, { backgroundColor: c.card, borderColor: c.cardBorder }]}>
            <Text style={[st.descText, { color: c.textMuted }]}>{t.quizDesc}</Text>
          </View>

          {Platform.OS === 'web' ? (
            <View style={[st.embedWrap, { backgroundColor: '#020510', borderColor: 'rgba(0,245,255,0.2)', borderLeftWidth: 1, borderRightWidth: 1 }]}>
              {React.createElement('iframe', {
                srcDoc: QUIZ_HTML,
                width: '100%',
                height: 560,
                style: { border: 'none', display: 'block' },
                sandbox: 'allow-scripts allow-same-origin',
              })}
            </View>
          ) : (
            <View style={[st.nativePreview, { backgroundColor: '#020510', borderColor: '#00F5FF', borderLeftWidth: 1, borderRightWidth: 1, height: 140 }]}>
              <Text style={{ fontSize: 36 }}>⚡</Text>
              <Text style={{ color: '#00F5FF', fontSize: 14, fontWeight: '700', marginTop: 6 }}>{t.quizTitle}</Text>
              <Text style={{ color: 'rgba(0,245,255,0.45)', fontSize: 12, marginTop: 4 }}>{t.quizWeb}</Text>
            </View>
          )}
        </View>

        {/* ── Anime Hero — $1M design ──────────────────────────────────────── */}
        <View style={[st.section, { marginTop: 4 }]}>
          {Platform.OS === 'web' ? (() => {
            const imageUri = Image.resolveAssetSource(maleeCasual).uri;
            return (
              <View style={[st.embedWrap, { backgroundColor: '#000508', borderColor: 'rgba(0,245,255,0.15)', borderLeftWidth: 1, borderRightWidth: 1 }]}>
                {React.createElement('iframe', {
                  srcDoc: getHeroHtml(imageUri),
                  width: '100%',
                  height: 480,
                  style: { border: 'none', display: 'block' },
                  sandbox: 'allow-scripts allow-same-origin',
                })}
              </View>
            );
          })() : (
            <View style={[st.nativePreview, { backgroundColor: '#000508', borderColor: '#00F5FF', borderLeftWidth: 1, borderRightWidth: 1, height: 180 }]}>
              <Text style={{ fontSize: 48 }}>⚡</Text>
              <Text style={{ color: '#00F5FF', fontSize: 16, fontWeight: '700', letterSpacing: 2 }}>THAI2DRIVE</Text>
              <Text style={{ color: 'rgba(0,245,255,0.45)', fontSize: 12, marginTop: 4 }}>
                {language === 'th' ? 'สอบผ่านครั้งแรก' : language === 'en' ? 'Pass your first try' : 'Bestå første gang'}
              </Text>
            </View>
          )}
        </View>

        {/* ── All platforms quick-links ────────────────────────────────────── */}
        <View style={[st.allRow, { borderColor: c.divider }]}>
          <Text style={[st.allRowLabel, { color: c.textMuted }]}>
            {language === 'th' ? 'ลิงก์ด่วน' : language === 'en' ? 'Quick links' : 'Hurtiglenker'}
          </Text>
          <View style={st.allBtns}>
            <TouchableOpacity style={[st.allBtn, { backgroundColor: '#FF0000' }]} onPress={() => open(YOUTUBE_CHAN)}>
              <Ionicons name="logo-youtube" size={20} color="#fff" />
            </TouchableOpacity>
            <TouchableOpacity style={[st.allBtn, { backgroundColor: '#0866FF' }]} onPress={() => open(FACEBOOK_URL)}>
              <Ionicons name="logo-facebook" size={20} color="#fff" />
            </TouchableOpacity>
            <TouchableOpacity style={[st.allBtn, { backgroundColor: '#010101', borderWidth: 1, borderColor: '#FE2C55' }]} onPress={() => open(TIKTOK_URL)}>
              <Text style={{ fontSize: 18 }}>♪</Text>
            </TouchableOpacity>
          </View>
        </View>

      </ScrollView>
    </SafeAreaView>
  );
}

// ── Styles ────────────────────────────────────────────────────────────────────
const st = StyleSheet.create({
  safe: { flex: 1 },
  header: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 20, paddingVertical: 16, borderBottomWidth: 1,
  },
  backBtn: { padding: 4 },
  headerTitle: { fontSize: 20, fontWeight: '800' },
  headerSub: { fontSize: 12, marginTop: 2 },
  scroll: { padding: 16, paddingBottom: 100 },

  section: { marginBottom: 28 },

  platformBanner: {
    borderRadius: 16, marginBottom: 0,
    overflow: 'hidden',
    borderBottomLeftRadius: 0, borderBottomRightRadius: 0,
  },
  bannerInner: {
    flexDirection: 'row', alignItems: 'center',
    paddingHorizontal: 16, paddingVertical: 14, gap: 12,
  },
  platformIconWrap: { },
  ytPlay: {
    width: 46, height: 46, borderRadius: 12,
    justifyContent: 'center', alignItems: 'center',
  },
  platformName: { color: '#fff', fontSize: 16, fontWeight: '800' },
  platformHandle: { color: 'rgba(255,255,255,0.7)', fontSize: 13, marginTop: 1 },
  followBtn: {
    backgroundColor: '#fff',
    paddingHorizontal: 14, paddingVertical: 8,
    borderRadius: 20,
  },
  followBtnText: { fontSize: 13, fontWeight: '800' },

  descCard: {
    padding: 14,
    borderLeftWidth: 1, borderRightWidth: 1,
  },
  descText: { fontSize: 13, lineHeight: 20 },

  embedWrap: {
    borderLeftWidth: 1, borderRightWidth: 1,
    overflow: 'hidden',
  },
  nativePreview: {
    height: 120, borderRadius: 0,
    borderLeftWidth: 1, borderRightWidth: 1,
    justifyContent: 'center', alignItems: 'center', gap: 8,
  },
  nativePreviewText: { fontSize: 14, opacity: 0.6 },

  openBtn: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'center',
    gap: 8, paddingVertical: 13, borderRadius: 12,
    marginTop: 10,
  },
  openBtnText: { color: '#fff', fontSize: 15, fontWeight: '800', flex: 1 },

  // TikTok custom preview
  ttPreview: {
    height: 160,
    backgroundColor: '#0A0A0A',
    borderLeftWidth: 1, borderRightWidth: 1,
    overflow: 'hidden',
    justifyContent: 'center',
  },
  ttGlow1: {
    position: 'absolute', top: -30, right: -30,
    width: 120, height: 120, borderRadius: 60,
    backgroundColor: 'rgba(105,201,208,0.12)',
  },
  ttGlow2: {
    position: 'absolute', bottom: -20, left: 20,
    width: 100, height: 100, borderRadius: 50,
    backgroundColor: 'rgba(254,44,85,0.10)',
  },
  ttContent: { padding: 20, gap: 12 },
  ttHandleRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  ttIcon: {
    width: 44, height: 44, borderRadius: 22,
    backgroundColor: '#1a1a1a',
    justifyContent: 'center', alignItems: 'center',
    borderWidth: 1.5, borderColor: '#FE2C55',
  },
  ttHandle: { color: '#fff', fontSize: 16, fontWeight: '800' },
  ttSub: { fontSize: 12, marginTop: 1 },
  ttStatsRow: {
    flexDirection: 'row', alignItems: 'center', gap: 0,
  },
  ttStat: { flex: 1, alignItems: 'center', gap: 2 },
  ttStatNum: { fontSize: 18 },
  ttStatLbl: { color: '#64748B', fontSize: 11 },
  ttStatDivider: { width: 1, height: 28, backgroundColor: '#1E293B' },
  ttOpenRow: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'flex-end', gap: 8,
  },
  ttOpenLabel: { color: '#64748B', fontSize: 13 },

  // All platforms row
  allRow: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    borderTopWidth: 1, paddingTop: 20, marginTop: 4,
  },
  allRowLabel: { fontSize: 13 },
  allBtns: { flexDirection: 'row', gap: 10 },
  allBtn: {
    width: 44, height: 44, borderRadius: 22,
    justifyContent: 'center', alignItems: 'center',
  },
});
