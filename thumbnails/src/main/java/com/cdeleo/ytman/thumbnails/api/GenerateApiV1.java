package com.cdeleo.ytman.thumbnails.api;

import com.cdeleo.ytman.thumbnails.ThumbnailGenerator;
import java.awt.image.BufferedImage;
import java.io.IOException;
import javax.imageio.ImageIO;
import javax.servlet.annotation.WebServlet;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

@WebServlet(name = "GenerateApiV1", value = "/generate/v1")
public class GenerateApiV1 extends HttpServlet {

  @Override
  public void doGet(HttpServletRequest request, HttpServletResponse response)
      throws IOException {

    ThumbnailGenerator generator = new ThumbnailGenerator();
  }
}
