"""Web-only Trafikklab (traffic board), step 1: the board only.

Installed into the existing web shell the same way as backend/stopping_distance_web.py.
No mobile, payment, auth or database changes. Texts go through the existing language
system (UI / t() / data-key) with no fallback to another language.
Thai texts are drafts and wait for review ("venter på kontroll").
"""

CSS = r"""
.tl-home {width:100%;display:flex;align-items:center;justify-content:center;gap:14px;margin:0 0 16px;padding:16px;background:#102039;border:2px solid #00F5FF;border-radius:16px;color:#fff;cursor:pointer;font:inherit;text-align:left}
.tl-home strong,.tl-home small {display:block}.tl-home small{color:#bacce2;margin-top:4px}
.tl-home-ico {width:56px;height:56px;flex-shrink:0;border-radius:10px;background:#585e64}
.tl-home:hover{box-shadow:0 0 0 1px #00F5FF;filter:brightness(1.08)}.tl-home:focus-visible{outline:3px solid #00F5FF;outline-offset:3px}
#screenTrafikklab {padding:24px;overflow-y:auto;background:#081426;gap:14px}
.tl-header {display:flex;justify-content:space-between;align-items:center;gap:12px}.tl-header h1{font-size:26px;margin:0}
.tl-btn {all:unset;box-sizing:border-box;cursor:pointer;min-height:44px;padding:10px 14px;border-radius:10px;border:1px solid #426080;background:#11273f;color:#fff;font-weight:700;font-size:15px;display:inline-flex;align-items:center;gap:7px}
.tl-btn:hover:not([disabled]){box-shadow:0 0 0 1px #00F5FF}.tl-btn:focus-visible{outline:3px solid #00F5FF;outline-offset:2px}.tl-btn[disabled]{opacity:.45;cursor:not-allowed}
.tl-tavle {position:relative;display:grid;grid-template-columns:84px minmax(0,1fr);gap:14px;align-items:start}
.tl-rail {display:flex;flex-direction:column;gap:6px;background:#102039;border:1px solid #304e6e;border-radius:14px;padding:8px}
.tl-rail button {all:unset;box-sizing:border-box;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:3px;padding:8px 4px;border-radius:10px;font-size:13px;font-weight:700;color:#fff;text-align:center}
.tl-rail button svg {width:26px;height:26px}
.tl-rail button:hover {background:#18314f}
.tl-rail button[aria-pressed="true"] {background:#006eaa;box-shadow:inset 0 0 0 2px #00F5FF}
.tl-rail button:focus-visible {outline:3px solid #00F5FF}
.tl-rail hr {border:0;border-top:1px solid #304e6e;margin:4px 2px;width:100%}
.tl-boardwrap {position:relative;min-width:0;border-radius:16px;overflow:hidden;background:#dde7cf;box-shadow:0 10px 30px -18px rgba(0,0,0,.6)}
#tlBoard {display:block;width:100%;height:auto;aspect-ratio:1000/700;touch-action:none;user-select:none;-webkit-user-select:none}
.tl-skiltlinje {position:absolute;left:10px;top:10px;display:flex;flex-direction:column;gap:2px;background:rgba(255,255,255,.94);border:1px solid #d6dad2;border-radius:10px;padding:5px 6px 3px;box-shadow:0 4px 14px -8px rgba(0,0,0,.4);color:#17202a;max-width:calc(100% - 140px)}
.tl-skiltlinje .tl-row {display:flex;flex-wrap:wrap;gap:2px}
.tl-skiltlinje button {all:unset;box-sizing:border-box;cursor:pointer;width:34px;height:34px;display:grid;place-items:center;border-radius:7px}
.tl-skiltlinje button svg {width:30px;height:30px}
.tl-skiltlinje button[aria-pressed="true"] {background:#dbe8fb;box-shadow:inset 0 0 0 2px #1d5fb8}
.tl-skiltlinje button:focus-visible {outline:2px solid #1d5fb8}
.tl-skiltlinje small {font-size:11px;color:#4b5560;text-align:center;letter-spacing:.03em}
.tl-vrh {position:absolute;right:10px;top:10px;display:grid;grid-template-columns:repeat(3,38px);grid-template-rows:38px auto;gap:2px;background:rgba(255,255,255,.94);border:1px solid #d6dad2;border-radius:10px;padding:6px;color:#17202a}
.tl-vrh button {all:unset;box-sizing:border-box;cursor:pointer;display:grid;place-items:center;border-radius:7px;font-weight:700;font-size:17px;color:#fff;background:#4f86c9}
.tl-vrh button[aria-pressed="true"] {background:#1d5fb8;box-shadow:0 0 0 2px #0b2f63}
.tl-vrh button:focus-visible {outline:2px solid #0b2f63}
.tl-vrh small {grid-column:1/-1;font-size:11px;text-align:center;color:#4b5560;line-height:1.2;max-width:122px}
.tl-help {position:absolute;max-width:270px;background:#fff;color:#17202a;border-radius:12px;padding:10px 12px;font-size:14px;box-shadow:0 10px 30px -10px rgba(0,0,0,.5);border:1px solid #d6dad2;z-index:6}
.tl-help b {display:block;font-size:16px;margin-bottom:2px}
.tl-pop {position:absolute;left:98px;top:62px;width:300px;max-width:calc(100% - 120px);z-index:5;background:#102039;color:#fff;border:1px solid #304e6e;border-radius:14px;padding:12px;box-shadow:0 14px 34px -18px rgba(0,0,0,.8);display:flex;flex-direction:column;gap:10px}
.tl-pop[hidden] {display:none}
.tl-pop h3 {font-size:17px;margin:0}
.tl-pop .tl-hint {font-size:14px;color:#b8c9df;margin:0}
.tl-seg {display:flex;flex-wrap:wrap;gap:6px}
.tl-seg button {all:unset;box-sizing:border-box;cursor:pointer;min-height:40px;padding:7px 11px;border-radius:9px;border:1px solid #426080;background:#11273f;color:#fff;font-size:14px;font-weight:700;display:inline-flex;align-items:center;gap:7px}
.tl-seg button[aria-pressed="true"] {background:#006eaa;border-color:#00F5FF}
.tl-seg button:focus-visible {outline:3px solid #00F5FF;outline-offset:1px}
.tl-seg svg {width:22px;height:22px}
.tl-lights {display:grid;grid-template-columns:repeat(4,1fr);gap:6px}
.tl-lights button {all:unset;box-sizing:border-box;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:4px;padding:8px 2px;border-radius:10px;border:1px solid #426080;background:#11273f;font-size:12px;text-align:center;font-weight:700}
.tl-lights button[aria-pressed="true"] {border-color:#00F5FF;box-shadow:inset 0 0 0 2px #00F5FF}
.tl-lights svg {width:24px;height:52px}
.tl-check {display:flex;gap:8px;align-items:center;font-size:14px;color:#b8c9df}
.tl-legend {display:flex;gap:14px;flex-wrap:wrap;font-size:14px;color:#b8c9df}
.tl-legend i {display:inline-block;width:12px;height:12px;border-radius:3px;vertical-align:-1px;margin-right:5px;background:rgba(59,190,96,.7)}
.tl-bl {opacity:0}
.v[data-blink="H"] .tl-bl.H,.v[data-blink="V"] .tl-bl.V {animation:tlblk .8s steps(1) infinite}
@keyframes tlblk {0%{opacity:1}50%{opacity:0}}
@media(prefers-reduced-motion:reduce){.v[data-blink="H"] .tl-bl.H,.v[data-blink="V"] .tl-bl.V{animation:none;opacity:1}}
@media(min-width:700px){#app.trafikklab-mode{width:min(1100px,96vw);max-width:none;margin:auto;border-radius:16px}#app.trafikklab-mode .flag-bg{display:none}}
@media(max-width:1060px) and (min-width:700px){.tl-tavle{grid-template-columns:76px minmax(0,1fr)}}
@media(max-width:699px){
  #screenTrafikklab{padding:16px}.tl-header h1{font-size:22px}
  .tl-tavle{grid-template-columns:minmax(0,1fr)}
  .tl-rail{order:2;flex-direction:row;overflow-x:auto;padding:6px}
  .tl-rail button{min-width:62px}.tl-rail hr{display:none}
  .tl-boardwrap{order:1}
  .tl-pop{order:3;position:static;width:auto;max-width:none}
}
@media(max-width:620px){
  .tl-skiltlinje button{width:26px;height:26px}.tl-skiltlinje button svg{width:23px;height:23px}
  .tl-vrh{grid-template-columns:repeat(3,28px);grid-template-rows:28px auto;padding:4px}
  .tl-vrh small{font-size:9px;max-width:92px}
}
"""

