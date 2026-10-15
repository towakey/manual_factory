// 画像に図形（〇 / □）を描き込む簡易エディタ
// openImageAnnotator(source, onSave)
//   source: File / Blob、または画像URL文字列（同一オリジン）
//   onSave: 描き込み済みの PNG File を受け取るコールバック
function openImageAnnotator(source, onSave) {
    const isObjectUrl = typeof source !== 'string';
    const url = isObjectUrl ? URL.createObjectURL(source) : source;
    const img = new Image();
    img.onload = function () {
        createAnnotatorEditor(img, url, isObjectUrl, onSave);
    };
    img.onerror = function () {
        if (isObjectUrl) URL.revokeObjectURL(url);
        if (typeof showAlert === 'function') {
            showAlert('画像を読み込めませんでした', 'error');
        }
    };
    img.src = url;
}

function createAnnotatorEditor(img, url, revokeUrl, onSave) {
    const scale = Math.min(
        (window.innerWidth * 0.85) / img.naturalWidth,
        (window.innerHeight * 0.6) / img.naturalHeight,
        1
    );
    const cw = Math.max(1, Math.round(img.naturalWidth * scale));
    const ch = Math.max(1, Math.round(img.naturalHeight * scale));

    const modal = document.createElement('div');
    modal.className = 'modal active';
    modal.innerHTML = `
        <div class="modal-content" style="width: auto; max-width: 92vw;">
            <div class="modal-header">
                <strong>画像を編集（図形で囲む）</strong>
                <button type="button" class="modal-close">×</button>
            </div>
            <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; align-items: center; margin-bottom: 0.5rem;">
                <button type="button" class="btn btn-secondary ia-tool" data-tool="ellipse" style="padding: 0.25rem 0.75rem;">〇</button>
                <button type="button" class="btn btn-secondary ia-tool" data-tool="rect" style="padding: 0.25rem 0.75rem;">□</button>
                <input type="color" class="ia-color" value="#e74c3c" title="図形の色" style="width: 2.5rem; height: 2rem; padding: 0; border: none; background: none; cursor: pointer;">
                <select class="ia-width" title="線の太さ" style="padding: 0.25rem;">
                    <option value="3">細</option>
                    <option value="6" selected>中</option>
                    <option value="10">太</option>
                </select>
                <button type="button" class="btn ia-undo" style="padding: 0.25rem 0.75rem;">1つ戻す</button>
                <button type="button" class="btn ia-clear" style="padding: 0.25rem 0.75rem;">全消し</button>
            </div>
            <canvas class="ia-canvas" width="${cw}" height="${ch}" style="display: block; max-width: 100%; border: 1px solid #ddd; cursor: crosshair; touch-action: none;"></canvas>
            <div style="display: flex; justify-content: flex-end; gap: 0.5rem; margin-top: 0.75rem;">
                <button type="button" class="btn ia-cancel" style="padding: 0.5rem 1rem;">キャンセル</button>
                <button type="button" class="btn btn-primary ia-save" style="padding: 0.5rem 1rem;">保存</button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);

    const canvas = modal.querySelector('.ia-canvas');
    const ctx = canvas.getContext('2d');
    const colorInput = modal.querySelector('.ia-color');
    const widthInput = modal.querySelector('.ia-width');

    let tool = 'ellipse';
    const shapes = [];
    let current = null;
    let dragStart = null;

    function drawShape(context, shape, ratio) {
        context.strokeStyle = shape.color;
        context.lineWidth = shape.width * ratio;
        const x = Math.min(shape.x0, shape.x1) * ratio;
        const y = Math.min(shape.y0, shape.y1) * ratio;
        const w = Math.abs(shape.x1 - shape.x0) * ratio;
        const h = Math.abs(shape.y1 - shape.y0) * ratio;
        context.beginPath();
        if (shape.type === 'rect') {
            context.strokeRect(x, y, w, h);
        } else {
            context.ellipse(x + w / 2, y + h / 2, w / 2, h / 2, 0, 0, Math.PI * 2);
            context.stroke();
        }
    }

    function redraw() {
        ctx.clearRect(0, 0, cw, ch);
        ctx.drawImage(img, 0, 0, cw, ch);
        shapes.forEach(s => drawShape(ctx, s, 1));
        if (current) drawShape(ctx, current, 1);
    }

    function canvasPos(e) {
        const rect = canvas.getBoundingClientRect();
        return {
            x: (e.clientX - rect.left) * (cw / rect.width),
            y: (e.clientY - rect.top) * (ch / rect.height)
        };
    }

    modal.querySelectorAll('.ia-tool').forEach(btn => {
        btn.addEventListener('click', function () {
            tool = btn.dataset.tool;
            modal.querySelectorAll('.ia-tool').forEach(b => {
                b.className = 'btn btn-secondary ia-tool';
            });
            btn.className = 'btn btn-primary ia-tool';
        });
    });
    modal.querySelector('.ia-tool[data-tool="ellipse"]').className = 'btn btn-primary ia-tool';

    canvas.addEventListener('pointerdown', function (e) {
        try { canvas.setPointerCapture(e.pointerId); } catch (err) { /* 一部環境で未対応 */ }
        dragStart = canvasPos(e);
        e.preventDefault();
    });

    canvas.addEventListener('pointermove', function (e) {
        if (!dragStart) return;
        const pos = canvasPos(e);
        current = {
            type: tool,
            x0: dragStart.x,
            y0: dragStart.y,
            x1: pos.x,
            y1: pos.y,
            color: colorInput.value,
            width: parseInt(widthInput.value, 10)
        };
        redraw();
    });

    canvas.addEventListener('pointerup', function (e) {
        if (!dragStart) return;
        const pos = canvasPos(e);
        dragStart = null;
        if (current && (Math.abs(current.x1 - current.x0) > 3 || Math.abs(current.y1 - current.y0) > 3)) {
            shapes.push(current);
        }
        current = null;
        redraw();
    });

    modal.querySelector('.ia-undo').addEventListener('click', function () {
        shapes.pop();
        redraw();
    });
    modal.querySelector('.ia-clear').addEventListener('click', function () {
        shapes.length = 0;
        redraw();
    });

    function close() {
        document.removeEventListener('keydown', onKeydown);
        modal.remove();
        if (revokeUrl) URL.revokeObjectURL(url);
    }

    function onKeydown(e) {
        if (e.key === 'Escape') close();
    }
    document.addEventListener('keydown', onKeydown);

    modal.querySelector('.modal-close').addEventListener('click', close);
    modal.querySelector('.ia-cancel').addEventListener('click', close);

    modal.querySelector('.ia-save').addEventListener('click', function () {
        const off = document.createElement('canvas');
        off.width = img.naturalWidth;
        off.height = img.naturalHeight;
        const octx = off.getContext('2d');
        octx.drawImage(img, 0, 0, off.width, off.height);
        const ratio = off.width / cw;
        shapes.forEach(s => drawShape(octx, s, ratio));
        off.toBlob(function (blob) {
            if (!blob) return;
            const file = new File([blob], `annotated_${Date.now()}.png`, { type: 'image/png' });
            close();
            onSave(file);
        }, 'image/png');
    });

    redraw();
}
