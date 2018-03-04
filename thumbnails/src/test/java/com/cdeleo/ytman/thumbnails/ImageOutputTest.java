package com.cdeleo.ytman.thumbnails;

import static com.google.common.truth.Truth.assertThat;

import java.awt.Color;
import java.awt.image.BufferedImage;
import java.io.File;
import javax.imageio.ImageIO;
import org.junit.Rule;
import org.junit.rules.TestName;

public abstract class ImageOutputTest {

  @Rule public TestName testName = new TestName();

  protected BufferedImage loadTestImage(String path) throws Exception {
    return ImageIO.read(getClass().getResourceAsStream(path));
  }

  protected void assertImagesEqual(
      BufferedImage actual, BufferedImage expected) throws Exception {
    ImageIO.write(actual, "png", getImageFile("actual"));
    assertThat(actual.getWidth()).isEqualTo(expected.getWidth());
    assertThat(actual.getHeight()).isEqualTo(expected.getHeight());

    int nDiff = 0;
    for (int i = 0; i < actual.getWidth(); i++) {
      for (int j = 0; j < actual.getHeight(); j++) {
        if (actual.getRGB(i, j) != expected.getRGB(i, j)) {
          expected.setRGB(i, j, Color.MAGENTA.getRGB());
          nDiff++;
        }
      }
    }
    if (nDiff > 0) {
      ImageIO.write(expected, "png", getImageFile("highlight"));
    }
    assertThat(nDiff).isEqualTo(0);
  }

  private File getImageFile(String type) {
    return new File(
        String.format(
            "%s_%s_%s.png",
            getClass().getSimpleName(),
            testName.getMethodName(),
            type));
  }
}
