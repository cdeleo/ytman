package com.cdeleo.ytman.thumbnails;

import static com.google.common.truth.Truth.assertThat;

import java.awt.BasicStroke;
import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.Rectangle;
import java.awt.image.BufferedImage;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

@RunWith(JUnit4.class)
public class VectorFontRendererTest extends ImageOutputTest {

  private VectorFontRenderer renderer;

  @Before
  public void setUp() {
    renderer = new VectorFontRenderer(
        getClass().getResource("/ahronbd.svg"), "Aharoni");
  }

  @Test
  public void testMeasure() throws Exception {
    Rectangle expected = new Rectangle(0, -1505, 2772, 2048);
    assertThat(renderer.layout("Hg", 1505).measure()).isEqualTo(expected);
  }

  @Test
  public void testDraw() throws Exception {
    VectorFontRenderer.Layout layout = renderer.layout("Hg", 1000);
    Rectangle bounds = layout.measure();

    BufferedImage image = new BufferedImage(
        2000, 2000, BufferedImage.TYPE_3BYTE_BGR);    
    Graphics2D c = image.createGraphics();
    c.setPaint(Color.WHITE);
    c.fill(new Rectangle(0, 0, image.getWidth(), image.getHeight()));
    
    c.setPaint(Color.BLACK);
    c.translate(0, -1 * bounds.y);
    layout.draw(c);

    c.setStroke(new BasicStroke(10f));
    c.setPaint(Color.BLUE);
    c.draw(new Rectangle(bounds.x, 0, bounds.width, bounds.height + bounds.y));
    c.setPaint(Color.RED);
    c.draw(new Rectangle(bounds.x, bounds.y, bounds.width, -1 * bounds.y));

    c.dispose();
    assertImagesEqual(image, loadTestImage("/text_sample.png"));
  }
}
