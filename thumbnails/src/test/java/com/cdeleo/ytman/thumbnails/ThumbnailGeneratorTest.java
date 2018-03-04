package com.cdeleo.ytman.thumbnails;

import static com.google.common.truth.Truth.assertThat;

import java.awt.image.BufferedImage;
import org.junit.Before;
import org.junit.Test;
import org.junit.runner.RunWith;
import org.junit.runners.JUnit4;

@RunWith(JUnit4.class)
public class ThumbnailGeneratorTest extends ImageOutputTest {

  private ThumbnailGenerator generator;

  @Before
  public void setUp() {
    generator = new ThumbnailGenerator();
  }

  @Test
  public void testGenerate() throws Exception {
    BufferedImage image = generator.generate(
        loadTestImage("/cyan.png"), "Descending title", "Descending subtitle");
    assertImagesEqual(image, loadTestImage("/thumbnail_sample.png"));
  }
}