HOME = r"""<button class="tl-home" id="trafikklabHomeBtn" onclick="openTrafikklab()"><svg class="tl-home-ico" viewBox="0 0 56 56" aria-hidden="true"><path d="M22 0h12v22h22v12H34v22H22V34H0V22h22z" fill="#6b7279"/><path d="M28 0v22M28 34v22M0 28h22M34 28h22" stroke="#f2c230" stroke-width="2" stroke-dasharray="5 4"/><circle cx="28" cy="46" r="0"/></svg><span><strong data-key="tl_title"></strong><small data-key="tl_home_sub"></small></span></button>"""

SCREEN = r"""
<div class="screen" id="screenTrafikklab">
  <div class="tl-header"><h1 data-key="tl_title"></h1><button class="tl-btn" onclick="closeTrafikklab()" data-key="backhome"></button></div>
  <div class="tl-tavle" id="tlTavle">
    <nav class="tl-rail" id="tlRail" data-label-key="tl_tools">
      <button data-cat="kryss" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 2h6v7h7v6h-7v7H9v-7H2V9h7z" fill="currentColor" opacity=".85"/></svg><span data-key="tl_cat_kryss"></span></button>
      <button data-cat="skilt" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M2 4h20L12 21z" fill="none" stroke="#d7262b" stroke-width="3" stroke-linejoin="round"/></svg><span data-key="tl_cat_skilt"></span></button>
      <button data-cat="lys" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="7" y="1.5" width="10" height="21" rx="3" fill="#2a2f35"/><circle cx="12" cy="6" r="2.4" fill="#e23b2e"/><circle cx="12" cy="12" r="2.4" fill="#f2b01e"/><circle cx="12" cy="18" r="2.4" fill="#2fb35a"/></svg><span data-key="tl_cat_lys"></span></button>
      <button data-cat="biler" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><rect x="6" y="2" width="12" height="20" rx="4" fill="currentColor"/><rect x="8" y="6" width="8" height="4" rx="1" fill="#9fc3e8"/><rect x="8" y="15" width="8" height="3" rx="1" fill="#9fc3e8"/></svg><span data-key="tl_cat_biler"></span></button>
      <hr>
      <button data-cat="tegn" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 20l1-5L16 4l4 4L9 19z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M3 21c3-1 5 0 8-1" stroke="#ff8a4c" stroke-width="2" fill="none"/></svg><span data-key="tl_cat_tegn"></span></button>
      <button data-cat="visk" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M14 3l7 7-9 9H7l-4-4z" fill="none" stroke="currentColor" stroke-width="2" stroke-linejoin="round"/><path d="M9 8l7 7" stroke="currentColor" stroke-width="2"/></svg><span data-key="tl_cat_visk"></span></button>
      <button id="tlUndoBtn" aria-pressed="false"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5L3 10l5 5" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/><path d="M3 10h11a6 6 0 010 12h-3" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round"/></svg><span data-key="tl_undo"></span></button>
    </nav>
    <div class="tl-boardwrap" id="tlBoardWrap">
      <svg id="tlBoard" viewBox="0 0 1000 700" role="img">
        <defs>
          <filter id="tl-goo" filterUnits="userSpaceOnUse" x="-200" y="-200" width="1400" height="1100" color-interpolation-filters="sRGB">
            <feGaussianBlur in="SourceGraphic" stdDeviation="11" result="b"/>
            <feColorMatrix in="b" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 30 -14"/>
          </filter>
          <filter id="tl-gooA" filterUnits="userSpaceOnUse" x="-200" y="-200" width="1400" height="1100" color-interpolation-filters="sRGB">
            <feGaussianBlur in="SourceGraphic" stdDeviation="11" result="b"/>
            <feColorMatrix in="b" type="matrix" values="1 0 0 0 0  0 1 0 0 0  0 0 1 0 0  0 0 0 30 -14" result="g"/>
            <feTurbulence type="fractalNoise" baseFrequency="0.85" numOctaves="2" seed="4" result="n"/>
            <feColorMatrix in="n" type="matrix" values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0.32 0 0 0 -0.08" result="nw"/>
            <feComposite in="nw" in2="g" operator="in" result="nn"/>
            <feMerge><feMergeNode in="g"/><feMergeNode in="nn"/></feMerge>
          </filter>
          <linearGradient id="tl-carShade" x1="0" x2="1" y1="0" y2="0">
            <stop offset="0" stop-color="#000" stop-opacity=".38"/><stop offset=".2" stop-color="#000" stop-opacity="0"/>
            <stop offset=".5" stop-color="#fff" stop-opacity=".24"/><stop offset=".8" stop-color="#000" stop-opacity="0"/>
            <stop offset="1" stop-color="#000" stop-opacity=".38"/>
          </linearGradient>
          <linearGradient id="tl-glass" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#1c2b37"/><stop offset="1" stop-color="#5b7a8d"/></linearGradient>
        </defs>
        <g id="tlLroad"></g><g id="tlLgreen"></g><g id="tlLpark"></g><g id="tlLsigns"></g><g id="tlLmsigns"></g>
        <g id="tlLveh"></g><g id="tlLsel"></g><g id="tlLdraw"></g>
      </svg>
      <div class="tl-skiltlinje" id="tlSkiltlinje"></div>
      <div class="tl-vrh" id="tlVrh" role="group">
        <button data-m="V" aria-pressed="false">V</button>
        <button data-m="R" aria-pressed="false">R</button>
        <button data-m="H" aria-pressed="false">H</button>
        <small data-key="tl_dir"></small>
      </div>
      <div class="tl-help" id="tlHelp" hidden></div>
    </div>
    <div class="tl-pop" id="tlPop" hidden></div>
  </div>
  <div class="tl-legend"><span><i></i><span data-key="tl_green_note"></span></span></div>
</div>
"""

