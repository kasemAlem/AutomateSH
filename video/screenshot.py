"""
Generate beautiful code screenshots using Playwright and Pygments.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter
import structlog

logger = structlog.get_logger(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
<style>
  body {{
    margin: 0;
    padding: 60px;
    background: transparent;
    display: flex;
    justify-content: center;
    align-items: center;
  }}
  .window {{
    background: #1e1e1e;
    border-radius: 16px;
    box-shadow: 0 30px 60px rgba(0,0,0,0.5);
    overflow: hidden;
    min-width: 800px;
    max-width: 1200px;
  }}
  .titlebar {{
    background: #2d2d2d;
    padding: 16px 20px;
    display: flex;
    align-items: center;
  }}
  .buttons {{
    display: flex;
    gap: 10px;
  }}
  .button {{
    width: 14px;
    height: 14px;
    border-radius: 50%;
  }}
  .close {{ background: #ff5f56; }}
  .minimize {{ background: #ffbd2e; }}
  .maximize {{ background: #27c93f; }}
  .content {{
    padding: 32px;
    font-family: 'SF Mono', 'JetBrains Mono', 'Fira Code', 'Menlo', 'Monaco', monospace;
    font-size: 32px;
    line-height: 1.6;
    color: #ffffff;
  }}
  pre {{ margin: 0; }}
  {pygments_css}
</style>
</head>
<body>
  <div class="window" id="capture-area">
    <div class="titlebar">
      <div class="buttons">
        <div class="button close"></div>
        <div class="button minimize"></div>
        <div class="button maximize"></div>
      </div>
    </div>
    <div class="content">
      {code_html}
    </div>
  </div>
</body>
</html>
"""

def generate_code_image(code: str, output_path: Path, language: str = "python") -> Path | None:
    """
    Generate a high-res screenshot of the code.
    """
    if not code.strip():
        logger.warning("Empty code provided, skipping screenshot")
        return None
        
    try:
        try:
            lexer = get_lexer_by_name(language, stripall=True)
        except Exception:
            lexer = guess_lexer(code)
            
        formatter = HtmlFormatter(style="monokai", cssclass="source")
        code_html = highlight(code, lexer, formatter)
        pygments_css = formatter.get_style_defs('.source')
        
        html = HTML_TEMPLATE.format(code_html=code_html, pygments_css=pygments_css)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(device_scale_factor=3)  # Retina quality
            page.set_content(html)
            
            element = page.locator("#capture-area")
            element.screenshot(path=str(output_path), omit_background=True)
            browser.close()
            
        logger.info("Code screenshot generated", path=str(output_path))
        return output_path
        
    except Exception as e:
        logger.error("Failed to generate code screenshot", error=str(e))
        return None
