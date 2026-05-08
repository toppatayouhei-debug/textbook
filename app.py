import streamlit as st
import pandas as pd
from gtts import gTTS
import io
import base64
import json

# ページタイトルの変更
st.set_page_config(page_title="WordBox - Large", layout="centered")

# --- 1. データの読み込み ---
@st.cache_data
def load_all_data():
    file_path = "wordlists.csv"
    try:
        df = pd.read_csv(file_path, sep=None, engine='python', skiprows=1, header=None).fillna("")
        text_list = df.values.tolist()
        tango_df = df.copy()
        while len(tango_df.columns) < 4:
            tango_df[f'col_{len(tango_df.columns)}'] = ""
        tango_list = tango_df.values.tolist()
    except Exception as e:
        error_msg = [["Error", f"読み込み失敗: {e}", "", ""]]
        return error_msg, error_msg
    return text_list, tango_list

text_raw, tango_raw = load_all_data()

# --- 2. 音声パック作成 ---
@st.cache_data
def prepare_assets(raw_data, is_tango=False):
    prepared = []
    for item in raw_data:
        eng_text = str(item[0]) if item[0] else "Empty"
        tts = gTTS(text=eng_text, lang='en')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64 = base64.b64encode(fp.read()).decode()
        entry = {
            "eng": eng_text,
            "jp": str(item[1]) if len(item) > 1 else "",
            "audio": f"data:audio/mp3;base64,{b64}",
            "ex": str(item[2]) if len(item) > 2 else "",
            "ext": str(item[3]) if len(item) > 3 else ""
        }
        prepared.append(entry)
    return prepared

with st.spinner("🚀 WordBox 準備中..."):
    text_json = json.dumps(prepare_assets(text_raw, False))
    tango_json = json.dumps(prepare_assets(tango_raw, True))

# メインタイトルの変更
st.markdown("<h1 style='text-align: center; color: #4a90e2;'>🤖 WordBox (Large)</h1>", unsafe_allow_html=True)

