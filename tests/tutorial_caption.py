"""Cartel y marca de corte de las grabaciones; nunca se cargan fuera del modo demo."""

SHOW_CAPTION = """text => {
    let caption = document.getElementById('tutorial-caption');
    if (!caption) {
        caption = document.createElement('aside');
        caption.id = 'tutorial-caption';
        caption.setAttribute('role', 'status');
        caption.style.cssText = 'position:fixed;right:24px;top:16px;'
            + 'max-width:min(640px,calc(100vw - 48px));box-sizing:border-box;padding:20px;'
            + 'background:#123b34;color:white;border-radius:8px;font:20px/1.5 sans-serif;'
            + 'z-index:2147483647;box-shadow:0 4px 24px #0005;pointer-events:none';
        document.body.append(caption);
    }
    caption.textContent = text;
}"""

HIDE_CAPTION = "document.getElementById('tutorial-caption')?.remove()"

# Un cuadro de color pleno que `tutorial-videos` busca en la toma para cortar en el cuadro exacto.
SHOW_MARK = """() => {
    const mark = document.createElement('div');
    mark.id = 'tutorial-mark';
    mark.style.cssText = 'position:fixed;inset:0;background:#ff00ff;z-index:2147483647';
    document.body.append(mark);
}"""

HIDE_MARK = "document.getElementById('tutorial-mark')?.remove()"
