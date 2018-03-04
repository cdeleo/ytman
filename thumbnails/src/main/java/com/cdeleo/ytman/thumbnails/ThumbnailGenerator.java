package com.cdeleo.ytman.thumbnails;

import com.google.auto.value.AutoValue;
import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.Rectangle;
import java.awt.RenderingHints;
import java.awt.image.BufferedImage;
import java.util.Optional;

public class ThumbnailGenerator {

  private static final int RUNOUT = 50;
  private static final int TEXT_PADDING = 30;

  private static final BoxSpec TITLE_BOX =
      BoxSpec.builder()
          .setX(22)
          .setY(480)
          .setWidth(1200)
          .setHeight(116)
          .setAngle(-2.0)
          .setFgColor("000000")
          .setBgColor("c56000")
          .build();

  private static final BoxSpec SUBTITLE_BOX =
      BoxSpec.builder()
          .setX(148)
          .setY(570)
          .setHeight(100)
          .setAngle(2.5)
          .setFgColor("e3e3e3")
          .setBgColor("c58800")
          .build();

  private final VectorFontRenderer fontRenderer;

  public ThumbnailGenerator() {
    fontRenderer = new VectorFontRenderer(
        getClass().getResource("/ahronbd.svg"), "Aharoni");
  }

  public BufferedImage generate(
      BufferedImage bgImage, String title, String subtitle) throws Exception {
    BufferedImage image = cloneImage(bgImage);
    Graphics2D c = image.createGraphics();   
    c.setRenderingHint(
        RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
    c.setRenderingHint(
        RenderingHints.KEY_INTERPOLATION,
        RenderingHints.VALUE_INTERPOLATION_BICUBIC);
    drawBox(SUBTITLE_BOX, subtitle, c);
    drawBox(TITLE_BOX, title, c);
    c.dispose();
    return image; 
  }

  private BufferedImage cloneImage(BufferedImage image) {
    return new BufferedImage(
        image.getColorModel(),
        image.copyData(null),
        image.getColorModel().isAlphaPremultiplied(),
        null);
  }

  private void drawBox(
      BoxSpec spec, String text, Graphics2D outerC) throws Exception {
    try (ContextFrame c = new ContextFrame(outerC)) {
      c.get().translate(spec.x(), spec.y());
      c.get().rotate(spec.angle() * Math.PI / 180.0);

      // Text layout
      int textAscent = spec.height() - 2 * TEXT_PADDING;
      VectorFontRenderer.Layout textLayout = fontRenderer.layout(
          text, textAscent);
      Rectangle textBounds = textLayout.measure();

      // Background
      c.get().setPaint(spec.bgColor());
      int width = spec.width().orElse(
          textBounds.width + 2 * TEXT_PADDING + RUNOUT);
      c.get().fill(new Rectangle(0, 0, width, spec.height()));

      // Foreground
      c.get().translate(TEXT_PADDING, TEXT_PADDING + textAscent);
      c.get().setPaint(spec.fgColor());
      textLayout.draw(c.get());
    }
  }

  @AutoValue
  abstract static class BoxSpec {
    public abstract int x();
    public abstract int y();
    public abstract Optional<Integer> width();
    public abstract int height();
    public abstract double angle();
    public abstract Color fgColor();
    public abstract Color bgColor();

    public static Builder builder() {
      return new AutoValue_ThumbnailGenerator_BoxSpec.Builder();
    }

    @AutoValue.Builder
    public abstract static class Builder {
      public abstract Builder setX(int x);
      public abstract Builder setY(int y);
      public abstract Builder setWidth(int width);
      public abstract Builder setWidth(Optional<Integer> width);
      public abstract Builder setHeight(int height);
      public abstract Builder setAngle(double angle);
      public abstract Builder setFgColor(Color fgColor);
      public abstract Builder setBgColor(Color bgColor);
      public Builder setFgColor(String fgColorString) {
        return setFgColor(parseColorString(fgColorString));
      }
      public Builder setBgColor(String bgColorString) {
        return setBgColor(parseColorString(bgColorString));
      }      

      public abstract BoxSpec build();

      private static Color parseColorString(String colorString) {
        return new Color(
            Integer.parseInt(colorString.substring(0, 2), 16),
            Integer.parseInt(colorString.substring(2, 4), 16),
            Integer.parseInt(colorString.substring(4, 6), 16));
      }
    }
  }
}
