"""
web_chat.py — Browser-based text chat for Tavi.

Serves a mobile-friendly chat UI on the local network so an iPhone
(or any device on the same network) can query the LLM via Safari.

Usage:
    python web_chat.py

Then open http://<pi-ip>:5000 in Safari.
On Bluetooth PAN, the Pi is typically at http://10.0.0.1:5000
"""

from flask import Flask, request, jsonify, render_template_string
from llm_interface import build_qwen_prompt, query_llm
from local_knowledge import load_knowledge_base

app = Flask(__name__)

PAGE = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1">
  <title>Tavi</title>
  <style>
    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, sans-serif;
      background: #1c1c1e;
      color: #f2f2f7;
      display: flex;
      flex-direction: column;
      height: 100dvh;
    }

    header {
      padding: 16px 20px 12px;
      font-size: 17px;
      font-weight: 600;
      border-bottom: 1px solid #2c2c2e;
      text-align: center;
      letter-spacing: 0.3px;
    }

    #log {
      flex: 1;
      overflow-y: auto;
      padding: 16px 16px 8px;
      display: flex;
      flex-direction: column;
      gap: 10px;
    }

    .bubble {
      max-width: 80%;
      padding: 10px 14px;
      border-radius: 18px;
      font-size: 16px;
      line-height: 1.4;
      word-wrap: break-word;
    }

    .user {
      align-self: flex-end;
      background: #0a84ff;
      color: #fff;
      border-bottom-right-radius: 4px;
    }

    .tavi {
      align-self: flex-start;
      background: #2c2c2e;
      color: #f2f2f7;
      border-bottom-left-radius: 4px;
    }

    .thinking {
      align-self: flex-start;
      color: #8e8e93;
      font-size: 14px;
      padding: 4px 8px;
    }

    #form {
      display: flex;
      gap: 8px;
      padding: 10px 12px 24px;
      border-top: 1px solid #2c2c2e;
      background: #1c1c1e;
    }

    #input {
      flex: 1;
      background: #2c2c2e;
      color: #f2f2f7;
      border: none;
      border-radius: 20px;
      padding: 10px 16px;
      font-size: 16px;
      outline: none;
    }

    #input::placeholder { color: #636366; }

    button {
      background: #0a84ff;
      color: #fff;
      border: none;
      border-radius: 50%;
      width: 40px;
      height: 40px;
      font-size: 18px;
      cursor: pointer;
      flex-shrink: 0;
      display: flex;
      align-items: center;
      justify-content: center;
    }

    button:disabled { background: #3a3a3c; }
  </style>
</head>
<body>
  <header>Tavi</header>
  <div id="log"></div>
  <form id="form">
    <input id="input" type="text" placeholder="Ask anything…" autocomplete="off" autofocus>
    <button id="send" type="submit">&#x2191;</button>
  </form>

  <script>
    const log = document.getElementById('log');
    const input = document.getElementById('input');
    const btn = document.getElementById('send');

    function addBubble(text, cls) {
      const el = document.createElement('div');
      el.className = 'bubble ' + cls;
      el.textContent = text;
      log.appendChild(el);
      log.scrollTop = log.scrollHeight;
      return el;
    }

    document.getElementById('form').addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) return;

      input.value = '';
      btn.disabled = true;
      addBubble(text, 'user');

      const thinking = document.createElement('div');
      thinking.className = 'thinking';
      thinking.textContent = 'Thinking…';
      log.appendChild(thinking);
      log.scrollTop = log.scrollHeight;

      try {
        const res = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: text })
        });
        const data = await res.json();
        thinking.remove();
        addBubble(data.reply, 'tavi');
      } catch {
        thinking.remove();
        addBubble('Something went wrong.', 'tavi');
      }

      btn.disabled = false;
      input.focus();
    });
  </script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(PAGE)


@app.route("/chat", methods=["POST"])
def chat():
    message = request.json.get("message", "").strip()
    if not message:
        return jsonify({"reply": "I didn't get that."})
    prompt = build_qwen_prompt(message)
    reply = query_llm(prompt)
    return jsonify({"reply": reply})


if __name__ == "__main__":
    load_knowledge_base()
    print("🌐 Tavi web chat running.")
    print("   Open http://10.0.0.1:5000 in Safari (Bluetooth PAN)")
    print("   or http://<your-mac-ip>:5000 on local WiFi")
    print("   Ctrl+C to quit.")
    app.run(host="0.0.0.0", port=5000, debug=False)
