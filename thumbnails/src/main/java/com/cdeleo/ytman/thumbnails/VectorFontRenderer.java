package com.cdeleo.ytman.thumbnails;

import com.kitfox.svg.Font;
import com.kitfox.svg.MissingGlyph;
import com.kitfox.svg.SVGDiagram;
import com.kitfox.svg.SVGUniverse;
import java.awt.Graphics2D;
import java.awt.Rectangle;
import java.net.URL;
import java.util.stream.Collectors;
import java.util.stream.Stream;

public class VectorFontRenderer {

  private final Font font;

  public VectorFontRenderer(URL fontPath, String fontName) {
    SVGUniverse universe = new SVGUniverse();
    universe.loadSVG(fontPath);
    font = universe.getFont(fontName);
    if (font == null) {
      throw new IllegalStateException(
          "SVG at " + fontPath + " did not contain font " + fontName);
    }
  }

  public Layout layout(String text, int ascent) {
    return new Layout(font, text, ascent);
  }

  public static class Layout {

    private final Font font;
    private final String text;
    private final double scale;

    private Layout(Font font, String text, int ascent) {
      this.font = font;
      this.text = text;
      scale = ((double) ascent) / ((double) font.getFontFace().getAscent());
    }

    public Rectangle measure() {
      int width = getGlyphs().mapToInt(glyph -> glyph.getHorizAdvX()).sum();
      int ascent = font.getFontFace().getAscent();
      int descent = font.getFontFace().getDescent();
      return new Rectangle(
          0,
          (int) (-1 * scale * ascent),
          (int) (scale * width),
          (int) (scale * (ascent - descent)));
    }

    public void draw(Graphics2D outerC) throws Exception {
      try (ContextFrame c = new ContextFrame(outerC)) {
        c.get().scale(scale, scale);
        getGlyphs().forEachOrdered(
            glyph -> {
              c.get().fill(glyph.getPath());
              c.get().translate(glyph.getHorizAdvX(), 0);
            });
      }
    }

    private Stream<MissingGlyph> getGlyphs() {
      return text
          .codePoints()
          .mapToObj(codePoint -> codePointToString(codePoint))
          .map(glyphString -> font.getGlyph(glyphString));
    }

    private static String codePointToString(int codePoint) {
      StringBuilder sb = new StringBuilder();
      return sb.appendCodePoint(codePoint).toString();
    }
  }
}