SCRIPT = r"""
Object.assign(UI, {
  tl_title:{no:'Trafikklab',th:'ห้องฝึกจราจร (Trafikklab)',en:'Traffic Lab'},
  tl_home_sub:{no:'Bygg et kryss, sett opp skilt og flytt bilene',th:'สร้างสี่แยก ติดป้าย และเลื่อนรถ',en:'Build a junction, set up signs and move the cars'},
  tl_tools:{no:'Verktøy',th:'เครื่องมือ',en:'Tools'},
  tl_board_label:{no:'Interaktiv trafikktavle',th:'กระดานจราจรแบบโต้ตอบ',en:'Interactive traffic board'},
  tl_cat_kryss:{no:'Kryss',th:'ทางแยก',en:'Junction'},tl_cat_skilt:{no:'Skilt',th:'ป้าย',en:'Signs'},tl_cat_lys:{no:'Lys',th:'ไฟ',en:'Lights'},tl_cat_biler:{no:'Biler',th:'รถ',en:'Cars'},
  tl_cat_tegn:{no:'Tegn',th:'วาด',en:'Draw'},tl_cat_visk:{no:'Visk',th:'ลบ',en:'Erase'},tl_undo:{no:'Angre',th:'เลิกทำ',en:'Undo'},
  tl_lay_vanlig:{no:'Vanlig',th:'ทั่วไป',en:'Standard'},tl_lay_skraa:{no:'Skrått',th:'เฉียง',en:'Skewed'},tl_lay_rund:{no:'Rundkjøring',th:'วงเวียน (rundkjøring)',en:'Roundabout'},
  tl_arms:{no:'Armer',th:'จำนวนแขนทาง',en:'Arms'},tl_arms4:{no:'4 armer',th:'4 แขน',en:'4 arms'},tl_arms3:{no:'3 armer (ta bort øvre)',th:'3 แขน (เอาแขนบนออก)',en:'3 arms (remove the top one)'},
  tl_lanes:{no:'Felt i hver retning',th:'ช่องจราจรในแต่ละทิศทาง',en:'Lanes in each direction'},tl_lane1:{no:'1 felt',th:'1 ช่อง',en:'1 lane'},tl_lane2:{no:'2 felt',th:'2 ช่อง',en:'2 lanes'},
  tl_xwalk:{no:'Gangfelt',th:'ทางม้าลาย (gangfelt)',en:'Pedestrian crossing'},tl_on:{no:'På',th:'เปิด',en:'On'},tl_off:{no:'Av',th:'ปิด',en:'Off'},
  tl_skilt_hint:{no:'Ett trykk setter opp hele krysset:',th:'กดครั้งเดียวตั้งค่าทั้งทางแยก:',en:'One tap sets up the whole junction:'},
  tl_route_q:{no:'Hvor går forkjørsveien?',th:'ถนนสายหลัก (forkjørsvei) ไปทางไหน?',en:'Where does the priority road go?'},
  tl_route_prefix:{no:'Forkjørsvei',th:'ถนนสายหลัก (forkjørsvei)',en:'Priority road'},
  tl_show_green:{no:'Vis grønt område',th:'แสดงพื้นที่สีเขียว',en:'Show green area'},
  tl_place_own:{no:'Plasser selv (kan flyttes):',th:'วางเอง (เลื่อนได้):',en:'Place yourself (can be moved):'},tl_place:{no:'Plasser',th:'วาง',en:'Place'},
  tl_del_sign:{no:'Slett valgt skilt',th:'ลบป้ายที่เลือก',en:'Delete selected sign'},
  tl_light_title:{no:'Lyssignal',th:'สัญญาณไฟจราจร (lyssignal)',en:'Traffic light'},
  tl_light_only:{no:'Lys finnes for vanlig kryss.',th:'สัญญาณไฟมีเฉพาะทางแยกแบบทั่วไป',en:'Traffic lights are available for the standard junction.'},
  tl_make_light:{no:'Sett opp lyskryss',th:'ตั้งค่าทางแยกสัญญาณไฟ',en:'Set up a signalised junction'},
  tl_light_hint:{no:'Velg farge for din vei. Tverrveien får motsatt fase.',th:'เลือกสีไฟสำหรับทางของคุณ ถนนที่ตัดกันจะได้สีตรงข้าม',en:'Choose the colour for your road. The crossing road gets the opposite phase.'},
  tl_cars_title:{no:'Biler og trafikanter',th:'รถและผู้ใช้ถนน',en:'Cars and road users'},
  tl_cars_hint:{no:'Trykk på en bil: blinker høyre. Trykk igjen: venstre. Tredje trykk: av. Dra for å flytte. Dra den runde knappen for å snu.',th:'แตะรถหนึ่งครั้ง: ไฟเลี้ยวขวากะพริบ แตะอีกครั้ง: ไฟเลี้ยวซ้าย แตะครั้งที่สาม: ปิด ลากเพื่อเลื่อน ลากปุ่มกลมเพื่อหมุนรถ',en:'Tap a car: right indicator. Tap again: left. Third tap: off. Drag to move. Drag the round handle to turn.'},
  tl_to_park:{no:'→ parkering',th:'→ ที่จอดรถ',en:'→ parking'},tl_all_park:{no:'Alle tilbake til parkering',th:'เก็บรถทุกคันกลับที่จอด',en:'All back to parking'},
  tl_draw_hint:{no:'Tegn med fingeren eller musa over hele tavlen, som på en whiteboard. Bilene står stille mens du tegner.',th:'วาดด้วยนิ้วหรือเมาส์ทั่วกระดาน เหมือนไวต์บอร์ด รถจะอยู่นิ่งขณะที่คุณวาด',en:'Draw with your finger or mouse anywhere on the board, like a whiteboard. The cars stay still while you draw.'},
  tl_erase_hint:{no:'Dra over en strek for å viske den bort. Trykk «Visk» igjen for å gå tilbake til flytting.',th:'ลากผ่านเส้นเพื่อลบ กดปุ่ม «ลบ» อีกครั้งเพื่อกลับไปเลื่อนรถ',en:'Drag across a line to erase it. Press Erase again to go back to moving.'},
  tl_clear_draw:{no:'Tøm alle tegninger',th:'ล้างภาพวาดทั้งหมด',en:'Clear all drawings'},
  tl_park_label:{no:'Parkering · dra inn i krysset',th:'ที่จอดรถ · ลากเข้าไปในทางแยก',en:'Parking · drag into the junction'},
  tl_green_note:{no:'Grønt: pedagogisk markering, ikke veioppmerking',th:'สีเขียว: เครื่องหมายเพื่อการเรียนรู้ ไม่ใช่เส้นจราจรจริง',en:'Green: teaching highlight, not a road marking'},
  tl_choose:{no:'Velg kryss',th:'เลือกทางแยก',en:'Choose junction'},
  tl_dir:{no:'Din retning (Bil A)',th:'ทิศทางของคุณ (รถ A)',en:'Your direction (Car A)'},
  tl_dir_V:{no:'Venstre',th:'ซ้าย (venstre)',en:'Left'},tl_dir_R:{no:'Rett fram',th:'ตรงไป (rett fram)',en:'Straight ahead'},tl_dir_H:{no:'Høyre',th:'ขวา (høyre)',en:'Right'},
  tl_reg_uregulert:{no:'Uregulert (høyreregelen)',th:'ไม่มีการควบคุม (uregulert, høyreregelen)',en:'Unregulated (right-hand rule)'},
  tl_reg_fare:{no:'Fareskilt: vegkryss',th:'ป้ายเตือน: ทางแยก (vegkryss)',en:'Warning sign: junction'},
  tl_reg_vikeplikt:{no:'Vikeplikt',th:'ให้ทาง (vikeplikt)',en:'Give way'},
  tl_reg_stopp:{no:'Stopp',th:'หยุด (stopp)',en:'Stop'},
  tl_reg_forkjorsvei:{no:'Forkjørsvei',th:'ถนนสายหลัก (forkjørsvei)',en:'Priority road'},
  tl_reg_forkjorskryss:{no:'Forkjørskryss',th:'ทางแยกสายหลัก (forkjørskryss)',en:'Priority junction'},
  tl_reg_lys:{no:'Lyssignal',th:'สัญญาณไฟจราจร (lyssignal)',en:'Traffic light'},
  tl_reg_rundkjoring:{no:'Rundkjøring',th:'วงเวียน (rundkjøring)',en:'Roundabout'},
  tl_sign_822:{no:'Underskilt 822',th:'ป้ายเสริม 822 (underskilt)',en:'Plate 822'},
  tl_sig_red:{no:'rødt',th:'แดง',en:'red'},tl_sig_redyellow:{no:'rødt og gult',th:'แดงและเหลือง',en:'red and yellow'},tl_sig_green:{no:'grønt',th:'เขียว',en:'green'},tl_sig_yellow:{no:'gult',th:'เหลือง',en:'yellow'},
  tl_route_SE:{no:'Svinger mot høyre',th:'เลี้ยวขวา',en:'Turns right'},tl_route_WS:{no:'Svinger mot venstre',th:'เลี้ยวซ้าย',en:'Turns left'},
  tl_route_SN:{no:'Rett fram (din vei)',th:'ตรงไป (ทางของคุณ)',en:'Straight ahead (your road)'},tl_route_WE:{no:'På tvers (du har vikeplikt)',th:'ตัดขวาง (คุณต้องให้ทาง — vikeplikt)',en:'Across (you give way)'},
  tl_help_202_t:{no:'Vikeplikt',th:'ให้ทาง (vikeplikt)',en:'Give way'},tl_help_202:{no:'Du skal slippe fram trafikken på veien du kjører inn på. Vent ved trekantene hvis noen kommer.',th:'คุณต้องให้ทางรถบนถนนที่คุณจะเข้าไป รอที่เครื่องหมายสามเหลี่ยมถ้ามีรถมา',en:'You must let traffic on the road you are joining go first. Wait at the triangles if someone is coming.'},
  tl_help_204_t:{no:'Stopp',th:'หยุด (stopp)',en:'Stop'},tl_help_204:{no:'Du skal stoppe helt ved stopplinjen. Kjør først når veien er fri.',th:'คุณต้องหยุดรถให้สนิทที่เส้นหยุด ออกตัวต่อเมื่อถนนว่างเท่านั้น',en:'You must come to a full stop at the stop line. Only go when the road is clear.'},
  tl_help_206_t:{no:'Forkjørsvei',th:'ถนนสายหลัก (forkjørsvei)',en:'Priority road'},tl_help_206:{no:'Trafikken fra sideveiene har vikeplikt for deg. Følg likevel med.',th:'รถจากถนนสายรองต้องให้ทางคุณ แต่ยังต้องคอยสังเกตรอบตัว',en:'Traffic from the side roads must give way to you. Still stay alert.'},
  tl_help_210_t:{no:'Forkjørskryss',th:'ทางแยกสายหลัก (forkjørskryss)',en:'Priority junction'},tl_help_210:{no:'I krysset som kommer, har trafikken fra sideveiene vikeplikt for deg.',th:'ที่ทางแยกข้างหน้า รถจากถนนสายรองต้องให้ทางคุณ',en:'At the junction ahead, traffic from the side roads must give way to you.'},
  tl_help_822_t:{no:'Underskilt',th:'ป้ายเสริม (underskilt)',en:'Plate'},tl_help_822:{no:'Den tykke streken viser hvor forkjørsveien går gjennom krysset.',th:'เส้นหนาแสดงว่าถนนสายหลักไปทางไหนผ่านทางแยก',en:'The thick line shows where the priority road runs through the junction.'},
  tl_help_402_t:{no:'Rundkjøring',th:'วงเวียน (rundkjøring)',en:'Roundabout'},tl_help_402:{no:'Du har vikeplikt for dem som allerede kjører i ringen.',th:'คุณต้องให้ทางรถที่อยู่ในวงเวียนแล้ว',en:'You must give way to those already in the roundabout.'},
  tl_help_fare_t:{no:'Fareskilt: vegkryss',th:'ป้ายเตือน: ทางแยก (vegkryss)',en:'Warning sign: junction'},tl_help_fare:{no:'Det kommer et kryss. Følg med og vær klar til å vente.',th:'ข้างหน้ามีทางแยก ให้ระวังและเตรียมพร้อมให้ทาง',en:'A junction is coming. Pay attention and be ready to wait.'},
  tl_help_signal_t:{no:'Lyssignal',th:'สัญญาณไฟจราจร (lyssignal)',en:'Traffic light'},tl_help_signal:{no:'Rødt: stopp. Rødt og gult: vent litt til. Grønt: kjør hvis det er trygt. Gult: stopp hvis du kan gjøre det trygt.',th:'แดง: หยุด แดงและเหลือง: รออีกสักครู่ เขียว: ไปได้ถ้าปลอดภัย เหลือง: หยุดถ้าทำได้อย่างปลอดภัย',en:'Red: stop. Red and yellow: wait a little longer. Green: go if it is safe. Yellow: stop if you can do so safely.'},
  tl_veh_A:{no:'Bil A',th:'รถ A',en:'Car A'},tl_veh_B:{no:'Bil B',th:'รถ B',en:'Car B'},tl_veh_C:{no:'Bil C',th:'รถ C',en:'Car C'},tl_veh_P:{no:'Pickup',th:'รถกระบะ',en:'Pickup'},
  tl_veh_R:{no:'Rød sportsbil',th:'รถสปอร์ตสีแดง',en:'Red sports car'},tl_veh_G:{no:'Gul sportsbil',th:'รถสปอร์ตสีเหลือง',en:'Yellow sports car'},tl_veh_T:{no:'Lastebil',th:'รถบรรทุก',en:'Truck'},
  tl_veh_Bu:{no:'Buss',th:'รถบัส',en:'Bus'},tl_veh_Sy:{no:'Syklist',th:'นักปั่นจักรยาน',en:'Cyclist'},tl_veh_F:{no:'Fotgjenger',th:'คนเดินเท้า',en:'Pedestrian'}
});
(function(){
var RAD=Math.PI/180, C={x:500,y:360};
function f(n){return Math.round(n*10)/10;}
function L(id){return document.getElementById('tl'+id);}
var LAY={vanlig:[['E',0],['S',90],['W',180],['N',270]],skraa:[['E',0],['S',62],['W',180],['N',242]],rund:[['E',0],['S',90],['W',180],['N',270]]};
var OPP={green:'red',yellow:'red',redyellow:'red',red:'green'};
var ROUTES=[{id:'SE',arms:['S','E']},{id:'WS',arms:['W','S']},{id:'SN',arms:['S','N']},{id:'WE',arms:['W','E']}];
var HELPCODES=['202','204','206','210','822','402','fare','signal'];
var IMGDIR='/api/assets/trafikklab-car-';
function regName(r){return t('tl_reg_'+r);}
function signName(c){
  if(c==='822')return t('tl_sign_822');if(c==='fare')return t('tl_reg_fare');if(c==='402')return t('tl_reg_rundkjoring');
  return regName({'202':'vikeplikt','204':'stopp','206':'forkjorsvei','210':'forkjorskryss'}[c])+' ('+c+')';
}
function sigName(s){return t('tl_sig_'+s);}
function routeName(id){return t('tl_route_'+id);}
function cap(s){return s.charAt(0).toUpperCase()+s.slice(1);}

function armsOf(st){return LAY[st.layout].filter(function(x){return !(st.arms===3&&x[0]==='N');}).map(function(x){return {id:x[0],a:x[1]};});}
function geo(st){
  if(st.layout==='rund'){var isl=14,W=st.lanes*48+isl,ring=st.lanes*46+8,Rout=st.lanes===1?118:150;return{W:W,isl:isl,ring:ring,Rout:Rout,Rin:Rout-ring,s0:Rout+20};}
  var W2=st.lanes*48;var s0=st.layout==='vanlig'?W2+28:W2/Math.tan(31*RAD)+28;return{W:W2,isl:0,s0:s0};
}
function P(a,x,y){var c=Math.cos(a*RAD),s=Math.sin(a*RAD);return[C.x+c*x-s*y,C.y+s*x+c*y];}
function armMap(st){var o={};armsOf(st).forEach(function(x){o[x.id]=x.a;});return o;}
function regsFor(st){
  if(st.layout==='rund')return['rundkjoring'];
  if(st.layout==='skraa')return['uregulert','forkjorsvei'];
  return st.arms===3?['uregulert','fare','vikeplikt','stopp','lys']:['uregulert','fare','vikeplikt','stopp','forkjorsvei','forkjorskryss','lys'];
}
function routesFor(st){return ROUTES.filter(function(r){return !(st.arms===3&&r.arms.indexOf('N')>=0);});}
function armReg(st,id){
  var R=st.reg,din=(id==='S'||id==='N');
  if(st.layout==='rund')return{line:'vike',signs:['202','402']};
  if(st.layout==='skraa'){if(R==='forkjorsvei'){return st.route.indexOf(id)>=0?{line:null,signs:['206','822']}:{line:'vike',signs:['202']};}return{line:null,signs:[]};}
  switch(R){
    case 'fare':return{line:null,signs:[],far:'fare'};
    case 'vikeplikt':return din?{line:'vike',signs:['202']}:{line:null,signs:[]};
    case 'stopp':return din?{line:'stopp',signs:['204']}:{line:null,signs:[]};
    case 'forkjorsvei':return din?{line:null,signs:['206']}:{line:'vike',signs:['202']};
    case 'forkjorskryss':return din?{line:null,signs:[],far:'210'}:{line:'vike',signs:['202']};
    case 'lys':return{line:'stopp',signs:[],signal:true};
    default:return{line:null,signs:[]};
  }
}
function greenOf(st){
  if(st.layout==='rund')return'ring';
  if(st.layout==='skraa')return st.reg==='forkjorsvei'?st.route:null;
  if(st.reg==='vikeplikt'||st.reg==='stopp')return['W','E'];
  if(st.reg==='forkjorsvei'||st.reg==='forkjorskryss')return['S','N'];
  return null;
}

/* ---------- Road drawing ---------- */
function roadLayer(st){
  var g=geo(st),side='',curb='',asph='';
  function rect(a,w){return '<rect x="0" y="'+(-w)+'" width="900" height="'+(2*w)+'" transform="translate('+C.x+' '+C.y+') rotate('+a+')"/>';}
  armsOf(st).forEach(function(x){side+=rect(x.a,g.W+26);curb+=rect(x.a,g.W+4);asph+=rect(x.a,g.W);});
  if(st.layout==='rund'){side+='<circle cx="'+C.x+'" cy="'+C.y+'" r="'+(g.Rout+26)+'"/>';curb+='<circle cx="'+C.x+'" cy="'+C.y+'" r="'+(g.Rout+4)+'"/>';asph+='<circle cx="'+C.x+'" cy="'+C.y+'" r="'+g.Rout+'"/>';}
  var out='<rect width="1000" height="700" fill="#dde7cf"/><g filter="url(#tl-goo)" fill="#d8dad3">'+side+'</g><g filter="url(#tl-goo)" fill="#b4b8b0">'+curb+'</g><g filter="url(#tl-gooA)" fill="#585e64">'+asph+'</g>';
  if(st.layout==='rund'){
    armsOf(st).forEach(function(x){
      out+='<g transform="translate('+C.x+' '+C.y+') rotate('+x.a+')"><polygon points="'+(g.Rout+4)+','+(-g.isl)+' '+(g.Rout+4)+','+g.isl+' '+(g.Rout+118)+',3 '+(g.Rout+118)+',-3" fill="#dcded7" stroke="#f6f6f1" stroke-width="2.5" stroke-linejoin="round"/></g>';
    });
    out+='<circle cx="'+C.x+'" cy="'+C.y+'" r="'+g.Rin+'" fill="#cbc3b4" stroke="#f6f6f1" stroke-width="3"/><circle cx="'+C.x+'" cy="'+C.y+'" r="'+(g.Rin-13)+'" fill="#9cbf7b"/><circle cx="'+(C.x-8)+'" cy="'+(C.y-6)+'" r="'+Math.max(10,g.Rin*.32)+'" fill="#86ad64" opacity=".8"/>';
  }
  return out;
}
function marksLayer(st){
  var g=geo(st),Y='#f2c230',Wt='#f7f7f2',out='';
  armsOf(st).forEach(function(x){
    var id=x.id,a=x.a,m='',rund=st.layout==='rund';
    var cl0=rund?g.Rout+124:g.s0;
    m+='<line x1="'+f(cl0)+'" y1="0" x2="900" y2="0" stroke="'+Y+'" stroke-width="4" stroke-dasharray="22 16"/>';
    if(st.lanes===2){var yy=g.isl+48;m+='<line x1="'+f(g.s0)+'" y1="'+yy+'" x2="900" y2="'+yy+'" stroke="'+Wt+'" stroke-width="3" stroke-dasharray="14 20"/><line x1="'+f(g.s0)+'" y1="'+(-yy)+'" x2="900" y2="'+(-yy)+'" stroke="'+Wt+'" stroke-width="3" stroke-dasharray="14 20"/>';}
    var gx=rund?g.Rout+40:g.s0+6,GW=38;
    if(st.gangfelt){for(var y=-g.W+5;y<=g.W-12;y+=13){if(rund&&Math.abs(y+3.5)<g.isl+5)continue;m+='<rect x="'+f(gx)+'" y="'+y+'" width="'+GW+'" height="7" fill="'+Wt+'"/>';}}
    var r=armReg(st,id);
    var lx=rund?g.Rout+7:(st.gangfelt?gx+GW+10:g.s0+8);
    var y0=-g.W+3,y1=-g.isl-3;
    if(r.line==='stopp')m+='<rect x="'+f(lx)+'" y="'+y0+'" width="7" height="'+(y1-y0)+'" fill="'+Wt+'"/>';
    if(r.line==='vike'){for(var yv=y0;yv+10<=y1;yv+=14)m+='<polygon points="'+f(lx)+','+yv+' '+f(lx)+','+(yv+10)+' '+f(lx+16)+','+(yv+5)+'" fill="'+Wt+'"/>';}
    out+='<g transform="translate('+C.x+' '+C.y+') rotate('+a+')">'+m+'</g>';
  });
  if(st.layout==='rund'&&st.lanes===2){out+='<circle cx="'+C.x+'" cy="'+C.y+'" r="'+(g.Rout-g.ring/2)+'" fill="none" stroke="'+Wt+'" stroke-width="3" stroke-dasharray="14 18"/>';}
  if(st.layout==='skraa'&&st.reg==='forkjorsvei'){
    var A=armMap(st),p=st.route[0],q=st.route[1];
    if(A[p]!==undefined&&A[q]!==undefined){var a1=P(A[p],g.s0,0),a2=P(A[q],g.s0,0);out+='<path d="M'+f(a1[0])+','+f(a1[1])+' Q'+C.x+','+C.y+' '+f(a2[0])+','+f(a2[1])+'" fill="none" stroke="'+Y+'" stroke-width="4" stroke-dasharray="22 16"/>';}
  }
  return out;
}
function greenLayer(st,showNote){
  var gr=greenOf(st);if(!gr)return'';var g=geo(st),shape='';
  if(gr==='ring'){shape='<circle cx="'+C.x+'" cy="'+C.y+'" r="'+(g.Rout-g.ring/2)+'" fill="none" stroke="#3bbe60" stroke-opacity=".42" stroke-width="'+g.ring+'"/>';}
  else{
    var A=armMap(st),ids=gr.filter(function(i){return A[i]!==undefined;});if(!ids.length)return'';
    function far(i){return P(A[i],900,0);}function near(i){return P(A[i],g.s0,0);}
    var d;
    if(ids.length===1){var a0=far(ids[0]);d='M'+f(a0[0])+','+f(a0[1])+' L'+C.x+','+C.y;}
    else{var a=far(ids[0]),b=near(ids[0]),c=near(ids[1]),e=far(ids[1]);d='M'+f(a[0])+','+f(a[1])+' L'+f(b[0])+','+f(b[1])+' Q'+C.x+','+C.y+' '+f(c[0])+','+f(c[1])+' L'+f(e[0])+','+f(e[1]);}
    shape='<path d="'+d+'" fill="none" stroke="#3bbe60" stroke-opacity=".38" stroke-width="'+(2*g.W+14)+'" stroke-linejoin="round"/>';
  }
  return shape;
}

/* ---------- Signs ---------- */
function signalShape(state,scale){
  scale=scale||1;
  var on={red:state==='red'||state==='redyellow',yellow:state==='yellow'||state==='redyellow',green:state==='green'};
  return '<g transform="scale('+scale+')"><rect x="-8" y="-20" width="16" height="40" rx="5" fill="#24292e" stroke="#fff" stroke-width="1.2"/><circle cy="-11" r="4.6" fill="'+(on.red?'#ff3b30':'#4a4f55')+'"/><circle cy="0" r="4.6" fill="'+(on.yellow?'#ffb21e':'#4a4f55')+'"/><circle cy="11" r="4.6" fill="'+(on.green?'#2fd160':'#4a4f55')+'"/></g>';
}
function signShape(code,o){
  o=o||{};
  switch(code){
    case '202':return '<polygon points="-17,-13 17,-13 0,16" fill="#d7262b" stroke="#fff" stroke-width="1.2" stroke-linejoin="round"/><polygon points="-10.5,-9 10.5,-9 0,9" fill="#fff"/>';
    case '204':{var p=[];for(var i=0;i<8;i++){var tt=(22.5+45*i)*RAD;p.push(f(15*Math.cos(tt))+','+f(15*Math.sin(tt)));}return '<polygon points="'+p.join(' ')+'" fill="#d7262b" stroke="#fff" stroke-width="1.6"/><text x="0" y="3.3" text-anchor="middle" font-size="8.6" font-weight="700" fill="#fff" font-family="Arial,sans-serif">STOPP</text>';}
    case '206':return '<rect x="-11.5" y="-11.5" width="23" height="23" transform="rotate(45)" fill="#fff" stroke="#333" stroke-width="1"/><rect x="-7" y="-7" width="14" height="14" transform="rotate(45)" fill="#f4c20d"/>';
    case '210':return '<polygon points="0,-16 17,13 -17,13" fill="#d7262b" stroke="#fff" stroke-width="1.2" stroke-linejoin="round"/><polygon points="0,-8.5 10.3,8.8 -10.3,8.8" fill="#fff"/><rect x="-1.7" y="-5" width="3.4" height="13" fill="#111"/><rect x="-6" y="2" width="12" height="1.6" fill="#111"/>';
    case 'fare':return '<polygon points="0,-16 17,13 -17,13" fill="#d7262b" stroke="#fff" stroke-width="1.2" stroke-linejoin="round"/><polygon points="0,-8.5 10.3,8.8 -10.3,8.8" fill="#fff"/><path d="M-4.5,-1 L4.5,7.5 M4.5,-1 L-4.5,7.5" stroke="#111" stroke-width="2.2"/>';
    case '402':{var s='<circle r="14" fill="#1f5fbf" stroke="#fff" stroke-width="1.5"/><circle r="7" fill="none" stroke="#fff" stroke-width="2.4"/>';[0,120,240].forEach(function(t0){s+='<g transform="rotate('+t0+') translate(7 0)"><polygon points="-3.6,1 3.6,1 0,-4.6" fill="#fff"/></g>';});return s;}
    case '822':{
      var st=o.st,A=armMap(st),rot=90-A[o.arm],s2='<rect x="-15" y="-11" width="30" height="22" rx="2" fill="#fff" stroke="#222" stroke-width="1.4"/>';
      Object.keys(A).forEach(function(id){var on=st.route.indexOf(id)>=0,t1=(A[id]+rot)*RAD;s2+='<line x1="0" y1="0" x2="'+f(9.5*Math.cos(t1))+'" y2="'+f(8*Math.sin(t1))+'" stroke="#111" stroke-width="'+(on?3.6:1.5)+'" stroke-linecap="round"/>';});
      return s2;}
    case 'signal':return signalShape(o.state||'red',1);
  }
  return'';
}
function mount(inner,x,y,help,extraH){
  extraH=extraH||0;
  return '<g class="tl-sg" data-help="'+help+'" style="cursor:pointer" transform="translate('+f(x)+' '+f(y)+')"><ellipse cx="3" cy="'+(24+extraH)+'" rx="7" ry="2.6" fill="#000" opacity=".18"/><line x1="0" y1="10" x2="0" y2="'+(24+extraH)+'" stroke="#7d8389" stroke-width="2.6"/>'+inner+'</g>';
}
function signsLayer(st){
  var g=geo(st),out='';
  armsOf(st).forEach(function(x){
    var id=x.id,a=x.a,r=armReg(st,id),rund=st.layout==='rund';
    var lx=rund?g.Rout+30:(st.gangfelt?g.s0+60:g.s0+14);
    var xy=P(a,lx+28,-(g.W+32));
    if(r.signal){var ns=(id==='S'||id==='N');var s=ns?st.signal:OPP[st.signal];out+=mount(signalShape(s),xy[0],xy[1]-4,'signal');}
    if(r.signs.length){
      var inner='';r.signs.forEach(function(c,i){inner+='<g transform="translate(0 '+(i*32)+')">'+signShape(c,{st:st,arm:id})+'</g>';});
      out+=mount(inner,xy[0],xy[1],r.signs[0],(r.signs.length-1)*32);
    }
    if(r.far){var fp=P(a,lx+190,-(g.W+32));out+=mount(signShape(r.far),fp[0],fp[1],r.far);}
  });
  return out;
}

/* ---------- Vehicles ---------- */
var VEH=[
 {id:'A',type:'sedan',color:'#2f6fd0',px:44,py:615},{id:'B',type:'suv',color:'#cf3434',px:84,py:615},
 {id:'C',type:'stasjonsvogn',color:'#2b9a57',px:124,py:615},{id:'P',type:'pickup',color:'#e9a514',px:164,py:620},
 {id:'R',type:'sport_rod',px:204,py:615},{id:'G',type:'sport_gul',px:244,py:615},
 {id:'T',type:'lastebil',px:292,py:625},{id:'Bu',type:'buss',px:344,py:625},
 {id:'Sy',type:'sykkel',px:300,py:545},{id:'F',type:'gaaende',px:340,py:548}];
var IMG={sedan:'sedan.webp',suv:'suv.webp',stasjonsvogn:'stasjonsvogn.webp',pickup:'pickup.webp',lastebil:'lastebil.webp',sport_rod:'sport-rod.webp',sport_gul:'sport-gul.webp'};
var SIZE={sedan:[34,78],suv:[37,79],stasjonsvogn:[35,80],pickup:[33,90],sport_rod:[32,74],sport_gul:[32,74],lastebil:[44,130],buss:[44,130],sykkel:[14,36],gaaende:[22,16]};
var BLINKS={sedan:1,suv:1,stasjonsvogn:1,pickup:1,sport_rod:1,sport_gul:1,lastebil:1,buss:1};
function vname(v){return t('tl_veh_'+v.id);}
function blinkers(hw,hh){
  return [[-1,-1,'V'],[-1,1,'V'],[1,-1,'H'],[1,1,'H']].map(function(q){return '<circle class="tl-bl '+q[2]+'" cx="'+(q[0]*(hw-2))+'" cy="'+(q[1]*(hh-5))+'" r="5.5" fill="#ff9a1a" stroke="#fff3c4" stroke-width="1.5"/>';}).join('');
}
function vehShape(v){
  var sz=SIZE[v.type],sh='<ellipse cx="4" cy="5" rx="'+(sz[0]/2+4)+'" ry="'+(sz[1]/2+3)+'" fill="#000" opacity=".2"/>';
  if(IMG[v.type]){var w=sz[0],h=sz[1];var badge=v.color?'<circle cx="0" cy="'+f(h*0.08)+'" r="7" fill="'+v.color+'" stroke="#fff" stroke-width="1.6"/><text x="0" y="'+f(h*0.08+3.6)+'" text-anchor="middle" font-size="10" font-weight="700" fill="#fff">'+v.id+'</text>':'';return sh+'<image href="'+IMGDIR+IMG[v.type]+'" x="'+(-w/2)+'" y="'+(-h/2)+'" width="'+w+'" height="'+h+'" preserveAspectRatio="none"/>'+badge+blinkers(w/2,h/2);}
  if(v.type==='buss'){var rows='';for(var i=0;i<4;i++)rows+='<rect x="-9" y="'+(-40+i*26)+'" width="18" height="12" rx="2" fill="#bfb8ad"/>';
    return sh+'<rect x="-22" y="-65" width="44" height="130" rx="8" fill="#c7372f"/><rect x="-22" y="-65" width="44" height="130" rx="8" fill="url(#tl-carShade)"/><rect x="-14" y="-52" width="28" height="108" rx="4" fill="#e9e4dc" opacity=".9"/>'+rows+'<path d="M-19,-63 Q0,-67 19,-63 L18,-56 Q0,-58 -18,-56Z" fill="url(#tl-glass)"/>'+blinkers(22,65);}
  if(v.type==='sykkel')return '<ellipse cx="2" cy="3" rx="8" ry="19" fill="#000" opacity=".16"/><rect x="-1.5" y="-18" width="3" height="36" rx="1.5" fill="#222"/><rect x="-9" y="-11" width="18" height="2.6" rx="1.3" fill="#333"/><ellipse cx="0" cy="0" rx="9" ry="6.5" fill="#2b8a6e"/><circle cx="0" cy="-2" r="4.8" fill="#f1d3b3" stroke="#3a2a1d" stroke-width="1.5"/>';
  if(v.type==='gaaende')return '<ellipse cx="2" cy="3" rx="12" ry="8" fill="#000" opacity=".16"/><ellipse cx="0" cy="0" rx="11" ry="6.5" fill="#6b4fa3"/><circle cx="0" cy="0" r="5.2" fill="#3a2a1d"/>';
  return'';
}
function vehG(v){
  return '<g class="v" data-id="'+v.id+'" data-blink="'+(v.blink||'')+'" style="cursor:grab" transform="translate('+f(v.x)+' '+f(v.y)+') rotate('+v.rot+')">'+vehShape(v)+'</g>';
}

/* ---------- Board state ---------- */
var inited=false;
var st={layout:'vanlig',arms:4,lanes:1,gangfelt:true,reg:'uregulert',route:['S','E'],signal:'red',maneuver:null};
var vehicles=[],strokes=[],msigns=[],sel=null,selSign=null,mode='move',cat=null,undo=[],showGreen=false,drag=null;
function resetVehicles(){vehicles=VEH.map(function(v){return Object.assign({},v,{x:v.px,y:v.py,rot:0,blink:''});});}
function snap(){return JSON.stringify({st:st,vehicles:vehicles,strokes:strokes,msigns:msigns,showGreen:showGreen});}
function pushUndo(){undo.push(snap());if(undo.length>60)undo.shift();}
function restore(s){var o=JSON.parse(s);st=o.st;vehicles=o.vehicles;strokes=o.strokes;msigns=o.msigns;showGreen=o.showGreen;sel=null;selSign=null;renderAll();}
function clamp(v,a,b){return Math.max(a,Math.min(b,v));}

function parkLayer(){
  var lines='';for(var i=0;i<6;i++)lines+='<line x1="'+(30+i*55)+'" y1="530" x2="'+(30+i*55)+'" y2="560" stroke="#fff" stroke-width="3"/>';
  return '<g><rect x="18" y="505" width="350" height="188" rx="12" fill="#eceee8" stroke="#bfc4ba" stroke-width="2" stroke-dasharray="8 6"/>'+lines+'<text x="30" y="523" font-size="14" font-weight="700" fill="#59616a">'+t('tl_park_label')+'</text></g>';
}
function renderStatic(){
  L('Lroad').innerHTML=roadLayer(st)+marksLayer(st);
  L('Lgreen').innerHTML=showGreen?greenLayer(st):'';
  L('Lpark').innerHTML=parkLayer();
  L('Lsigns').innerHTML=signsLayer(st);
  renderMs();
}
function renderMs(){L('Lmsigns').innerHTML=msigns.map(function(s){return '<g class="tl-ms" data-id="'+s.id+'" style="cursor:grab">'+mount(signShape(s.code,{st:st,arm:'S'}),s.x,s.y,s.code)+(s.id===selSign?'<circle cx="'+f(s.x)+'" cy="'+f(s.y)+'" r="22" fill="none" stroke="#1d5fb8" stroke-width="2" stroke-dasharray="5 4"/>':'')+'</g>';}).join('');}
function renderVeh(){L('Lveh').innerHTML=vehicles.map(vehG).join('');renderSel();}
function renderSel(){
  var v=vehicles.filter(function(x){return x.id===sel;})[0];if(!v){L('Lsel').innerHTML='';return;}
  var sz=SIZE[v.type],w=sz[0],h=sz[1];
  L('Lsel').innerHTML='<g transform="translate('+f(v.x)+' '+f(v.y)+') rotate('+v.rot+')"><rect x="'+(-w/2-6)+'" y="'+(-h/2-6)+'" width="'+(w+12)+'" height="'+(h+12)+'" rx="10" fill="none" stroke="#1d5fb8" stroke-width="2" stroke-dasharray="6 5"/><line x1="0" y1="'+(-h/2-6)+'" x2="0" y2="'+(-h/2-26)+'" stroke="#1d5fb8" stroke-width="2"/><g class="tl-rot" style="cursor:grab"><circle cx="0" cy="'+(-h/2-36)+'" r="12" fill="#fff" stroke="#1d5fb8" stroke-width="2.5"/><path d="M-5,'+(-h/2-38)+' a5,5 0 1,1 2,6" fill="none" stroke="#1d5fb8" stroke-width="2"/></g></g>';
}
function strokeD(pts){return pts.map(function(p,i){return (i?'L':'M')+f(p[0])+','+f(p[1]);}).join(' ');}
function renderStrokes(){L('Ldraw').innerHTML=strokes.map(function(s){return '<path class="tl-stroke" data-id="'+s.id+'" d="'+strokeD(s.pts)+'" fill="none" stroke="#d9530f" stroke-width="6" stroke-linecap="round" stroke-linejoin="round" style="pointer-events:'+(mode==='erase'?'stroke':'none')+'"/>';}).join('');}
function renderAll(){
  L('Board').setAttribute('aria-label',t('tl_board_label'));
  renderStatic();renderVeh();renderStrokes();renderSkiltlinje();renderVRH();if(cat)openCat(cat,true);
}

/* Sign line (choose junction) */
function regIcon(r){
  if(r==='uregulert')return '<svg viewBox="-20 -20 40 40" aria-hidden="true"><path d="M-5,-18h10v13h13v10h-13v13h-10v-13h-13v-10h13z" fill="#585e64"/></svg>';
  if(r==='lys')return '<svg viewBox="-20 -22 40 44" aria-hidden="true">'+signalShape('green',.95)+'</svg>';
  if(r==='rundkjoring')return '<svg viewBox="-18 -18 36 36" aria-hidden="true">'+signShape('402')+'</svg>';
  var code={fare:'fare',vikeplikt:'202',stopp:'204',forkjorsvei:'206',forkjorskryss:'210'}[r];
  return '<svg viewBox="-19 -19 38 38" aria-hidden="true">'+signShape(code)+'</svg>';
}
function routeLabel(r){return t('tl_route_prefix')+': '+routeName(r.id);}
function renderSkiltlinje(){
  var h='<div class="tl-row">'+regsFor(st).map(function(r){return '<button data-reg="'+r+'" aria-pressed="'+(st.reg===r)+'" title="'+regName(r)+'" aria-label="'+regName(r)+'">'+regIcon(r)+'</button>';}).join('')+'</div>';
  if(st.layout==='skraa'&&st.reg==='forkjorsvei'){
    h+='<div class="tl-row">'+routesFor(st).map(function(r){return '<button data-route="'+r.id+'" aria-pressed="'+(st.route.join('')===r.arms.join(''))+'" title="'+routeLabel(r)+'" aria-label="'+routeLabel(r)+'"><svg viewBox="-17 -13 34 26" aria-hidden="true">'+signShape('822',{st:Object.assign({},st,{route:r.arms}),arm:'S'})+'</svg></button>';}).join('')+'</div>';
  }
  h+='<small>'+t('tl_choose')+'</small>';
  L('Skiltlinje').innerHTML=h;
}
function chooseRoute(id){var r=ROUTES.filter(function(x){return x.id===id;})[0];if(!r)return;pushUndo();st.route=r.arms.slice();showGreen=true;renderAll();}
function renderVRH(){
  var names={V:t('tl_dir_V'),R:t('tl_dir_R'),H:t('tl_dir_H')};
  document.querySelectorAll('#tlVrh button').forEach(function(b){b.setAttribute('aria-pressed',String(st.maneuver===b.dataset.m));b.title=names[b.dataset.m];b.setAttribute('aria-label',names[b.dataset.m]);});
  L('Vrh').setAttribute('aria-label',t('tl_dir'));
}
function setReg(r){
  pushUndo();st.reg=r;if(r==='lys'&&!st.signal)st.signal='red';
  showGreen=!!greenOf(st)&&(r==='forkjorsvei'||st.layout!=='vanlig')?showGreen:false;
  renderAll();
}
function setLayout(k,v){
  pushUndo();st[k]=v;
  if(regsFor(st).indexOf(st.reg)<0)st.reg=regsFor(st)[0];
  if(st.layout==='rund')st.reg='rundkjoring';
  if(st.layout==='skraa'&&!routesFor(st).some(function(r){return r.arms.join('')===st.route.join('');}))st.route=['S','E'];
  renderAll();
}
function setSignal(s){pushUndo();st.signal=s;renderStatic();if(cat==='lys')openCat('lys',true);}

/* Panels */
function segBtns(items,cur,attr){return '<div class="tl-seg">'+items.map(function(i){return '<button data-'+attr+'="'+i[0]+'" aria-pressed="'+(String(cur)===String(i[0]))+'">'+i[1]+'</button>';}).join('')+'</div>';}
function hint(k){return '<p class="tl-hint">'+t(k)+'</p>';}
function openCat(c,refresh){
  var pop=L('Pop');
  if(!refresh&&cat===c){cat=null;pop.hidden=true;mode='move';updateRail();renderStrokes();return;}
  cat=c;mode=c==='tegn'?'draw':c==='visk'?'erase':'move';updateRail();renderStrokes();
  var h='';
  if(c==='kryss'){
    h='<h3>'+t('tl_cat_kryss')+'</h3>'+segBtns([['vanlig',t('tl_lay_vanlig')],['skraa',t('tl_lay_skraa')],['rund',t('tl_lay_rund')]],st.layout,'layout')
     +hint('tl_arms')+segBtns([[4,t('tl_arms4')],[3,t('tl_arms3')]],st.arms,'arms')
     +hint('tl_lanes')+segBtns([[1,t('tl_lane1')],[2,t('tl_lane2')]],st.lanes,'lanes')
     +hint('tl_xwalk')+segBtns([[1,t('tl_on')],[0,t('tl_off')]],st.gangfelt?1:0,'gang');
  }
  if(c==='skilt'){
    h='<h3>'+t('tl_cat_skilt')+'</h3>'+hint('tl_skilt_hint')+'<div class="tl-seg">'+regsFor(st).map(function(r){return '<button data-reg="'+r+'" aria-pressed="'+(st.reg===r)+'">'+regIcon(r)+regName(r)+'</button>';}).join('')+'</div>';
    if(st.layout==='skraa'&&st.reg==='forkjorsvei'){var cur=ROUTES.filter(function(r){return r.arms.join('')===st.route.join('');})[0];h+=hint('tl_route_q')+segBtns(routesFor(st).map(function(r){return [r.id,routeName(r.id)];}),cur?cur.id:'','route');}
    h+='<label class="tl-check"><input type="checkbox" id="tlGreenChk" '+(showGreen?'checked':'')+' '+(greenOf(st)?'':'disabled')+'> '+t('tl_show_green')+'</label>';
    h+=hint('tl_place_own')+'<div class="tl-seg">'+['202','204','206','210','402','fare'].map(function(s){return '<button data-place="'+s+'" title="'+signName(s)+'" aria-label="'+t('tl_place')+' '+signName(s)+'"><svg viewBox="-19 -19 38 38" aria-hidden="true">'+signShape(s)+'</svg></button>';}).join('')+'</div><button class="tl-btn" id="tlDelSign" '+(selSign?'':'disabled')+'>'+t('tl_del_sign')+'</button>';
  }
  if(c==='lys'){
    h='<h3>'+t('tl_light_title')+'</h3>';
    if(st.reg!=='lys'||st.layout!=='vanlig')h+=hint('tl_light_only')+'<button class="tl-btn" id="tlMkLys">'+t('tl_make_light')+'</button>';
    else h+=hint('tl_light_hint')+'<div class="tl-lights">'+['red','redyellow','green','yellow'].map(function(s){return '<button data-sig="'+s+'" aria-pressed="'+(st.signal===s)+'"><svg viewBox="-12 -24 24 48" aria-hidden="true">'+signalShape(s,1)+'</svg>'+cap(sigName(s))+'</button>';}).join('')+'</div>';
  }
  if(c==='biler'){
    h='<h3>'+t('tl_cars_title')+'</h3>'+hint('tl_cars_hint')+'<div class="tl-seg">'+vehicles.map(function(v){return '<button data-park="'+v.id+'">'+vname(v)+' '+t('tl_to_park')+'</button>';}).join('')+'</div><button class="tl-btn" id="tlParkAll">'+t('tl_all_park')+'</button>';
  }
  if(c==='tegn')h='<h3>'+t('tl_cat_tegn')+'</h3>'+hint('tl_draw_hint')+'<button class="tl-btn" id="tlClearDraw">'+t('tl_clear_draw')+'</button>';
  if(c==='visk')h='<h3>'+t('tl_cat_visk')+'</h3>'+hint('tl_erase_hint')+'<button class="tl-btn" id="tlClearDraw">'+t('tl_clear_draw')+'</button>';
  pop.innerHTML=h;pop.hidden=false;
}
function updateRail(){document.querySelectorAll('#tlRail [data-cat]').forEach(function(b){b.setAttribute('aria-pressed',String(b.dataset.cat===cat));});}

/* Pointer: move, indicators, rotate, draw, erase */
function svgPt(e){var b=L('Board'),p=b.createSVGPoint();p.x=e.clientX;p.y=e.clientY;var q=p.matrixTransform(b.getScreenCTM().inverse());return[q.x,q.y];}
function eraseAt(e){var el=document.elementFromPoint(e.clientX,e.clientY);if(el&&el.classList&&el.classList.contains('tl-stroke')){strokes=strokes.filter(function(s){return s.id!==el.dataset.id;});el.remove();drag.n++;}}
function placeVeh(v){var el=L('Board').querySelector('.v[data-id="'+v.id+'"]');if(el){el.setAttribute('transform','translate('+f(v.x)+' '+f(v.y)+') rotate('+v.rot+')');el.dataset.blink=v.blink||'';}renderSel();}
function findVeh(id){return vehicles.filter(function(x){return x.id===id;})[0];}
function onDown(e){
  var p=svgPt(e);hideHelp();var board=L('Board');
  if(mode==='draw'){pushUndo();var s={id:'k'+Date.now(),pts:[p]};strokes.push(s);drag={kind:'draw',s:s};renderStrokes();board.setPointerCapture(e.pointerId);return;}
  if(mode==='erase'){pushUndo();drag={kind:'erase',n:0};eraseAt(e);board.setPointerCapture(e.pointerId);return;}
  var rot=e.target.closest('.tl-rot'),v=e.target.closest('.v'),ms=e.target.closest('.tl-ms'),sg=e.target.closest('.tl-sg');
  if(rot){pushUndo();drag={kind:'rot',v:findVeh(sel)};}
  else if(v){var veh=findVeh(v.dataset.id);drag={kind:'veh',v:veh,start:p,ox:veh.x,oy:veh.y,moved:false};}
  else if(ms){var s2=msigns.filter(function(x){return x.id===ms.dataset.id;})[0];selSign=s2.id;renderMs();if(cat==='skilt')openCat('skilt',true);drag={kind:'ms',s:s2,start:p,ox:s2.x,oy:s2.y,moved:false};}
  else if(sg){showHelp(sg.dataset.help,sg);return;}
  else{sel=null;selSign=null;renderSel();renderMs();return;}
  board.setPointerCapture(e.pointerId);
}
function onMove(e){
  if(!drag)return;var p=svgPt(e);
  if(drag.kind==='draw'){var l=drag.s.pts[drag.s.pts.length-1];if(Math.hypot(p[0]-l[0],p[1]-l[1])>3){drag.s.pts.push(p);var el=L('Board').querySelector('[data-id="'+drag.s.id+'"]');if(el)el.setAttribute('d',strokeD(drag.s.pts));}return;}
  if(drag.kind==='erase'){eraseAt(e);return;}
  if(drag.kind==='rot'){var v=drag.v;var a=Math.atan2(p[1]-v.y,p[0]-v.x)/RAD+90;a=Math.round(a/15)*15;v.rot=((a%360)+360)%360;placeVeh(v);return;}
  var dx=p[0]-drag.start[0],dy=p[1]-drag.start[1];
  if(!drag.moved&&Math.hypot(dx,dy)>6){drag.moved=true;pushUndo();}
  if(!drag.moved)return;
  if(drag.kind==='veh'){drag.v.x=clamp(drag.ox+dx,10,990);drag.v.y=clamp(drag.oy+dy,10,690);placeVeh(drag.v);}
  if(drag.kind==='ms'){drag.s.x=clamp(drag.ox+dx,20,980);drag.s.y=clamp(drag.oy+dy,20,670);renderMs();}
}
function endDrag(){
  if(!drag)return;var d=drag;drag=null;
  if(d.kind==='draw'){if(d.s.pts.length<2){strokes=strokes.filter(function(s){return s!==d.s;});undo.pop();renderStrokes();}}
  if(d.kind==='erase'){if(!d.n)undo.pop();}
  if(d.kind==='rot'){renderVeh();}
  if(d.kind==='veh'){
    var v=d.v;
    if(!d.moved){sel=v.id;if(BLINKS[v.type]){pushUndo();v.blink=v.blink===''?'H':v.blink==='H'?'V':'';renderVeh();}else renderSel();}
    else renderVeh();
  }
}
function showHelp(code,el){
  if(HELPCODES.indexOf(code)<0)return;var h=L('Help');
  if(greenOf(st)&&code!=='signal'&&code!=='fare'){showGreen=true;renderStatic();}
  h.innerHTML='<b>'+t('tl_help_'+code+'_t')+'</b>'+t('tl_help_'+code);h.hidden=false;
  var wr=L('BoardWrap').getBoundingClientRect(),r=el.getBoundingClientRect();
  var x=r.right-wr.left+8,y=r.top-wr.top-10;if(x+280>wr.width)x=Math.max(8,r.left-wr.left-280);h.style.left=x+'px';h.style.top=Math.max(8,Math.min(y,wr.height-130))+'px';
}
function hideHelp(){var h=L('Help');if(h)h.hidden=true;}

function init(){
  if(inited)return;inited=true;resetVehicles();
  var board=L('Board');
  L('Skiltlinje').addEventListener('click',function(e){
    var b=e.target.closest('button');if(!b)return;
    if(b.dataset.reg)setReg(b.dataset.reg);
    if(b.dataset.route)chooseRoute(b.dataset.route);
  });
  L('Vrh').addEventListener('click',function(e){var b=e.target.closest('button');if(!b)return;pushUndo();st.maneuver=st.maneuver===b.dataset.m?null:b.dataset.m;renderVRH();});
  L('Rail').addEventListener('click',function(e){
    var b=e.target.closest('button');if(!b)return;
    if(b.id==='tlUndoBtn'){if(undo.length)restore(undo.pop());return;}
    if(b.dataset.cat)openCat(b.dataset.cat);
  });
  L('Pop').addEventListener('click',function(e){
    var b=e.target.closest('button');if(!b)return;var d=b.dataset;
    if(d.layout)setLayout('layout',d.layout);
    if(d.arms)setLayout('arms',+d.arms);
    if(d.lanes)setLayout('lanes',+d.lanes);
    if(d.gang!==undefined)setLayout('gangfelt',d.gang==='1');
    if(d.reg)setReg(d.reg);
    if(d.route)chooseRoute(d.route);
    if(d.sig)setSignal(d.sig);
    if(d.place){pushUndo();var s={id:'s'+Date.now(),code:d.place,x:860,y:470};msigns.push(s);selSign=s.id;renderMs();openCat('skilt',true);}
    if(d.park){pushUndo();var v=findVeh(d.park);Object.assign(v,{x:v.px,y:v.py,rot:0,blink:''});renderVeh();}
    if(b.id==='tlParkAll'){pushUndo();resetVehicles();renderVeh();}
    if(b.id==='tlMkLys'){if(st.layout!=='vanlig')setLayout('layout','vanlig');setReg('lys');openCat('lys',true);}
    if(b.id==='tlDelSign'&&selSign){pushUndo();msigns=msigns.filter(function(s){return s.id!==selSign;});selSign=null;renderMs();openCat('skilt',true);}
    if(b.id==='tlClearDraw'){pushUndo();strokes=[];renderStrokes();}
  });
  L('Pop').addEventListener('change',function(e){if(e.target.id==='tlGreenChk'){showGreen=e.target.checked;renderStatic();}});
  board.addEventListener('pointerdown',onDown);board.addEventListener('pointermove',onMove);
  board.addEventListener('pointerup',endDrag);board.addEventListener('pointercancel',endDrag);
}
window.tlOnShow=function(){init();renderAll();};
window.tlRerender=function(){if(!inited)return;hideHelp();renderAll();};
window.openTrafikklab=function(){showTab('trafikklab');};
window.closeTrafikklab=function(){hideHelp();showTab('home');};
})();
"""


