package com.cdeleo.ytman.thumbnails.api;

import com.cdeleo.ytman.thumbnails.ThumbnailGenerator;
import com.google.appengine.api.appidentity.AppIdentityServiceFactory;
import com.google.appengine.api.images.Image;
import com.google.appengine.api.images.ImagesService;
import com.google.appengine.api.images.ImagesServiceFactory;
import com.google.appengine.api.users.User;
import com.google.api.server.spi.config.Api;
import com.google.api.server.spi.config.ApiMethod;
import com.google.api.server.spi.config.ApiNamespace;
import com.google.api.server.spi.config.Named;
import com.google.api.server.spi.response.UnauthorizedException;
import java.awt.image.BufferedImage;
import java.io.ByteArrayInputStream;
import java.io.ByteArrayOutputStream;
import java.io.OutputStream;
import java.util.logging.Level;
import java.util.logging.Logger;
import javax.imageio.ImageIO;

import java.awt.Color;
import java.awt.Graphics2D;
import java.awt.Rectangle;

@Api(
    name = "thumbnails",
    version = "v1",
    clientIds = {ThumbnailsV1.CONSOLE_CLIENT_ID, ThumbnailsV1.WEB_CLIENT_ID},
    namespace = @ApiNamespace(
        ownerDomain = "com.cdeleo",
        ownerName = "com.cdeleo",
        packagePath = "ytman/thumbnails/api"
    )
)
public class ThumbnailsV1 {

  static final String CONSOLE_CLIENT_ID =
      "955262123852-j4nv7slhidt5lcjve721nj9lo8otmfq5.apps.googleusercontent.com";
  static final String WEB_CLIENT_ID =
      "955262123852-c1gthms5mhs36q6njvg6kgqu4f1b09q7.apps.googleusercontent.com";

  private final ThumbnailGenerator generator;
  private final ImagesService imagesService;
  private final String defaultBucket;

  private final Logger logger = Logger.getLogger(ThumbnailsV1.class.getName());

  public ThumbnailsV1() {
    generator = new ThumbnailGenerator();
    imagesService = ImagesServiceFactory.getImagesService();
    defaultBucket = AppIdentityServiceFactory
        .getAppIdentityService().getDefaultGcsBucketName();
  }

  @ApiMethod(name = "get", path = "get")
  public GetResponse get(
      User user,
      @Named("bg_key") String bgKey,
      @Named("title") String title,
      @Named("subtitle") String subtitle) throws Exception {
    // Validation
    if (user == null) {
      throw new UnauthorizedException("Authorization required.");
    }
    if (bgKey == null) {
      throw new IllegalArgumentException("bgKey is required.");
    }
    if (title == null) {
      throw new IllegalArgumentException("title is required.");
    }
    if (subtitle == null) {
      throw new IllegalArgumentException("subtitle is required.");
    }

    // Thumbnail generation
    ByteArrayOutputStream out = new ByteArrayOutputStream();
    writeThumbnail(user, bgKey, title, subtitle, out);

    // Response generation
    GetResponse response = new GetResponse();
    response.setImage_data(out.toByteArray());
    return response;
  }

  private Image readBgImage(String userId, String key) {
    String path = String.format(
        "/gs/%s/images/%s/%s.png", defaultBucket, userId, key);
    return imagesService.applyTransform(
         ImagesServiceFactory.makeResize(1280, 720),
         ImagesServiceFactory.makeImageFromFilename(path));
  }

  private void writeThumbnail(
      User user, String bgKey, String title, String subtitle, OutputStream out)
      throws Exception {
    BufferedImage bgImage = ImageIO.read(
        new ByteArrayInputStream(
            readBgImage(user.getUserId(), bgKey).getImageData()));
    BufferedImage image = generator.generate(bgImage, title, subtitle);
    ImageIO.write(image, "png", out);
  }

  public static class GetResponse {

    private byte[] imageData;

    public byte[] getImage_data() {
      return imageData;
    }

    public void setImage_data(byte[] imageData) {
      this.imageData = imageData;
    }
  }
}