# --- 3. メインUI (HTML/JS) ---
st.components.v1.html(f"""
    <style>
        @keyframes glow {{
            0% {{ box-shadow: 0 10px 40px rgba(74,144,226,0.2); border-color: #f0f4f8; }}
            50% {{ box-shadow: 0 0 60px rgba(74,144,226,0.8); border-color: #4a90e2; }}
            100% {{ box-shadow: 0 10px 40px rgba(74,144,226,0.2); border-color: #f0f4f8; }}
        }}
        .playing {{ animation: glow 1.2s infinite ease-in-out; border-width: 4px !important; }}
        
        button {{ font-family: sans-serif; transition: 0.2s; }}
        button:active {{ transform: scale(0.95); }}
    </style>

    <div id="study-app" style="font-family: 'Helvetica Neue', Arial, sans-serif; color: #000; max-width: 800px; margin: auto;">
        
        <div style="display: flex; background: #e0e6ed; padding: 8px; border-radius: 25px; margin-bottom: 30px;">
            <button id="mode-text" style="flex: 1; padding: 15px; border-radius: 20px; border: none; background: #4a90e2; color: white; font-weight: bold; cursor: pointer; font-size: 18px;">📖 一覧音読</button>
            <button id="mode-tango" style="flex: 1; padding: 15px; border-radius: 20px; border: none; background: transparent; color: #555; font-weight: bold; cursor: pointer; font-size: 18px;">🗂️ 単語カード</button>
        </div>

        <div style="display: flex; gap: 12px; margin-bottom: 30px; justify-content: center;">
            <button id="btn-manual" style="padding: 12px 25px; border-radius: 25px; border: 1px solid #ccc; background: #fff; font-size: 16px; font-weight: bold;">👆手動</button>
            <button id="btn-auto" style="padding: 12px 25px; border-radius: 25px; border: 1px solid #ccc; background: #fff; font-size: 16px; font-weight: bold;">🤖オート</button>
            <button id="btn-random" style="padding: 12px 25px; border-radius: 25px; border: 1px solid #ccc; background: #fff; font-size: 16px; font-weight: bold;">🔀ランダム</button>
        </div>

        <div id="card" style="background: #ffffff; padding: 60px 40px; border-radius: 40px; text-align: center; min-height: 450px; display: flex; flex-direction: column; justify-content: center; box-shadow: 0 15px 35px rgba(0,0,0,0.1); border: 3px solid #f0f4f8; position: relative; transition: 0.3s;">
            
            <div id="eng" style="font-size: 56px; font-weight: 900; margin-bottom: 30px; color: #000; line-height: 1.1; letter-spacing: -1px;"></div>
            
            <div id="jp-container">
                <div id="jp" style="font-size: 38px; color: #444; font-weight: 700; line-height: 1.3; background: #f8f9fa; padding: 15px; border-radius: 15px; display: inline-block;"></div>
                <div id="tango-extra" style="display: none; border-top: 2px solid #eee; margin-top: 40px; padding-top: 30px; text-align: left;">
                    <div id="ex" style="font-size: 24px; color: #4a90e2; font-weight: 600; font-style: italic; margin-bottom: 15px; line-height: 1.2;"></div>
                    <div id="ext" style="font-size: 20px; color: #666; font-weight: 500;"></div>
                </div>
            </div>

            <button id="btn-show" style="display: none; margin: 40px auto 0; padding: 20px 50px; border-radius: 40px; border: none; background: #4a90e2; color: white; font-weight: bold; cursor: pointer; font-size: 22px; box-shadow: 0 4px 15px rgba(74,144,226,0.3);">🔍 意味を表示</button>
        </div>

        <div id="nav-controls" style="margin-top: 40px; display: flex; gap: 30px; justify-content: center;">
            <button id="btn-prev" style="width: 90px; height: 90px; border-radius: 50%; background: #fff; border: 2px solid #eee; font-size: 40px; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">⬅️</button>
            <button id="btn-next" style="width: 90px; height: 90px; border-radius: 50%; background: #fff; border: 2px solid #eee; font-size: 40px; cursor: pointer; box-shadow: 0 4px 10px rgba(0,0,0,0.05);">➡️</button>
        </div>

        <div id="auto-extra" style="display: none; margin-top: 30px;">
            <button id="btn-stop" style="width: 100%; padding: 20px; border-radius: 25px; background: #ff4757; color: white; border: none; font-weight: bold; font-size: 20px; cursor: pointer;">⏹️ オート演奏を停止</button>
        </div>

        <div style="margin-top: 40px; text-align: center;">
            <div id="status" style="font-size: 20px; color: #999; font-weight: bold;"></div>
        </div>
    </div>

    <script>
        const textData = {text_json};
        const tangoData = {tango_json};
        let currentDataSet = textData;
        let index = 0;
        let isAuto = false;
        let isRandom = false;
        let currentAudio = new Audio();
        let timer = null;
        let currentMode = 'text';

        function updateCard(shouldPlay = true) {{
            const item = currentDataSet[index];
            if (!item) return;
            
            document.getElementById('eng').innerText = item.eng;
            document.getElementById('jp').innerText = item.jp;
            
            const extra = document.getElementById('tango-extra');
            const showBtn = document.getElementById('btn-show');
            const jpContainer = document.getElementById('jp-container');

            if (currentMode === 'tango') {{
                document.getElementById('jp').style.color = "#d63031"; 
                document.getElementById('ex').innerText = item.ex || "";
                document.getElementById('ext').innerText = item.ext || "";
                
                if (isAuto) {{
                    jpContainer.style.display = "block";
                    extra.style.display = "block";
                    showBtn.style.display = "none";
                }} else {{
                    jpContainer.style.display = "none";
                    extra.style.display = "none";
                    showBtn.style.display = "block";
                }}
            }} else {{
                document.getElementById('jp').style.color = "#444";
                jpContainer.style.display = "block";
                extra.style.display = "none";
                showBtn.style.display = "none";
            }}

            document.getElementById('status').innerText = (index + 1) + " / " + currentDataSet.length;
            if (shouldPlay) playAudio(item.audio);
        }}

        function playAudio(src) {{
            if (timer) clearTimeout(timer);
            currentAudio.pause();
            currentAudio.src = src;
            
            const card = document.getElementById('card');
            card.classList.add('playing');

            currentAudio.play().then(() => {{
                currentAudio.onended = () => {{
                    card.classList.remove('playing');
                    if (isAuto) {{
                        const delay = currentMode === 'text' ? 2500 : 3500;
                        timer = setTimeout(() => {{
                            if (!isAuto) return;
                            nextCard();
                        }}, delay);
                    }}
                }};
            }}).catch(e => {{
                card.classList.remove('playing');
            }});
        }}

        function nextCard() {{
            if (isRandom) {{
                index = Math.floor(Math.random() * currentDataSet.length);
            }} else {{
                index = (index + 1) % currentDataSet.length;
            }}
            updateCard();
        }}

        document.getElementById('btn-show').onclick = () => {{
            document.getElementById('jp-container').style.display = "block";
            document.getElementById('tango-extra').style.display = "block";
            document.getElementById('btn-show').style.display = "none";
        }};

        document.getElementById('btn-random').onclick = () => {{
            isRandom = !isRandom;
            updateUI();
        }};

        document.getElementById('mode-text').onclick = () => {{
            currentMode = 'text'; currentDataSet = textData; index = 0; isAuto = false;
            updateUI(); updateCard(false);
        }};
        document.getElementById('mode-tango').onclick = () => {{
            currentMode = 'tango'; currentDataSet = tangoData; index = 0; isAuto = false;
            updateUI(); updateCard(false);
        }};

        document.getElementById('btn-next').onclick = () => {{ isAuto = false; nextCard(); updateUI(); }};
        document.getElementById('btn-prev').onclick = () => {{ isAuto = false; index = (index - 1 + currentDataSet.length) % currentDataSet.length; updateCard(); updateUI(); }};
        document.getElementById('btn-auto').onclick = () => {{ isAuto = true; updateUI(); updateCard(); }};
        document.getElementById('btn-manual').onclick = () => {{ isAuto = false; updateUI(); updateCard(false); }};
        document.getElementById('btn-stop').onclick = () => {{ 
            isAuto = false; 
            currentAudio.pause(); 
            document.getElementById('card').classList.remove('playing');
            updateUI(); 
        }};

        function updateUI() {{
            const isText = (currentMode === 'text');
            const modeText = document.getElementById('mode-text');
            const modeTango = document.getElementById('mode-tango');

            modeText.style.background = isText ? '#4a90e2' : 'transparent';
            modeText.style.color = isText ? 'white' : '#555';
            modeTango.style.background = isText ? 'transparent' : '#4a90e2';
            modeTango.style.color = isText ? '#555' : 'white';
            
            const btnManual = document.getElementById('btn-manual');
            const btnAuto = document.getElementById('btn-auto');
            const btnRandom = document.getElementById('btn-random');

            btnManual.style.background = isAuto ? '#fff' : '#333';
            btnManual.style.color = isAuto ? '#555' : '#fff';
            btnAuto.style.background = isAuto ? '#4a90e2' : '#fff';
            btnAuto.style.color = isAuto ? '#fff' : '#555';
            btnRandom.style.background = isRandom ? '#f39c12' : '#fff';
            btnRandom.style.color = isRandom ? '#fff' : '#555';
            
            document.getElementById('auto-extra').style.display = isAuto ? 'block' : 'none';
        }}

        updateCard(false);
    </script>
""", height=900)