def _swap(html: str, old: str, new: str) -> str:
    """Replace the first occurrence; fail loudly if the shell changed so a hook is never skipped silently."""
    if old not in html:
        raise ValueError('trafikklab_web: anchor not found in web shell: ' + old[:70])
    return html.replace(old, new, 1)


def install(html: str) -> str:
    """Install the isolated screen into the existing web shell; no mobile/payment changes."""
    html = _swap(html, '</style>', CSS + '\n</style>')
    html = _swap(html, '<div class="home-main-actions">', HOME + '\n<div class="home-main-actions">')
    html = _swap(html, '<div class="screen" id="screenCats">', SCREEN + '\n<div class="screen" id="screenCats">')
    html = _swap(html, 'function t(key) {', SCRIPT + '\nfunction t(key) {')
    html = _swap(html, "library:'screenLibrary', stopping:'screenStopping'",
                 "library:'screenLibrary', stopping:'screenStopping', trafikklab:'screenTrafikklab'")
    html = _swap(html, "app.classList.toggle('stopping-mode', id === 'screenStopping');",
                 "app.classList.toggle('stopping-mode', id === 'screenStopping');\n"
                 "  app.classList.toggle('trafikklab-mode', id === 'screenTrafikklab');")
    html = _swap(html, "if (tab === 'stopping')  loadStopping(false);",
                 "if (tab === 'stopping')  loadStopping(false);\n"
                 "    if (tab === 'trafikklab') tlOnShow();")
    html = _swap(html, "if (typeof renderStopping === 'function' && document.getElementById('stopSpeed')) renderStopping();",
                 "if (typeof renderStopping === 'function' && document.getElementById('stopSpeed')) renderStopping();\n"
                 "  if (typeof tlRerender === 'function') tlRerender();")
    return html
