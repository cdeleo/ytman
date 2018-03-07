package com.cdeleo.ytman.thumbnails.api;

import com.cdeleo.ytman.thumbnails.ThumbnailGenerator;
import com.google.api.server.spi.config.Api;
import com.google.api.server.spi.config.ApiMethod;
import com.google.api.server.spi.config.ApiNamespace;
import com.google.api.server.spi.config.Named;
import java.awt.image.BufferedImage;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import javax.imageio.ImageIO;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.Rectangle;

@Api(
    name = "thumbnails",
    version = "v1",
    namespace = @ApiNamespace(
        ownerDomain = "com.cdeleo",
        ownerName = "com.cdeleo",
        packagePath = "ytman/thumbnails/api"
    )
)
public class ThumbnailsV1 {

  private final ThumbnailGenerator generator;

  public ThumbnailsV1() {
    generator = new ThumbnailGenerator();
  }

  @ApiMethod(name = "get", path = "get")
  public GetResponse get(
      @Named("title") String title, @Named("subtitle") String subtitle)
      throws Exception {
    // Validation
    if (title == null) {
      throw new IllegalArgumentException("title is required.");
    }
    if (subtitle == null) {
      throw new IllegalArgumentException("subtitle is required.");
    }

    // Thumbnail generation
    ByteArrayOutputStream out = new ByteArrayOutputStream();
    writeThumbnail(title, subtitle, out);

    // Response generation
    GetResponse response = new GetResponse();
    response.setImageData(out.toByteArray());
    return response;
  }

  private void writeThumbnail(String title, String subtitle, OutputStream out)
      throws Exception {
    BufferedImage bgImage = new BufferedImage(
        1280, 720, BufferedImage.TYPE_3BYTE_BGR);
    Graphics2D c = bgImage.createGraphics();
    c.setPaint(Color.CYAN);
    c.fill(new Rectangle(0, 0, bgImage.getWidth(), bgImage.getHeight()));

    BufferedImage image = generator.generate(bgImage, title, subtitle);
    ImageIO.write(image, "png", out);
  }

  public static class GetResponse {

    private byte[] imageData;

    public byte[] getImageData() {
      return imageData;
    }

    public void setImageData(byte[] imageData) {
      this.imageData = imageData;
    }
  }
}
